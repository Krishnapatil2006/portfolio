import os
import sys
import time
import json
from datetime import datetime, timezone, date as date_obj
from typing import Optional, Dict, Any, List
from collections import defaultdict
from dotenv import load_dotenv

# Ensure the backend directory is in the Python module search path
backend_dir = os.path.dirname(os.path.abspath(__file__))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

# Load environment variables (.env in backend or parent directory)
load_dotenv(dotenv_path=os.path.join(backend_dir, ".env"))
load_dotenv(dotenv_path=os.path.join(os.path.dirname(backend_dir), ".env"))
load_dotenv()

from fastapi import FastAPI, Request, Response, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from pydantic import BaseModel
import requests

import github_service
import portfolio_data

# Record start time for /api/status uptime tracking
_server_start_time = time.time()

# Normalize AI Keys from environment (Groq, Gemini, OpenAI)
groq_key = (
    os.getenv("GROQ_API_KEY") or
    os.getenv("Groq_Api_Key") or
    ""
).strip()

gemini_key = (
    os.getenv("GEMINI_API_KEY") or
    os.getenv("Gemini_Api_Key") or
    os.getenv("GOOGLE_API_KEY") or
    ""
).strip()

serp_key = (
    os.getenv("SERPAPI_API_KEY") or
    os.getenv("SERP_API_KEY") or
    os.getenv("Serp_Api_Key") or
    ""
).strip()

# Initialize FastAPI app
app = FastAPI(
    title="Krishna Patil Portfolio API",
    description="Backend API for portfolio analytics, live GitHub synchronization, and AI Twin chatbot.",
    version="1.0.0"
)

# ==============================================================================
# 1. SECURITY & PRODUCTION MIDDLEWARES
# ==============================================================================

# --- A. Request Size Limiter Middleware (Max 100 KB) ---
class RequestSizeLimitMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        content_length = request.headers.get("content-length")
        if content_length:
            try:
                if int(content_length) > 102400:  # 100 KB limit
                    return JSONResponse(
                        status_code=413,
                        content={"success": False, "message": "Request entity too large (max 100KB allowed)."}
                    )
            except ValueError:
                pass
        return await call_next(request)

# --- B. Security Headers Middleware ---
class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response: Response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "SAMEORIGIN"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        return response

# --- C. Production Request Logging Middleware (Safe: never logs secrets or bodies) ---
class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        t0 = time.time()
        response = await call_next(request)
        duration_ms = round((time.time() - t0) * 1000, 2)
        # Avoid console spam from external 5-minute keepalive monitors
        if request.url.path not in ["/health", "/keepalive"]:
            print(f"[{request.method}] {request.url.path} {response.status_code} - {duration_ms}ms")
        return response

app.add_middleware(RequestLoggingMiddleware)
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(RequestSizeLimitMiddleware)

# --- D. CORS Configuration ---
cors_origins_env = os.getenv("CORS_ORIGIN") or os.getenv("FRONTEND_URL") or "*"
if cors_origins_env == "*":
    allowed_origins = ["*"]
else:
    allowed_origins = [o.strip() for o in cors_origins_env.split(",") if o.strip()]
    # Always allow local development origins
    for dev_origin in ["http://localhost:5173", "http://127.0.0.1:5173", "http://localhost:3000", "http://127.0.0.1:3000"]:
        if dev_origin not in allowed_origins:
            allowed_origins.append(dev_origin)

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True if allowed_origins != ["*"] else False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- E. Centralized Safe Error Handler ---
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    # Log internally for server diagnostics
    print(f"[Unhandled Error on {request.method} {request.url.path}]: {exc}")
    is_dev = os.getenv("ENVIRONMENT", "production").lower() in ["development", "dev", "local"]
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "message": "Internal server error occurred." if not is_dev else str(exc)
        }
    )

# ==============================================================================
# 2. ULTRA-LIGHTWEIGHT HEALTH & KEEP-ALIVE ENDPOINTS (<10ms)
# ==============================================================================

