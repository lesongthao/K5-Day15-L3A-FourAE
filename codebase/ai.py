"""Nối model — chỗ DUY NHẤT trong bản chạy thử gọi model AI.

Hỗ trợ chế độ giả (fake) và gọi API thật qua urllib (OpenAI, Gemini, Anthropic, Ollama)
để không phải cài thêm thư viện ngoài. Token luôn lấy từ trường usage của API.
"""
from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from typing import Any

from tracing import model_call

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SHOW_RAW = False


def load_env(path: str = os.path.join(ROOT, ".env")) -> None:
    """Đọc file .env (KEY=VALUE mỗi dòng) vào biến môi trường, không ghi đè biến đã có."""
    if not os.path.exists(path):
        return
    with open(path, encoding="utf-8-sig") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


load_env()
MODEL_PROVIDER = (os.environ.get("MODEL_PROVIDER") or "fake").strip().lower()
MODEL_NAME = (os.environ.get("MODEL_NAME") or "").strip()
API_KEY = (os.environ.get("API_KEY") or "").strip()
BASE_URL = (os.environ.get("BASE_URL") or "").strip()


def _post_json(url: str, headers: dict[str, str], body: dict[str, Any], timeout: int = 60) -> dict[str, Any]:
    """Gửi yêu cầu HTTP POST JSON bằng thư viện chuẩn urllib và trả về dict phản hồi."""
    req = urllib.request.Request(
        url,
        data=json.dumps(body).encode("utf-8"),
        method="POST",
        # User-Agent riêng: Cloudflare trước proxy chặn UA mặc định "Python-urllib" (HTTP 403, error code 1010)
        headers={"Content-Type": "application/json", "User-Agent": "hackathon-eval-client/1.0", **headers},
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            data = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as err:
        detail = err.read().decode("utf-8", "replace")[:300]
        raise RuntimeError(f"HTTP {err.code}: {detail}") from err
    if SHOW_RAW:
        print(json.dumps(data, ensure_ascii=False, indent=2)[:3000])
    return data


def _call_openai(system: str, user: str) -> dict[str, Any]:
    """Gọi OpenAI Chat Completions API (hoặc endpoint tương thích qua BASE_URL)."""
    url = BASE_URL or "https://api.openai.com/v1/chat/completions"
    if not url.rstrip("/").endswith("/chat/completions"):   # BASE_URL dạng ".../v1" → nối thêm đường dẫn
        url = url.rstrip("/") + "/chat/completions"
    messages = ([{"role": "system", "content": system}] if system else []) + [{"role": "user", "content": user}]
    data = _post_json(url, {"Authorization": "Bearer " + API_KEY}, {"model": MODEL_NAME, "messages": messages})
    usage = data.get("usage", {})
    return {
        "text": data["choices"][0]["message"]["content"],
        "tokens_in": int(usage.get("prompt_tokens", 0)),
        "tokens_out": int(usage.get("completion_tokens", 0)),
    }


def _call_gemini(system: str, user: str) -> dict[str, Any]:
    """Gọi Google Gemini REST API v1beta và cộng cả thoughtsTokenCount nếu có."""
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL_NAME}:generateContent?key={API_KEY}"
    body: dict[str, Any] = {"contents": [{"role": "user", "parts": [{"text": user}]}]}
    if system:
        body["systemInstruction"] = {"parts": [{"text": system}]}
    data = _post_json(url, {}, body)
    parts = data["candidates"][0]["content"].get("parts", [])
    text = "".join(p.get("text", "") for p in parts)
    usage = data.get("usageMetadata", {})
    tokens_out = int(usage.get("candidatesTokenCount", 0)) + int(usage.get("thoughtsTokenCount", 0))
    return {"text": text, "tokens_in": int(usage.get("promptTokenCount", 0)), "tokens_out": tokens_out}


def _call_claude(system: str, user: str) -> dict[str, Any]:
    """Gọi Anthropic Messages API."""
    url = BASE_URL or "https://api.anthropic.com/v1/messages"
    data = _post_json(
        url,
        {"x-api-key": API_KEY, "anthropic-version": "2023-06-01"},
        {"model": MODEL_NAME, "max_tokens": 1500, "system": system or "", "messages": [{"role": "user", "content": user}]},
    )
    text = "".join(b.get("text", "") for b in data.get("content", []) if b.get("type") == "text")
    usage = data.get("usage", {})
    return {"text": text, "tokens_in": int(usage.get("input_tokens", 0)), "tokens_out": int(usage.get("output_tokens", 0))}


def _call_ollama(system: str, user: str) -> dict[str, Any]:
    """Gọi model chạy cục bộ qua Ollama."""
    url = BASE_URL or "http://localhost:11434/api/chat"
    messages = ([{"role": "system", "content": system}] if system else []) + [{"role": "user", "content": user}]
    data = _post_json(url, {}, {"model": MODEL_NAME, "messages": messages, "stream": False}, timeout=300)
    return {
        "text": data["message"]["content"],
        "tokens_in": int(data.get("prompt_eval_count", 0)),
        "tokens_out": int(data.get("eval_count", 0)),
    }


@model_call
def call_model(system: str, user: str) -> dict[str, Any]:
    """Gọi model theo cấu hình trong .env và trả về dict chuẩn 4 khoá để tracing ghi nhận."""
    if MODEL_PROVIDER == "fake":
        last = (user.strip().splitlines() or [""])[-1]
        return {
            "text": "[câu trả lời giả — chưa nối model] " + last[:60],
            "model": "fake",
            "tokens_in": 0,
            "tokens_out": 0,
        }
    if not MODEL_NAME or (MODEL_PROVIDER != "ollama" and not API_KEY):
        raise RuntimeError("Thiếu MODEL_NAME hoặc API_KEY trong file .env — xem docs/connect-model.md")
    if MODEL_PROVIDER == "openai":
        res = _call_openai(system, user)
    elif MODEL_PROVIDER == "gemini":
        res = _call_gemini(system, user)
    elif MODEL_PROVIDER == "anthropic":
        res = _call_claude(system, user)
    elif MODEL_PROVIDER == "ollama":
        res = _call_ollama(system, user)
    else:
        raise NotImplementedError(f"Chưa hỗ trợ MODEL_PROVIDER={MODEL_PROVIDER!r} trong codebase/ai.py")
    return {"text": res["text"], "model": MODEL_NAME, "tokens_in": res["tokens_in"], "tokens_out": res["tokens_out"]}
