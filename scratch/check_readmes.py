import requests
import re
import json

repos = [
    'TraffiX-AI',
    'Plagiarism-Checker',
    'BashaConverter-Krishna',
    'fake-review-id-system',
    'AI-Medical-Consultancy',
    'kirito1.0'
]

def extract_live_demo(readme_text: str, homepage: str = None) -> str | None:
    if homepage and homepage.startswith('http') and not 'github.com' in homepage:
        return homepage

    # Look for explicit demo links: [Live Demo](url), [Demo](url), Demo: url, Live: url
    patterns = [
        r'\[(?:Live\s*Demo|Demo|Live\s*Site|Live\s*App|View\s*Live|Live|Website)\]\((https?://[^\s\)]+)\)',
        r'(?:Live\s*Demo|Demo\s*URL|Live\s*Site|Demo|Deployment|Website)\s*[:\-]\s*(https?://[^\s\)]+)',
        r'https?://[a-zA-Z0-9_\-]+\.(?:vercel\.app|netlify\.app|streamlit\.app|onrender\.com|render\.com|herokuapp\.com|github\.io/[a-zA-Z0-9_\-]+)',
    ]
    for p in patterns:
        m = re.search(p, readme_text, re.IGNORECASE)
        if m:
            url = m.group(1) if m.groups() else m.group(0)
            url = url.rstrip('.,)>"\']')
            if not 'github.com' in url and not 'shields.io' in url and not 'capsule-render' in url:
                return url
    return None

for repo in repos:
    r = requests.get(f'http://127.0.0.1:8000/api/github/readme?repo={repo}')
    content = r.json().get('content', '')
    live_url = extract_live_demo(content)
    print(f"Repo: {repo} -> Live Link: {live_url}")
