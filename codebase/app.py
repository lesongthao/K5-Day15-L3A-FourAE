"""Giao diện Web UI thuần Python & CLI dự phòng cho bản chạy thử Track C1.

Chạy mặc định: python run.py (mở Web UI tại http://127.0.0.1:8765)
Chạy dòng lệnh: python codebase/app.py --cli
Không cần cài thư viện ngoài; giữ nguyên hợp đồng answer(text) -> {"output": str}.
"""
from __future__ import annotations

import json
import os
import re
import sys
import threading
import time
import traceback
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any

for _stream in (sys.stdout, sys.stderr, sys.stdin):
    try:
        _stream.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError, OSError):
        pass

CODEBASE_DIR = Path(__file__).resolve().parent
if str(CODEBASE_DIR) not in sys.path:
    sys.path.insert(0, str(CODEBASE_DIR))

UI_FILE = CODEBASE_DIR / "web_ui.html"
ASSETS_DIR = CODEBASE_DIR / "assets"
_ASSET_MIMES = {".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".png": "image/png", ".webp": "image/webp"}
MAX_BODY_BYTES = 16 * 1024
MAX_TEXT_LEN = 2000
_TRACE_LOCK = threading.Lock()

_ITEM_RE = re.compile(
    r"^•\s*(\d{2}:\d{2})[–-](\d{2}:\d{2})\s*\|\s*\[([A-Z0-9]+)\]\s*"
    r"(.+?)\s*\(([A-Z0-9_]+),\s*([^)]+)\)\s*[—-]\s*(.*)$"
)
_COST_RE = re.compile(
    r"vé\s+([A-Z0-9_]+)\):\s*([\d,.]+)đ\s*\(Vé cổng:\s*([\d,.]+)đ\s*·\s*Dịch vụ lẻ:\s*([\d,.]+)đ\)"
)


class _StrictThreadingHTTPServer(ThreadingHTTPServer):
    """HTTP server không chiếm đè cổng đang có tiến trình khác lắng nghe trên Windows."""

    allow_reuse_address = False


def _where(err: BaseException) -> str:
    """Tìm file trong codebase/ gây lỗi khi nạp module."""
    path = getattr(err, "filename", None) or (traceback.extract_tb(err.__traceback__)[-1].filename if err.__traceback__ else "")
    if not path:
        return "codebase/"
    abs_path = os.path.abspath(path)
    base = str(CODEBASE_DIR.parent)
    return os.path.relpath(abs_path, base).replace(os.sep, "/") if abs_path.startswith(base) else abs_path


def _parse_int_vnd(raw: str) -> int:
    """Chuyển chuỗi tiền tệ có dấu phẩy/chấm thành số nguyên VNĐ."""
    digits = re.sub(r"[^\d]", "", raw)
    return int(digits) if digits else 0


def _parse_output_for_ui(output_text: str) -> dict[str, Any]:
    """Tách chuỗi kết quả từ agent.answer() thành dữ liệu có cấu trúc cho Web UI."""
    lines = [ln.strip() for ln in output_text.splitlines() if ln.strip()]
    first = lines[0] if lines else ""
    is_mock = first.startswith("[CHẾ ĐỘ KHUNG")

    if first.startswith("LỊCH TRÌNH ĐỀ XUẤT") or is_mock:
        kind = "schedule"
    elif "Không thể đáp ứng" in output_text:
        kind = "blocked"
    elif first.startswith("Để xếp lịch chính xác"):
        kind = "ask_more"
    elif first.startswith(("Không thể xếp lịch", "Không xếp được", "Trong dữ liệu hiện tại")):
        kind = "impossible"
    else:
        kind = "other"

    weather, items, notes, cost, disclaimer = "", [], [], None, ""
    for line in lines:
        if line.startswith("- Kịch bản thời tiết"):
            weather = line.split(":", 1)[-1].strip()
        elif m := _ITEM_RE.match(line):
            items.append({
                "start": m.group(1), "end": m.group(2), "id": m.group(3),
                "name": m.group(4).strip(), "zone": m.group(5).strip(),
                "env": m.group(6).strip(), "reason": m.group(7).strip(),
            })
        elif line.startswith("- Ghi chú thêm:"):
            notes = [n.strip() for n in line.split(":", 1)[-1].strip().split(" | ") if n.strip()]
        elif line.startswith("- Tổng chi phí"):
            mc = _COST_RE.search(line)
            cost = {
                "ticket_type": mc.group(1) if mc else "",
                "total_vnd": _parse_int_vnd(mc.group(2)) if mc else 0,
                "gate_vnd": _parse_int_vnd(mc.group(3)) if mc else 0,
                "extra_vnd": _parse_int_vnd(mc.group(4)) if mc else 0,
                "raw": line.lstrip("- ").strip(),
            }
        elif line.startswith("- Lưu ý:"):
            disclaimer = line.split(":", 1)[-1].strip()

    return {
        "kind": kind, "is_mock": is_mock, "headline": first, "weather": weather,
        "items": items, "notes": notes, "cost": cost, "disclaimer": disclaimer,
    }


def execute_plan(text: str) -> dict[str, Any]:
    """Chạy agent.answer(text) có ghi trace an toàn luồng và trả dữ liệu cho UI."""
    import tracing
    from agent import answer

    with _TRACE_LOCK:
        t0 = time.perf_counter()
        tracing.begin("web_app")
        try:
            result = answer(text)
        except Exception:
            tracing.end()
            raise
        summary, events = tracing.end()
        elapsed_s = round(time.perf_counter() - t0, 3)

    output = result.get("output", "") if isinstance(result, dict) else str(result)
    compact_events = [
        {"kind": ev.get("kind", ""), "name": ev.get("name", ""), "t": ev.get("t", 0.0), "latency_s": ev.get("latency_s"), "text": ev.get("text", "")}
        for ev in events
    ]
    return {"output": output, "parsed": _parse_output_for_ui(output), "trace": {**summary, "elapsed_s": elapsed_s, "events": compact_events}}


class PlanRequestHandler(BaseHTTPRequestHandler):
    """Bộ xử lý HTTP phục vụ trang Web UI, ảnh tĩnh /assets/* và API lập lịch."""

    def _send_bytes(self, status: int, content_type: str, data: bytes, cache: str = "no-store") -> None:
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", cache)
        self.end_headers()
        self.wfile.write(data)

    def _send_json(self, status: int, payload: dict[str, Any]) -> None:
        self._send_bytes(status, "application/json; charset=utf-8", json.dumps(payload, ensure_ascii=False).encode("utf-8"))

    def do_GET(self) -> None:
        """Phục vụ trang HTML, ảnh tĩnh /assets/* và endpoint kiểm tra sức khỏe."""
        path = self.path.split("?", 1)[0]
        if path in ("/", "/index.html"):
            try:
                self._send_bytes(200, "text/html; charset=utf-8", UI_FILE.read_bytes())
            except FileNotFoundError:
                self._send_json(500, {"error": "Không tìm thấy tệp giao diện codebase/web_ui.html."})
            return
        if path.startswith("/assets/"):
            name = path[len("/assets/"):]
            if not name or "/" in name or "\\" in name or ".." in name:
                self._send_json(404, {"error": "Đường dẫn ảnh không hợp lệ."})
                return
            target = (ASSETS_DIR / name).resolve()
            mime = _ASSET_MIMES.get(target.suffix.lower())
            if not mime or target.parent != ASSETS_DIR.resolve() or not target.is_file():
                self._send_json(404, {"error": "Không tìm thấy tệp ảnh."})
                return
            self._send_bytes(200, mime, target.read_bytes(), cache="public, max-age=3600")
            return
        if path == "/api/health":
            self._send_json(200, {"ok": True, "app": "FourAE Track C1", "park": "VinWonders Nha Trang"})
            return
        self._send_json(404, {"error": "Không tìm thấy đường dẫn yêu cầu."})

    def do_POST(self) -> None:
        """Nhận yêu cầu gia đình qua POST /api/plan và trả lịch trình + trace."""
        if self.path.split("?", 1)[0] != "/api/plan":
            self._send_json(404, {"error": "Không tìm thấy API endpoint."})
            return
        try:
            length = int(self.headers.get("Content-Length", "0"))
        except ValueError:
            self._send_json(400, {"error": "Header Content-Length không hợp lệ."})
            return
        if length <= 0 or length > MAX_BODY_BYTES:
            self._send_json(400, {"error": "Kích thước dữ liệu gửi lên không hợp lệ (tối đa 16KB)."})
            return
        try:
            payload = json.loads(self.rfile.read(length).decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError):
            self._send_json(400, {"error": "Nội dung JSON gửi lên không đúng định dạng UTF-8."})
            return

        text = str(payload.get("text", "")).strip() if isinstance(payload, dict) else ""
        if not text:
            self._send_json(400, {"error": "Vui lòng nhập thông tin gia đình và nhu cầu đi chơi."})
            return
        if len(text) > MAX_TEXT_LEN:
            self._send_json(400, {"error": f"Yêu cầu quá dài (tối đa {MAX_TEXT_LEN} ký tự)."})
            return
        try:
            self._send_json(200, execute_plan(text))
        except NotImplementedError as exc:
            self._send_json(503, {"error": f"Chưa cấu hình model thật: {exc}. Kiểm tra tệp .env theo docs/connect-model.md."})
        except (ValueError, RuntimeError, OSError) as exc:
            msg = str(exc)
            if "HTTP 530" in msg or "1016" in msg:
                self._send_json(502, {
                    "error": (
                        "Máy chủ proxy AI trong .env đang không phản hồi (Cloudflare HTTP 530 / lỗi DNS 1016). "
                        "Kiểm tra lại BASE_URL proxy của nhóm, đổi provider trong .env theo docs/connect-model.md, "
                        "hoặc đặt tạm MODEL_PROVIDER=fake để chạy thử giao diện."
                    )
                })
                return
            self._send_json(500, {"error": f"Lỗi khi gọi hệ thống ({type(exc).__name__}): {exc}"})

    def log_message(self, format: str, *args: Any) -> None:
        """Ẩn log HTTP mặc định để terminal gọn gàng; bật khi đặt FOURAE_HTTP_LOG=1."""
        if os.environ.get("FOURAE_HTTP_LOG") == "1":
            super().log_message(format, *args)


def create_server(host: str = "127.0.0.1", port: int = 8765) -> ThreadingHTTPServer:
    """Khởi tạo máy chủ Web UI cục bộ; tự chuyển cổng rảnh nếu cổng mặc định bận."""
    try:
        return _StrictThreadingHTTPServer((host, port), PlanRequestHandler)
    except OSError:
        if port != 0:
            return _StrictThreadingHTTPServer((host, 0), PlanRequestHandler)
        raise


def run_cli() -> int:
    """Chế độ dòng lệnh tối thiểu dự phòng (--cli)."""
    try:
        import tracing
        from agent import answer
    except (ImportError, SyntaxError, OSError, RuntimeError) as exc:
        print("Không nạp được codebase/ — lỗi ở %s: %s: %s" % (_where(exc), type(exc).__name__, exc))
        return 1
    print("Bản chạy thử (CLI) — gõ đầu vào rồi Enter. Thoát: Ctrl+C (hoặc Enter 2 lần với dòng trống).")
    blank = 0
    while True:
        try:
            text = input("> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            return 0
        if not text:
            blank += 1
            if blank >= 2:
                return 0
            continue
        blank = 0
        tracing.begin("app")
        try:
            result = answer(text)
        except NotImplementedError as exc:
            tracing.end()
            print("Chưa nối model: %s" % exc)
            return 1
        except (ValueError, RuntimeError, OSError) as exc:
            tracing.end()
            print("[lỗi] %s: %s" % (type(exc).__name__, exc))
            continue
        summary, _ = tracing.end()
        print(result.get("output", "") if isinstance(result, dict) else result)
        print("   (model: %s · gọi model %d lần · công cụ %d lần · token vào %d / ra %d)"
              % (", ".join(summary["models"]) or "—", summary["model_calls"], summary["tool_calls"], summary["tokens_in"], summary["tokens_out"]))


def run_web(port: int = 8765, open_browser: bool = True) -> int:
    """Khởi chạy Web UI tại localhost và tự mở trình duyệt."""
    try:
        import agent  # noqa: F401
        import tracing  # noqa: F401
    except (ImportError, SyntaxError, OSError, RuntimeError) as exc:
        print("Không nạp được codebase/ — lỗi ở %s: %s: %s" % (_where(exc), type(exc).__name__, exc))
        return 1
    server = create_server("127.0.0.1", port)
    actual_port = int(server.server_address[1])
    url = f"http://127.0.0.1:{actual_port}"
    print(f"FourAE Web UI đang chạy tại: {url}")
    print("Nhấn Ctrl+C để dừng máy chủ. (Muốn chạy dòng lệnh thuần: python codebase/app.py --cli)")
    if open_browser and os.environ.get("FOURAE_NO_BROWSER") != "1":
        webbrowser.open(url)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nĐã dừng máy chủ Web UI.")
    finally:
        server.server_close()
    return 0


def main(argv: list[str] | None = None) -> int:
    """Điểm vào chính hỗ trợ Web UI mặc định và cờ --cli / --port / --no-browser."""
    args = sys.argv[1:] if argv is None else argv
    if "--cli" in args:
        return run_cli()
    port = 8765
    if "--port" in args:
        idx = args.index("--port")
        if idx + 1 >= len(args):
            print("Thiếu số cổng sau --port.")
            return 2
        try:
            port = int(args[idx + 1])
        except ValueError:
            print("Số cổng --port phải là số nguyên.")
            return 2
    return run_web(port=port, open_browser="--no-browser" not in args)


if __name__ == "__main__":
    sys.exit(main())