@app.get("/health")
async def health_check():
    """
    Render Health Check Endpoint.
    MUST execute in <10ms. Does NOT call GitHub, AI, or database.
    """
    return {
        "status": "ok",
        "service": "krishna-portfolio-api",
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

@app.get("/keepalive")
async def keepalive_ping():
    """
    Keep-alive endpoint for external uptime services (e.g. cron-job.org every 5 min).
    Extremely cheap ping to prevent Render free-tier cold spins.
    Does NOT trigger data refreshes.
    """
    return {
        "status": "ok",
        "service": "krishna-portfolio-api",
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

@app.get("/ready")
async def readiness_probe():
    """Readiness probe confirming the server is ready to accept requests."""
    return {
        "ready": True,
        "service": "krishna-portfolio-api",
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

@app.get("/api/status")
async def api_status():
    """
    Health, uptime, and diagnostics without exposing secrets.
    """
    uptime_sec = round(time.time() - _server_start_time, 2)
    has_gh_token = bool(github_service.GITHUB_TOKEN)
    has_ai = bool(groq_key or gemini_key or os.getenv("OPENAI_API_KEY"))
    
    return {
        "status": "ok",
        "service": "krishna-portfolio-api",
        "github": "available" if has_gh_token else "cached/unauthenticated",
        "ai": "available" if has_ai else "unconfigured",
        "uptime": uptime_sec,
        "version": "1.0.0",
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

@app.get("/api/ping")
async def ping():
    """Alias ping endpoint."""
    return {"pong": True}

# ==============================================================================
# 3. GITHUB NORMALIZED API ENDPOINTS
# ==============================================================================

@app.get("/api/github/profile")
async def github_profile(username: Optional[str] = None):
    """Normalized live GitHub profile information."""
    target_user = username or github_service.GITHUB_USERNAME
    raw = github_service.get_profile(target_user)
    return {
        "success": True,
        "data": {
            "username": raw.get("login", target_user),
            "name": raw.get("name") or "Krishna Chandrakant Patil",
            "avatar": raw.get("avatar_url"),
            "bio": raw.get("bio"),
            "followers": raw.get("followers", 0),
            "following": raw.get("following", 0),
            "publicRepos": raw.get("public_repos", 0),
            "location": raw.get("location"),
            "website": raw.get("blog") or raw.get("html_url"),
        },
        "cached": raw.get("isCached", False),
        "lastUpdated": raw.get("lastUpdated", datetime.now(timezone.utc).isoformat())
    }

@app.get("/api/github/repositories")
async def github_repositories(username: Optional[str] = None):
    """Normalized list of public repositories with language, stars, forks, and tags."""
    target_user = username or github_service.GITHUB_USERNAME
    repos = github_service.get_repositories(target_user)
    return {
        "success": True,
        "count": len(repos),
        "data": repos,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

@app.get("/api/github/activity")
async def github_activity(username: Optional[str] = None, limit: int = 15):
    """Normalized recent GitHub events feed."""
    target_user = username or github_service.GITHUB_USERNAME
    events = github_service.get_activity(target_user, limit)
    return {
        "success": True,
        "count": len(events),
        "data": events,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

@app.get("/api/github/contributions")
async def github_contributions(username: Optional[str] = None, year: Optional[int] = None):
    """Live contribution calendar, active days, streak metrics, and annual totals."""
    target_user = username or github_service.GITHUB_USERNAME
    contribs = github_service.get_contributions(target_user, year)
    return {
        "success": True,
        **contribs
    }

@app.get("/api/github/commits")
async def github_commits(username: Optional[str] = None, limit: int = 30):
    """Timeline of recent commits across public repositories."""
    target_user = username or github_service.GITHUB_USERNAME
    commits = github_service.get_commits(target_user, limit)
    return {
        "success": True,
        "count": len(commits),
        "data": commits,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

@app.get("/api/github/overview")
async def github_overview(username: Optional[str] = None):
    """Master consolidated payload consumed by frontend overview hooks."""
    target_user = username or github_service.GITHUB_USERNAME
    return github_service.get_overview(target_user)

@app.get("/api/github/languages")
async def github_languages(username: Optional[str] = None):
    """Dynamic language breakdown derived from repository codebases."""
    target_user = username or github_service.GITHUB_USERNAME
    return github_service.get_languages(target_user)

@app.get("/api/github/stats")
async def github_stats(username: Optional[str] = None):
    """High-level GitHub summary statistics."""
    target_user = username or github_service.GITHUB_USERNAME
    overview = github_service.get_overview(target_user)
    return overview.get("statistics", {})

@app.get("/api/github/readme")
async def github_readme(repo: str, username: Optional[str] = None):
    """Sanitized repository README content for the project modal."""
    target_user = username or github_service.GITHUB_USERNAME
    return github_service.get_readme(repo, target_user)

@app.post("/api/github/refresh")
async def github_refresh():
    """Flushes in-memory cache and initiates a fresh data sync."""
    github_service.clear_cache()
    new_data = github_service.get_overview()
    return {
        "success": True,
        "status": "success",
        "message": "GitHub cache cleared and refreshed successfully.",
        "meta": new_data.get("meta")
    }

@app.get("/api/portfolio/data")
async def get_portfolio_payload():
    """Structured portfolio data combined with live GitHub metrics."""
    return portfolio_data.get_live_portfolio_data()

# ==============================================================================
# 4. AI TWIN CHATBOT WITH RATE LIMITING & TOKEN ECONOMY
# ==============================================================================

class ChatRequest(BaseModel):
    message: str
    session_id: str = "portfolio_visitor"

# --- A. Per-IP Rate Limiting (20 requests per minute per IP) ---
_chat_rate_limits: Dict[str, List[float]] = defaultdict(list)
CHAT_MAX_PER_MINUTE = int(os.getenv("CHAT_RATE_LIMIT_PER_MINUTE", "20"))

def _check_rate_limit(ip: str) -> bool:
    now = time.time()
    cutoff = now - 60.0
    history = [t for t in _chat_rate_limits[ip] if t > cutoff]
    if len(history) >= CHAT_MAX_PER_MINUTE:
        _chat_rate_limits[ip] = history
        return False
    history.append(now)
    _chat_rate_limits[ip] = history
    return True

# --- B. In-Memory AI Answer Cache (TTL 30 min, max 100 entries) ---
_ai_response_cache: Dict[str, Dict[str, Any]] = {}
AI_CACHE_TTL = 1800

def _get_cached_ai(key: str) -> Optional[str]:
    if key in _ai_response_cache:
        entry = _ai_response_cache[key]
        if time.time() - entry["ts"] < AI_CACHE_TTL:
            return entry["reply"]
        del _ai_response_cache[key]
    return None

def _set_cached_ai(key: str, reply: str):
    if len(_ai_response_cache) > 100:
        oldest = min(_ai_response_cache.keys(), key=lambda k: _ai_response_cache[k]["ts"])
        del _ai_response_cache[oldest]
    _ai_response_cache[key] = {"reply": reply, "ts": time.time()}

# --- C. System Persona Prompt for AI ---
QA_SYSTEM_PROMPT = """You are Krishna Chandrakant Patil's official AI Twin.
You speak directly as Krishna in the first person ("I built", "My projects", "I study").
Keep responses concise, friendly, engaging, and professional.
Use Markdown formatting (bullet points, bold text, links) for readability.
Highlight key accomplishments: Shark Tank Winner (1st Prize 2025, 2nd Prize 2024), Vice President of Coders Club, 99+ repositories, 74,900+ contributions.
If a question is off-topic, give a brief polite response and steer the conversation back to engineering and projects.
Never hallucinate projects or credentials not mentioned in the context.
"""

INSTANT_REPLIES = {
    "hi": "Hey! I'm Krishna's AI Twin. Ask me about my projects, technical skills, or schedule a meeting!",
    "hey": "Hey there! What would you like to know about my work or background?",
    "hello": "Hello! I'm Krishna Patil's AI Twin. What can I help you explore today?",
    "yo": "Yo! Ready to chat. Ask me about my AI/ML projects, full-stack builds, or achievements!",
    "hii": "Hey! I'm Krishna's AI Twin. Ask me about my projects, skills, or background!",
    "helo": "Hello! I'm Krishna Patil's AI Twin. Feel free to ask about my engineering work.",
    "sup": "Hey! Ready to chat. Ask me about my skills, projects, or when we can connect!",
    "whats up": "Hey! I'm actively coding and exploring new AI tech. What would you like to know about my work?",
    "what's up": "Hey! I'm actively coding and exploring new AI tech. What would you like to know about my work?",
    "ok": "Sure! What else would you like to know about my projects or background?",
    "okay": "Awesome! Feel free to ask about any specific project, tech stack, or get in touch.",
    "thanks": "Happy to help! Anything else you'd like to know?",
    "thank you": "You're very welcome! Feel free to ask about my projects, skills, or scheduling a call!",
    "thankyou": "You're welcome! Feel free to connect anytime on GitHub or LinkedIn.",
    "bye": "Thanks for visiting my portfolio! Feel free to reach out anytime on LinkedIn or email. Goodbye!",
    "goodbye": "Thanks for stopping by! Let's connect on LinkedIn. Have a great day!",
}

INTRO_TRIGGERS = [
    "introduce yourself", "introduction", "introduce", "tell me about yourself",
    "tell me about you", "who are you", "who r u", "who ru", "about you",
    "about yourself", "what are you", "who is krishna", "describe yourself",
]

INTRO_REPLY = (
    "Hey! I'm **Krishna Chandrakant Patil** — or rather, my interactive AI Twin 😄\n\n"
    "I'm a 3rd-year BCA student specialising in Computational Science at G.H. Raisoni Institute of Engineering, "
    "Jalgaon. I'm based in Pachora, Maharashtra, India.\n\n"
    "**Snapshot of what I do:**\n"
    "- 🤖 **AI & ML Engineer** — 12+ machine learning projects including computer vision, medical diagnosis, NLP, and fraud detection\n"
    "- 💻 **Full-Stack Developer** — Python (FastAPI, Flask, Django), React, TypeScript, Node.js, REST APIs\n"
    "- 🏆 **Shark Tank Winner** — 1st Prize 2025 & Runner-up 2024\n"
    "- 🎓 **Vice President** of the Coders Club at G.H. Raisoni\n"
    "- 🏸 **State-Level Badminton Player** & gamer\n"
    "- 📈 **99+ public repositories** and **74,900+ contributions** on GitHub!\n\n"
    "Feel free to ask me about any of my **projects**, **skills**, **education**, or **scheduling a meeting**!"
)

# --- D. Lightweight Direct LLM Caller (Requests-based, no heavy SDKs) ---
def _call_direct_llm(user_msg: str, context_text: str) -> Optional[str]:
    """Calls Groq or Gemini directly with an 8-second timeout, 1 call limit, max 800 tokens."""
    # 1. Try Groq (ultra-fast, free tier friendly)
    if groq_key and groq_key != "dummy_groq_key":
        try:
            payload = {
                "model": os.getenv("AI_MODEL", "llama-3.1-8b-instant"),
                "messages": [
                    {"role": "system", "content": QA_SYSTEM_PROMPT},
                    {"role": "user", "content": f"Context about Krishna Patil:\n{context_text[:1400]}\n\nUser Question: {user_msg}"}
                ],
                "temperature": 0.3,
                "max_tokens": 800
            }
            res = requests.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={"Authorization": f"Bearer {groq_key}", "Content-Type": "application/json"},
                json=payload,
                timeout=8
            )
            if res.status_code == 200:
                data = res.json()
                choices = data.get("choices", [])
                if choices and "message" in choices[0]:
                    return choices[0]["message"].get("content", "").strip()
        except Exception as e:
            print(f"[Direct Groq LLM Error] {e}")

    # 2. Try Google Gemini (if Groq not available)
    if gemini_key and gemini_key != "dummy_google_key":
        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={gemini_key}"
            payload = {
                "contents": [{
                    "parts": [{"text": f"{QA_SYSTEM_PROMPT}\n\nContext about Krishna:\n{context_text[:1400]}\n\nUser Question: {user_msg}"}]
                }],
                "generationConfig": {"temperature": 0.3, "maxOutputTokens": 800}
            }
            res = requests.post(url, headers={"Content-Type": "application/json"}, json=payload, timeout=8)
            if res.status_code == 200:
                data = res.json()
                candidates = data.get("candidates", [])
                if candidates:
                    parts = candidates[0].get("content", {}).get("parts", [])
                    if parts and "text" in parts[0]:
                        return parts[0]["text"].strip()
        except Exception as e:
            print(f"[Direct Gemini LLM Error] {e}")

    return None

@app.post("/api/chat")
async def chat_endpoint(req: ChatRequest, request: Request):
    """
    AI Twin conversational endpoint with strict rate limiting, 
    token economy, and zero-token deterministic fast-path.
    """
    # 1. Message Validation
    raw_msg = (req.message or "").strip()
    if not raw_msg:
        raise HTTPException(status_code=400, detail="Message cannot be empty.")
    if len(raw_msg) > 2000:
        raw_msg = raw_msg[:2000]

    # 2. Per-IP Rate Limiting
    client_ip = request.client.host if request.client else "unknown"
    if not _check_rate_limit(client_ip):
        return JSONResponse(
            status_code=429,
            content={
                "success": False,
                "reply": "Please wait a moment before sending another message. Rate limit reached."
            }
        )

    clean = raw_msg.lower().rstrip("!?.,")

    # Layer 0: Exact greetings (0 tokens)
    if clean in INSTANT_REPLIES:
        return {"success": True, "reply": INSTANT_REPLIES[clean]}

    for trigger in INTRO_TRIGGERS:
        if trigger in clean:
            return {"success": True, "reply": INTRO_REPLY}

    # Layer 1: Zero-hallucination deterministic portfolio answers (0 tokens)
    try:
        portfolio_answer = portfolio_data.answer_portfolio_question(raw_msg)
        if portfolio_answer:
            return {"success": True, "reply": portfolio_answer}
    except Exception as e:
        print(f"[Portfolio Question Handler Error] {e}")

    # Layer 2: Response Cache (0 tokens)
    cached_reply = _get_cached_ai(clean)
    if cached_reply:
        return {"success": True, "reply": cached_reply}

    # Layer 3: Direct LLM with targeted context (<1500 chars)
    try:
        # Build compact context from structured data
        p_data = portfolio_data.PORTFOLIO_DATA
        compact_context = (
            f"Name: Krishna Patil, BCA student graduating 2026. "
            f"Skills: {', '.join(p_data.get('skills', {}).get('programming_languages', [])[:6])}. "
            f"AI/ML: {', '.join(p_data.get('skills', {}).get('ai_and_ml', [])[:5])}. "
            f"Projects: TraffiX-AI, Plagiarism Checker, MediAI Pro, BashaConverter, Fake Reviews ID. "
            f"Awards: Shark Tank 1st Prize 2025, VP Coders Club. "
            f"GitHub: kriss2012 (99 repos, 74.9k contributions). "
            f"Contact: 202krishnapatil@gmail.com, +91 9850159631."
        )

        llm_reply = _call_direct_llm(raw_msg, compact_context)
        if llm_reply:
            _set_cached_ai(clean, llm_reply)
            return {"success": True, "reply": llm_reply}
    except Exception as llm_err:
        print(f"[LLM Inference Error] {llm_err}")

    # Layer 4: Graceful deterministic fallback (never crashes)
    return {
        "success": True,
        "reply": (
            "I'm Krishna Patil! I specialize in AI/ML and Full Stack development with 99+ repositories on GitHub. "
            "Feel free to ask me about my featured projects (like TraffiX-AI or MediAI Pro), technical skills, "
            "or how to schedule a meeting with me!"
        )
    }

# ==============================================================================
# 5. UNIFIED FRONTEND STATIC SERVING (Optional Full-Stack Render Deployment)
# ==============================================================================

frontend_dist = os.path.abspath(os.path.join(backend_dir, "..", "dist"))
if os.path.exists(frontend_dist) and os.path.exists(os.path.join(frontend_dist, "index.html")):
    from fastapi.staticfiles import StaticFiles
    from fastapi.responses import FileResponse

    assets_dir = os.path.join(frontend_dist, "assets")
    if os.path.exists(assets_dir):
        app.mount("/assets", StaticFiles(directory=assets_dir), name="assets")

    # SPA catch-all fallback for non-API routes
    @app.get("/{full_path:path}")
    async def serve_spa_frontend(full_path: str):
        # Do not catch API or system endpoints
        if full_path.startswith("api/") or full_path in ["health", "keepalive", "ready", "docs", "openapi.json"]:
            raise HTTPException(status_code=404, detail="Not found")
        file_path = os.path.join(frontend_dist, full_path)
        if os.path.isfile(file_path):
            return FileResponse(file_path)
        return FileResponse(os.path.join(frontend_dist, "index.html"))

# ==============================================================================
# 6. RENDER PRODUCTION STARTUP BINDING
# ==============================================================================

if __name__ == "__main__":
    import uvicorn
    # Respect Render's dynamically assigned PORT, default to 8000
    port = int(os.getenv("PORT", "8000"))
    host = os.getenv("HOST", "0.0.0.0")
    print(f"[Production Server] Listening on {host}:{port}...")
    uvicorn.run("main:app", host=host, port=port, log_level="info")
