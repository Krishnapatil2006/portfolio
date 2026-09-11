import os
import time
import re
import html
import base64
import requests
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from dotenv import load_dotenv

# Load env variables from backend/.env or parent .env
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), ".env"))
load_dotenv()

GITHUB_USERNAME = os.getenv("GITHUB_USERNAME") or "kriss2012"
GITHUB_TOKEN = (
    os.getenv("GITHUB_TOKEN")
    or os.getenv("GITHUB_PAT")
    or os.getenv("github api")
    or ""
).strip()
GITHUB_API_BASE = os.getenv("GITHUB_API_BASE_URL", "https://api.github.com").rstrip("/")
GRAPHQL_ENDPOINT = f"{GITHUB_API_BASE}/graphql"

# Cache TTL defaults (in seconds)
TTL_PROFILE = int(os.getenv("GITHUB_PROFILE_CACHE_TTL", 6 * 3600))       # 6 hours
TTL_REPOS = int(os.getenv("GITHUB_REPOS_CACHE_TTL", 3600))              # 1 hour
TTL_ACTIVITY = int(os.getenv("GITHUB_ACTIVITY_CACHE_TTL", 600))         # 10 minutes
TTL_COMMITS = int(os.getenv("GITHUB_COMMITS_CACHE_TTL", 600))           # 10 minutes
TTL_CONTRIBUTIONS = int(os.getenv("GITHUB_CONTRIBUTIONS_CACHE_TTL", 7200)) # 2 hours
TTL_LANGUAGES = int(os.getenv("GITHUB_LANGUAGES_CACHE_TTL", 7200))       # 2 hours

# Language hex colors
LANGUAGE_COLORS: Dict[str, str] = {
    "Python": "#3572A5",
    "JavaScript": "#f1e05a",
    "TypeScript": "#3178c6",
    "HTML": "#e34c26",
    "CSS": "#563d7c",
    "C++": "#f34b7d",
    "C": "#555555",
    "Java": "#b07219",
    "Shell": "#89e051",
    "Jupyter Notebook": "#DA5B0B",
    "Dart": "#00B4AB",
    "Go": "#00ADD8",
    "Rust": "#dea584",
    "PHP": "#4F5D95",
    "Ruby": "#701516",
    "Swift": "#F05138",
    "Kotlin": "#A97BFF",
    "Dockerfile": "#384d54",
    "SCSS": "#c6538c",
}

# In-memory cache store: key -> { data, timestamp, is_stale_fallback }
_cache: Dict[str, Dict[str, Any]] = {}

def _get_headers() -> Dict[str, str]:
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": f"krishna-portfolio-backend/2.0 ({GITHUB_USERNAME})",
    }
    if GITHUB_TOKEN:
        headers["Authorization"] = f"Bearer {GITHUB_TOKEN}"
    return headers

def _is_cache_valid(key: str, ttl: int) -> bool:
    if key not in _cache:
        return False
    entry = _cache[key]
    return (time.time() - entry.get("timestamp", 0)) < ttl

def _set_cache(key: str, data: Any):
    _cache[key] = {
        "data": data,
        "timestamp": time.time(),
    }

def _get_cache(key: str) -> Optional[Any]:
    if key in _cache:
        return _cache[key].get("data")
    return None

def clear_cache():
    """Clear all cached GitHub responses."""
    _cache.clear()

def _calc_relative_time(iso_str: str) -> str:
    """Format an ISO timestamp to relative time (e.g., '2 hours ago')."""
    try:
        dt = datetime.fromisoformat(iso_str.replace("Z", "+00:00"))
        now = datetime.now(timezone.utc)
        diff = now - dt
        seconds = int(diff.total_seconds())
        if seconds < 60:
            return "just now"
        elif seconds < 3600:
            m = seconds // 60
            return f"{m}m ago"
        elif seconds < 86400:
            h = seconds // 3600
            return f"{h}h ago"
        elif seconds < 2592000:
            d = seconds // 86400
            return f"{d}d ago"
        elif seconds < 31536000:
            mo = seconds // 2592000
            return f"{mo}mo ago"
        else:
            y = seconds // 31536000
            return f"{y}y ago"
    except Exception:
        return iso_str[:10] if iso_str else ""

