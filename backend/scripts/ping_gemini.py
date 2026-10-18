from app.core.config import get_settings
import httpx

settings = get_settings()
if not settings.gemini_api_key:
    raise SystemExit("GEMINI_API_KEY not loaded")

response = httpx.post(
    f"https://generativelanguage.googleapis.com/v1beta/models/{settings.gemini_model}:generateContent",
    headers={"x-goog-api-key": settings.gemini_api_key, "Content-Type": "application/json"},
    json={
        "contents": [{"parts": [{"text": 'Return JSON {"ok": true} only.'}]}],
        "generationConfig": {
            "temperature": 0,
            "maxOutputTokens": 512,
            "responseMimeType": "application/json",
        },
    },
    timeout=20.0,
)
print("http", response.status_code)
if response.status_code >= 400:
    print(response.text[:800])
    raise SystemExit(1)
body = response.json()
print("model", settings.gemini_model)
print("keys", list(body.keys()))
cand = (body.get("candidates") or [{}])[0]
print("finish", cand.get("finishReason"))
print("usage", body.get("usageMetadata"))
parts = (cand.get("content") or {}).get("parts") or []
text = "".join(str(part.get("text") or "") for part in parts if not part.get("thought"))
print("reply", text[:300] if text else "<empty>")
