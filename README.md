# Krishna Patil — Live Data-Driven Portfolio & API

A high-performance developer portfolio and API for **Krishna Chandrakant Patil** ([@kriss2012](https://github.com/kriss2012)). Built with **React 19, TypeScript, Vite, and a production-grade FastAPI backend**, optimized specifically for **Render Free Tier**.

The backend synchronizes live GitHub statistics (74,900+ contributions, 99+ repositories, commits, and activity) with in-memory TTL caching, rate-limit shielding, stale-while-revalidate fallbacks, and a low-token AI Twin chatbot.

---

## Architecture Overview

```
Client Browser (Vercel / Netlify / Render)
      │
      ▼  (HTTP / JSON - /api/...)
FastAPI Backend Service (Render Free Tier)
      │
      ├── /health & /keepalive (< 5ms response, 0 external calls)
      ├── Security Middleware (100KB body limit, security headers, CORS)
      ├── Chat Rate Limiter (20 req/min per IP)
      │
      ├── In-Memory TTL Cache Layer
      │     ├── Profile: 6 hours
      │     ├── Repositories: 1 hour
      │     ├── Contributions: 2 hours
      │     ├── Activity & Commits: 10 minutes
      │
      ├── Stale-While-Revalidate Engine (zero downtime on GitHub rate limits)
      ├── GitHub REST & GraphQL API Client (timeout: 8s, 0 token leaks)
      └── AI Twin Token Economy (zero-token deterministic fast-path + 1-call Groq/Gemini)
```

---

## Deployment Target: Render Free Tier

The backend is engineered specifically to operate within Render Free Tier limits (512 MB RAM, ephemeral storage, automatic sleep on inactivity):
- **Ultra-low memory footprint**: ~25 MB RAM.
- **Sub-second cold start**: Boots in ~300ms. No database, no heavy ML models in memory.
- **Fast health check**: `GET /health` and `GET /keepalive` respond in <10ms without external requests.
- **Render dynamic PORT**: Automatically binds to `0.0.0.0:$PORT`.
- **Zero background thread loops**: Data is only fetched on request if cache is expired.

---

## Render Deployment Guide (Step-by-Step)

### Step 1: Push Repository to GitHub
Ensure all code and `render.yaml` are pushed to your GitHub repository:
```bash
git add .
git commit -m "Configure Render Free Tier deployment"
git push origin main
```

### Step 2: Open Render Dashboard
Go to [dashboard.render.com](https://dashboard.render.com) and log in.

### Step 3: Create Blueprint or Web Service
- **Option A (Blueprint — Recommended)**:
  1. Click **New +** → **Blueprint**.
  2. Connect your GitHub repository `kriss2012/portfolio`.
  3. Render will detect `render.yaml` and configure the service automatically.
- **Option B (Manual Web Service)**:
  1. Click **New +** → **Web Service**.
  2. Connect your repository.
  3. Configure settings:
     - **Name**: `krishna-portfolio-api`
     - **Runtime**: `Python 3`
     - **Build Command**: `pip install -r backend/requirements.txt`
     - **Start Command**: `python -m uvicorn backend.main:app --host 0.0.0.0 --port $PORT`
     - **Health Check Path**: `/health`
     - **Plan**: `Free`

### Step 4: Configure Environment Variables in Render
In your Render Service Dashboard → **Environment**, add:
| Key | Value | Description |
|---|---|---|
| `PYTHON_VERSION` | `3.11.9` | Python runtime version |
| `ENVIRONMENT` | `production` | Production mode |
| `GITHUB_USERNAME` | `kriss2012` | GitHub account username |
| `GITHUB_TOKEN` | *your_token* | Read-only GitHub PAT (increases rate limit from 60 to 5,000 req/hr) |
| `GROQ_API_KEY` | *your_groq_key* | Free-tier Groq key for AI Twin (optional) |
| `GEMINI_API_KEY` | *your_gemini_key* | Google Gemini key for AI Twin (optional) |
| `CORS_ORIGIN` | `*` or your frontend URL | Allowed frontend origins |

> **Security Note**: Never commit `GITHUB_TOKEN` or `GROQ_API_KEY` to git. Only configure them in Render environment settings.

### Step 5: Deploy
Click **Create Web Service** / **Apply**. Render will install dependencies and start the server.

### Step 6: Verify Deployment
Once live, your service will have a URL like `https://krishna-portfolio-api.onrender.com`.
Verify via browser or curl:
- `https://your-service.onrender.com/health` → `{"status": "ok", "service": "krishna-portfolio-api", ...}`
- `https://your-service.onrender.com/api/status` → `{"status": "ok", "github": "available", ...}`

### Step 7: Configure External Keep-Alive (Prevent Cold Spins)
Render Free web services spin down after 15 minutes of inactivity. To keep your backend warm and responsive:
1. Go to a free monitoring service like [cron-job.org](https://cron-job.org) or [UptimeRobot](https://uptimerobot.com).
2. Set up an HTTP `GET` request every **5 minutes** to:
   ```
   https://your-service.onrender.com/keepalive
   ```
3. **Safety Guarantee**: `/keepalive` executes in ~3ms. It does **NOT** call GitHub, does **NOT** call AI, and does **NOT** trigger cache refreshes, consuming zero rate limits or tokens.

---

## API Endpoints Reference

| Method | Endpoint | Purpose | External Calls |
|---|---|---|---|
| `GET` | `/health` | Render health check (<10ms) | None |
| `GET` | `/keepalive` | 5-min uptime monitor ping | None |
| `GET` | `/ready` | Readiness probe | None |
| `GET` | `/api/status` | Diagnostics & uptime (no secrets) | None |
| `GET` | `/api/github/profile` | Normalized profile with followers/repos | GitHub (cached 6h) |
| `GET` | `/api/github/repositories` | Normalized repository catalog | GitHub (cached 1h) |
| `GET` | `/api/github/activity` | Recent events feed | GitHub (cached 10m) |
| `GET` | `/api/github/contributions?year=2026` | Real 53-week heatmap & annual totals | GitHub GraphQL (cached 2h) |
| `GET` | `/api/github/commits` | Recent public commits timeline | GitHub (cached 10m) |
| `GET` | `/api/github/overview` | Master payload for frontend hooks | GitHub (cached) |
| `GET` | `/api/github/readme?repo=...` | Sanitized README content for modal | GitHub (cached) |
| `POST` | `/api/github/refresh` | Clear cache and re-sync | GitHub |
| `POST` | `/api/chat` | AI Twin with rate limiting & token economy | Groq/Gemini/Fallback |

---

## Frontend Integration (`VITE_API_BASE_URL`)

The frontend uses a single centralized API base configuration in [src/config/api.ts](file:///c:/Users/IMRD/Documents/GitHub/portfolio/src/config/api.ts):
```ts
export const API_BASE_URL = (
  import.meta.env.VITE_API_BASE_URL ||
  import.meta.env.VITE_BACKEND_URL ||
  ''
).replace(/\/$/, '')
```

- **Local Development**: Leave empty. The Vite dev server proxies `/api` to `http://localhost:8000`.
- **Production (Separate Frontend, e.g. Vercel / Netlify)**:
  Set environment variable in Vercel/Netlify:
  ```
  VITE_API_BASE_URL=https://krishna-portfolio-api.onrender.com
  ```
- **Production (Unified Full-Stack on Render)**:
  If deployed together, the backend automatically serves the pre-built `dist/` directory at root `/` with SPA routing. No CORS configuration needed!

---

## AI Twin Token-Saving Strategy

To prevent exhausting free AI API quotas:
1. **Tier 0: Greetings & Intro**: Instant scripted replies for greetings (`hi`, `hello`, `who are you`) using 0 AI tokens.
2. **Tier 1: Deterministic Portfolio Q&A**: Direct structured matching in `portfolio_data.py` answers questions about Krishna's education, experience, achievements, skills, contact, and projects with 0 AI tokens and 0 hallucination.
3. **Tier 2: In-Memory Answer Cache**: Caches common questions for 30 minutes (max 100 entries).
4. **Tier 3: 1 Single AI Call Max**: When an AI call is required, only compact relevant context (<1500 chars) is sent. The model (`llama-3.1-8b-instant`) is capped at 800 tokens with an 8-second timeout.
5. **Rate Limiter**: Strict per-IP rate limiter allows max 20 messages per minute, returning HTTP 429 if abused.

---

## Local Development Setup

### 1. Backend Server
```bash
cd backend
pip install -r requirements.txt
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### 2. Frontend Development Server
In the root directory:
```bash
npm install
npm run dev
```
Open `http://localhost:5173`.

### 3. Run Production Build & Tests
```bash
npm run build      # Compiles React TypeScript bundle to dist/
npx vitest run     # Runs unit tests (36 tests)
python scratch/test_all_endpoints.py # Verifies all API endpoints
```

---

## Post-Deployment Testing Checklist

Run these quick checks against your deployed Render URL:
```bash
# 1. Health check (Expected: 200, <10ms)
curl https://your-service.onrender.com/health

# 2. Keepalive ping (Expected: 200, <10ms)
curl https://your-service.onrender.com/keepalive

# 3. Status check (Expected: 200, github: available)
curl https://your-service.onrender.com/api/status

# 4. Profile endpoint (Expected: 200, followers/repos from GitHub)
curl https://your-service.onrender.com/api/github/profile

# 5. Contributions endpoint (Expected: 200, 74900+ contributions)
curl "https://your-service.onrender.com/api/github/contributions?year=2026"

# 6. Chatbot endpoint (Expected: 200)
curl -X POST https://your-service.onrender.com/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What projects has Krishna built?"}'
```

---

## License
MIT License © 2026 Krishna Chandrakant Patil.