# -------------------------------------------------------------
# 1. Profile API
# -------------------------------------------------------------
def get_profile(username: str = GITHUB_USERNAME) -> Dict[str, Any]:
    cache_key = f"profile_{username}"
    if _is_cache_valid(cache_key, TTL_PROFILE):
        cached = _get_cache(cache_key)
        cached["isCached"] = True
        return cached

    url = f"{GITHUB_API_BASE}/users/{username}"
    try:
        resp = requests.get(url, headers=_get_headers(), timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            created_at = data.get("created_at", "")
            account_age_years = 0
            if created_at:
                try:
                    c_year = datetime.fromisoformat(created_at.replace("Z", "+00:00")).year
                    account_age_years = datetime.now().year - c_year
                except Exception:
                    pass

            result = {
                "name": data.get("name") or "Krishna Chandrakant Patil",
                "login": data.get("login") or username,
                "avatar_url": data.get("avatar_url") or f"https://github.com/{username}.png",
                "bio": data.get("bio") or "BCA Computational Science student | AI/ML & Full Stack Developer",
                "location": data.get("location") or "Pachora, Maharashtra, India",
                "company": data.get("company"),
                "blog": data.get("blog") or "https://tgkrish-portfolio.netlify.app/",
                "followers": data.get("followers", 0),
                "following": data.get("following", 0),
                "public_repos": data.get("public_repos", 0),
                "public_gists": data.get("public_gists", 0),
                "created_at": created_at,
                "account_age_years": account_age_years,
                "html_url": data.get("html_url") or f"https://github.com/{username}",
                "isCached": False,
                "lastUpdated": datetime.now(timezone.utc).isoformat(),
            }
            _set_cache(cache_key, result)
            return result
        else:
            print(f"[GitHub Profile] HTTP {resp.status_code}: {resp.text}")
    except Exception as e:
        print(f"[GitHub Profile Error] {e}")

    # Fallback to cached data if exists
    cached = _get_cache(cache_key)
    if cached:
        cached["isCached"] = True
        return cached

    # Safe fallback
    return {
        "name": "Krishna Chandrakant Patil",
        "login": username,
        "avatar_url": f"https://github.com/{username}.png",
        "bio": "BCA Computational Science student | AI/ML & Full Stack Developer",
        "location": "Pachora, Maharashtra, India",
        "company": None,
        "blog": "https://tgkrish-portfolio.netlify.app/",
        "followers": 9,
        "following": 9,
        "public_repos": 99,
        "public_gists": 0,
        "created_at": "2024-01-01T00:00:00Z",
        "account_age_years": 2,
        "html_url": f"https://github.com/{username}",
        "isCached": True,
        "lastUpdated": datetime.now(timezone.utc).isoformat(),
        "isFallback": True,
    }

# -------------------------------------------------------------
# 2. Repositories API
# -------------------------------------------------------------
def _infer_category(name: str, desc: str, topics: List[str], lang: str) -> str:
    text = f"{name} {desc} {' '.join(topics)} {lang}".lower()
    if any(k in text for k in ["traffic", "ai", "ml", "detection", "model", "nlp", "fraud", "medical", "consultancy", "tensorflow", "pytorch", "plagiarism", "vision", "dataset", "prediction", "assistant", "kirito"]):
        return "AI/ML"
    if any(k in text for k in ["react", "vite", "frontend", "portfolio", "ui", "web", "html", "css", "tailwind"]):
        return "Web Development"
    if any(k in text for k in ["django", "flask", "fastapi", "node", "express", "backend", "api", "mongo", "sql", "fullstack", "full-stack"]):
        return "Full Stack"
    if any(k in text for k in ["game", "rdr", "unity", "gaming", "play"]):
        return "Games & Tools"
    return "Software Engineering"

def get_repositories(username: str = GITHUB_USERNAME) -> List[Dict[str, Any]]:
    cache_key = f"repos_{username}"
    if _is_cache_valid(cache_key, TTL_REPOS):
        return _get_cache(cache_key)

    url = f"{GITHUB_API_BASE}/users/{username}/repos?per_page=100&sort=updated&type=owner"
    try:
        resp = requests.get(url, headers=_get_headers(), timeout=15)
        if resp.status_code == 200:
            repos_raw = resp.json()
            processed: List[Dict[str, Any]] = []

            for r in repos_raw:
                name = r.get("name", "")
                desc = r.get("description") or "No description provided."
                lang = r.get("language") or "Other"
                topics = r.get("topics") or []
                stars = r.get("stargazers_count", 0)
                forks = r.get("forks_count", 0)
                updated_at = r.get("updated_at", "")
                created_at = r.get("created_at", "")
                homepage = r.get("homepage") or ""
                html_url = r.get("html_url") or f"https://github.com/{username}/{name}"

                category = _infer_category(name, desc, topics, lang)

                processed.append({
                    "id": r.get("id"),
                    "name": name,
                    "title": name.replace("-", " ").replace("_", " ").title(),
                    "description": desc,
                    "language": lang,
                    "languageColor": LANGUAGE_COLORS.get(lang, "#8b949e"),
                    "topics": topics,
                    "stars": stars,
                    "forks": forks,
                    "openIssues": r.get("open_issues_count", 0),
                    "size": r.get("size", 0),
                    "isFork": r.get("fork", False),
                    "htmlUrl": html_url,
                    "homepage": homepage if homepage and homepage.startswith("http") else None,
                    "updatedAt": updated_at,
                    "updatedAtRelative": _calc_relative_time(updated_at),
                    "createdAt": created_at,
                    "category": category,
                    "image": f"https://opengraph.githubassets.com/1/{username}/{name}",
                })

            _set_cache(cache_key, processed)
            return processed
        else:
            print(f"[GitHub Repos] HTTP {resp.status_code}: {resp.text}")
    except Exception as e:
        print(f"[GitHub Repos Error] {e}")

    cached = _get_cache(cache_key)
    if cached:
        return cached

    return []

# -------------------------------------------------------------
# 3. Contributions & Heatmap (GraphQL API)
# -------------------------------------------------------------
def get_contributions(username: str = GITHUB_USERNAME, year: Optional[int] = None) -> Dict[str, Any]:
    target_year = year or datetime.now().year
    cache_key = f"contributions_{username}_{target_year}"
    if _is_cache_valid(cache_key, TTL_CONTRIBUTIONS):
        return _get_cache(cache_key)

    from_date = f"{target_year}-01-01T00:00:00Z"
    to_date = f"{target_year}-12-31T23:59:59Z"

    query = """
    query ($username: String!, $from: DateTime, $to: DateTime) {
      user(login: $username) {
        contributionsCollection(from: $from, to: $to) {
          totalCommitContributions
          totalPullRequestContributions
          totalIssueContributions
          totalRepositoryContributions
          totalPullRequestReviewContributions
          contributionCalendar {
            totalContributions
            weeks {
              contributionDays {
                contributionCount
                date
                weekday
                color
              }
            }
          }
        }
      }
    }
    """
    variables = {"username": username, "from": from_date, "to": to_date}

    try:
        resp = requests.post(
            GRAPHQL_ENDPOINT,
            json={"query": query, "variables": variables},
            headers=_get_headers(),
            timeout=15,
        )
        if resp.status_code == 200:
            res_json = resp.json()
            user_data = res_json.get("data", {}).get("user", {})
            if user_data:
                col = user_data.get("contributionsCollection", {})
                calendar = col.get("contributionCalendar", {})
                weeks = calendar.get("weeks", [])

                # Calculate streaks & active days
                active_days = 0
                max_streak = 0
                current_streak = 0
                streak_counter = 0

                all_days: List[Dict[str, Any]] = []
                for week in weeks:
                    for day in week.get("contributionDays", []):
                        all_days.append(day)
                        count = day.get("contributionCount", 0)
                        if count > 0:
                            active_days += 1
                            streak_counter += 1
                            if streak_counter > max_streak:
                                max_streak = streak_counter
                        else:
                            streak_counter = 0

                # Current streak starting backwards from today
                today_str = datetime.now().strftime("%Y-%m-%d")
                curr = 0
                for day in reversed(all_days):
                    d_str = day.get("date", "")
                    if d_str > today_str:
                        continue
                    cnt = day.get("contributionCount", 0)
                    if cnt > 0:
                        curr += 1
                    else:
                        if curr > 0:
                            break

                current_streak = curr

                result = {
                    "year": target_year,
                    "totalContributions": calendar.get("totalContributions", 0),
                    "totalCommits": col.get("totalCommitContributions", 0),
                    "totalPullRequests": col.get("totalPullRequestContributions", 0),
                    "totalIssues": col.get("totalIssueContributions", 0),
                    "totalRepositories": col.get("totalRepositoryContributions", 0),
                    "totalReviews": col.get("totalPullRequestReviewContributions", 0),
                    "activeDays": active_days,
                    "longestStreak": max_streak,
                    "currentStreak": current_streak,
                    "weeks": weeks,
                    "availableYears": [2026, 2025, 2024],
                    "isCached": False,
                    "lastUpdated": datetime.now(timezone.utc).isoformat(),
                }
                _set_cache(cache_key, result)
                return result
            else:
                print(f"[GitHub Contributions GraphQL Error] {res_json.get('errors')}")
        else:
            print(f"[GitHub Contributions HTTP {resp.status_code}] {resp.text}")
    except Exception as e:
        print(f"[GitHub Contributions Error] {e}")

    cached = _get_cache(cache_key)
    if cached:
        cached["isCached"] = True
        return cached

    # Fallback structure with synthetic days for smooth UI
    return {
        "year": target_year,
        "totalContributions": 74904 if target_year == 2026 else 12500,
        "totalCommits": 21385 if target_year == 2026 else 4200,
        "totalPullRequests": 12,
        "totalIssues": 8,
        "totalRepositories": 99,
        "totalReviews": 4,
        "activeDays": 240,
        "longestStreak": 38,
        "currentStreak": 14,
        "weeks": [],
        "availableYears": [2026, 2025, 2024],
        "isCached": True,
        "isFallback": True,
        "lastUpdated": datetime.now(timezone.utc).isoformat(),
    }

# -------------------------------------------------------------
# 4. Language Analytics
# -------------------------------------------------------------
def get_languages(username: str = GITHUB_USERNAME) -> Dict[str, Any]:
    cache_key = f"languages_{username}"
    if _is_cache_valid(cache_key, TTL_LANGUAGES):
        return _get_cache(cache_key)

    repos = get_repositories(username)
    lang_totals: Dict[str, int] = {}
    lang_repos: Dict[str, int] = {}

    # Aggregate by language frequency and fetch detailed bytes for top repos
    for repo in repos:
        if repo.get("isFork"):
            continue
        lang = repo.get("language")
        if lang and lang != "Other":
            lang_repos[lang] = lang_repos.get(lang, 0) + 1
            # Weight repo size as approximate byte mass if detailed call not available
            size_kb = max(repo.get("size", 10), 1)
            lang_totals[lang] = lang_totals.get(lang, 0) + (size_kb * 1024)

    total_bytes = sum(lang_totals.values()) or 1
    percentages: List[Dict[str, Any]] = []

    for name, b in sorted(lang_totals.items(), key=lambda x: x[1], reverse=True):
        pct = round((b / total_bytes) * 100, 1)
        percentages.append({
            "name": name,
            "bytes": b,
            "percentage": pct,
            "reposCount": lang_repos.get(name, 0),
            "color": LANGUAGE_COLORS.get(name, "#8b949e"),
        })

    result = {
        "languages": percentages[:8], # Top 8 languages
        "totalLanguagesCount": len(percentages),
        "totalReposAnalyzed": len(repos),
        "lastUpdated": datetime.now(timezone.utc).isoformat(),
    }
    _set_cache(cache_key, result)
    return result

# -------------------------------------------------------------
# 5. Commit Activity Timeline
# -------------------------------------------------------------
def get_commits(username: str = GITHUB_USERNAME, limit: int = 15) -> List[Dict[str, Any]]:
    cache_key = f"commits_{username}"
    if _is_cache_valid(cache_key, TTL_COMMITS):
        return _get_cache(cache_key)

    # Use search commits or recent events to retrieve live commits
    url = f"{GITHUB_API_BASE}/search/commits?q=author:{username}&sort=author-date&order=desc&per_page={limit}"
    headers = _get_headers()
    headers["Accept"] = "application/vnd.github.cloak-preview+json, application/vnd.github+json"

    try:
        resp = requests.get(url, headers=headers, timeout=12)
        if resp.status_code == 200:
            items = resp.json().get("items", [])
            commits: List[Dict[str, Any]] = []
            for item in items:
                commit_info = item.get("commit", {})
                repo_info = item.get("repository", {})
                author_info = commit_info.get("author", {})
                date_str = author_info.get("date", "")
                sha = item.get("sha", "")

                commits.append({
                    "sha": sha[:7],
                    "fullSha": sha,
                    "message": commit_info.get("message", "").split("\n")[0],
                    "repository": repo_info.get("name", "portfolio"),
                    "repositoryUrl": repo_info.get("html_url", f"https://github.com/{username}"),
                    "date": date_str,
                    "dateRelative": _calc_relative_time(date_str),
                    "commitUrl": item.get("html_url") or f"https://github.com/{username}/{repo_info.get('name')}/commit/{sha}",
                    "author": author_info.get("name", username),
                })

            if commits:
                _set_cache(cache_key, commits)
                return commits
    except Exception as e:
        print(f"[GitHub Commits Error] {e}")

    # Fallback to extracts from events
    events = get_activity(username)
    fallback_commits: List[Dict[str, Any]] = []
    for ev in events:
        if ev.get("type") == "PushEvent":
            for c in ev.get("commits", []):
                fallback_commits.append({
                    "sha": c.get("sha", "")[:7],
                    "fullSha": c.get("sha", ""),
                    "message": c.get("message", "Updated repository"),
                    "repository": ev.get("repo", ""),
                    "repositoryUrl": f"https://github.com/{username}/{ev.get('repo')}",
                    "date": ev.get("createdAt", ""),
                    "dateRelative": ev.get("timeAgo", ""),
                    "commitUrl": f"https://github.com/{username}/{ev.get('repo')}/commit/{c.get('sha')}",
                    "author": username,
                })
        if len(fallback_commits) >= limit:
            break

    if fallback_commits:
        _set_cache(cache_key, fallback_commits)
        return fallback_commits

    return []

# -------------------------------------------------------------
# 6. Live Activity Events Feed
# -------------------------------------------------------------
def get_activity(username: str = GITHUB_USERNAME, limit: int = 15) -> List[Dict[str, Any]]:
    cache_key = f"activity_{username}"
    if _is_cache_valid(cache_key, TTL_ACTIVITY):
        return _get_cache(cache_key)

    url = f"{GITHUB_API_BASE}/users/{username}/events/public?per_page={limit * 2}"
    try:
        resp = requests.get(url, headers=_get_headers(), timeout=10)
        if resp.status_code == 200:
            events_raw = resp.json()
            activities: List[Dict[str, Any]] = []

            for ev in events_raw:
                ev_type = ev.get("type", "")
                repo_full = ev.get("repo", {}).get("name", "")
                repo_name = repo_full.split("/")[-1] if "/" in repo_full else repo_full
                created_at = ev.get("created_at", "")
                payload = ev.get("payload", {})
                time_ago = _calc_relative_time(created_at)

                act_item = None
                if ev_type == "PushEvent":
                    commits = payload.get("commits", [])
                    count = len(commits)
                    first_msg = commits[0].get("message", "Pushed commits").split("\n")[0] if commits else "Pushed code"
                    act_item = {
                        "id": ev.get("id"),
                        "type": "push",
                        "badge": "⚡ Push",
                        "icon": "commit",
                        "repo": repo_name,
                        "repoUrl": f"https://github.com/{repo_full}",
                        "description": f"Pushed {count} commit{'s' if count != 1 else ''}: \"{first_msg}\"",
                        "createdAt": created_at,
                        "timeAgo": time_ago,
                        "commits": [{"sha": c.get("sha", ""), "message": c.get("message", "")} for c in commits[:3]],
                    }
                elif ev_type == "CreateEvent":
                    ref_type = payload.get("ref_type", "repository")
                    act_item = {
                        "id": ev.get("id"),
                        "type": "create",
                        "badge": f"🌱 New {ref_type.capitalize()}",
                        "icon": "plus",
                        "repo": repo_name,
                        "repoUrl": f"https://github.com/{repo_full}",
                        "description": f"Created {ref_type} in {repo_name}",
                        "createdAt": created_at,
                        "timeAgo": time_ago,
                    }
                elif ev_type == "WatchEvent":
                    act_item = {
                        "id": ev.get("id"),
                        "type": "star",
                        "badge": "⭐ Star",
                        "icon": "star",
                        "repo": repo_name,
                        "repoUrl": f"https://github.com/{repo_full}",
                        "description": f"Starred repository {repo_name}",
                        "createdAt": created_at,
                        "timeAgo": time_ago,
                    }
                elif ev_type == "ForkEvent":
                    forkee = payload.get("forkee", {}).get("full_name", "")
                    act_item = {
                        "id": ev.get("id"),
                        "type": "fork",
                        "badge": "🍴 Fork",
                        "icon": "fork",
                        "repo": repo_name,
                        "repoUrl": f"https://github.com/{repo_full}",
                        "description": f"Forked {repo_name} to {forkee}",
                        "createdAt": created_at,
                        "timeAgo": time_ago,
                    }
                elif ev_type == "PullRequestEvent":
                    action = payload.get("action", "")
                    pr = payload.get("pull_request", {})
                    act_item = {
                        "id": ev.get("id"),
                        "type": "pr",
                        "badge": f"🔀 PR {action}",
                        "icon": "pr",
                        "repo": repo_name,
                        "repoUrl": pr.get("html_url", f"https://github.com/{repo_full}"),
                        "description": f"{action.capitalize()} PR #{pr.get('number', '')}: {pr.get('title', '')}",
                        "createdAt": created_at,
                        "timeAgo": time_ago,
                    }
                elif ev_type == "IssuesEvent":
                    action = payload.get("action", "")
                    issue = payload.get("issue", {})
                    act_item = {
                        "id": ev.get("id"),
                        "type": "issue",
                        "badge": f"🐛 Issue {action}",
                        "icon": "issue",
                        "repo": repo_name,
                        "repoUrl": issue.get("html_url", f"https://github.com/{repo_full}"),
                        "description": f"{action.capitalize()} issue #{issue.get('number', '')}: {issue.get('title', '')}",
                        "createdAt": created_at,
                        "timeAgo": time_ago,
                    }

                if act_item:
                    activities.append(act_item)
                if len(activities) >= limit:
                    break

            _set_cache(cache_key, activities)
            return activities
    except Exception as e:
        print(f"[GitHub Activity Error] {e}")

    return _get_cache(cache_key) or []

# -------------------------------------------------------------
# 7. Repository README (Sanitized)
# -------------------------------------------------------------
def get_readme(repo_name: str, username: str = GITHUB_USERNAME) -> Dict[str, Any]:
    cache_key = f"readme_{username}_{repo_name}"
    if _is_cache_valid(cache_key, TTL_REPOS):
        return _get_cache(cache_key)

    url = f"{GITHUB_API_BASE}/repos/{username}/{repo_name}/readme"
    try:
        resp = requests.get(url, headers=_get_headers(), timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            raw_content = data.get("content", "")
            encoding = data.get("encoding", "base64")
            if encoding == "base64":
                decoded_bytes = base64.b64decode(raw_content)
                text = decoded_bytes.decode("utf-8", errors="replace")
            else:
                text = raw_content

            # Sanitize: strip script tags, iframe, object, embed, onerror attributes
            sanitized = re.sub(r"<\s*script[^>]*>.*?<\s*/\s*script\s*>", "", text, flags=re.DOTALL | re.IGNORECASE)
            sanitized = re.sub(r"<\s*iframe[^>]*>.*?<\s*/\s*iframe\s*>", "", sanitized, flags=re.DOTALL | re.IGNORECASE)
            sanitized = re.sub(r"on\w+\s*=\s*['\"].*?['\"]", "", sanitized, flags=re.IGNORECASE)

            # Limit length to 10,000 characters for snappy UI rendering
            if len(sanitized) > 10000:
                sanitized = sanitized[:10000] + "\n\n*(README truncated for preview. View full repository on GitHub.)*"

            result = {
                "repo": repo_name,
                "content": sanitized,
                "htmlUrl": f"https://github.com/{username}/{repo_name}",
            }
            _set_cache(cache_key, result)
            return result
    except Exception as e:
        print(f"[GitHub Readme Error] {e}")

    return {
        "repo": repo_name,
        "content": f"### {repo_name}\n\n*README details can be viewed directly on the GitHub repository.*",
        "htmlUrl": f"https://github.com/{username}/{repo_name}",
    }

# -------------------------------------------------------------
# 8. Consolidated Master Overview Endpoint
# -------------------------------------------------------------
def get_overview(username: str = GITHUB_USERNAME) -> Dict[str, Any]:
    cache_key = f"master_overview_{username}"
    if _is_cache_valid(cache_key, 600): # 10 minutes cache
        cached = _get_cache(cache_key)
        cached["isCached"] = True
        return cached

    profile = get_profile(username)
    repos = get_repositories(username)
    contributions = get_contributions(username)
    languages = get_languages(username)
    commits = get_commits(username, limit=10)
    activity = get_activity(username, limit=10)

    # Compute aggregate stats
    total_stars = sum(r.get("stars", 0) for r in repos if not r.get("isFork"))
    total_forks = sum(r.get("forks", 0) for r in repos if not r.get("isFork"))
    total_repos_count = profile.get("public_repos") or len(repos)
    total_commits = contributions.get("totalCommits") or 21385
    total_contributions = contributions.get("totalContributions") or 74904

    stats = {
        "totalRepos": total_repos_count,
        "totalStars": total_stars,
        "totalForks": total_forks,
        "totalCommits": total_commits,
        "totalContributions": total_contributions,
        "totalPullRequests": contributions.get("totalPullRequests", 12),
        "totalIssues": contributions.get("totalIssues", 8),
        "totalReviews": contributions.get("totalReviews", 4),
        "followers": profile.get("followers", 9),
        "following": profile.get("following", 9),
        "activeDays": contributions.get("activeDays", 240),
        "longestStreak": contributions.get("longestStreak", 38),
        "currentStreak": contributions.get("currentStreak", 14),
    }

    result = {
        "profile": profile,
        "statistics": stats,
        "contributions": contributions,
        "languages": languages,
        "repositories": repos,
        "commits": commits,
        "activity": activity,
        "meta": {
            "username": username,
            "isCached": False,
            "lastSynchronized": datetime.now(timezone.utc).isoformat(),
            "serverTime": datetime.now(timezone.utc).isoformat(),
        }
    }

    _set_cache(cache_key, result)
    return result
