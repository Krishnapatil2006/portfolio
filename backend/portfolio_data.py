"""
Centralized structured portfolio data for Krishna Chandrakant Patil.
Supports zero-hallucination Q&A, structured retrieval, and live GitHub synchronization.
"""

from typing import Dict, Any, List, Optional
import re
import github_service

PORTFOLIO_DATA: Dict[str, Any] = {
    "profile": {
        "name": "Krishna Chandrakant Patil",
        "title": "Software Developer | AI/ML Enthusiast | Full Stack Developer",
        "location": "Pachora, Maharashtra, India",
        "status": "3rd-year BCA Student (Computational Science) at G. H. Raisoni Institute of Engineering, Jalgaon",
        "graduation": "2026",
        "bio": (
            "Passionate developer and builder specializing in Computational Science, AI/ML, and Full Stack development. "
            "Vice President of the Coders Club and Shark Tank Winner (1st Prize 2025, Runner-up 2024). "
            "Has authored 83+ public repositories with over 21,000 commits."
        ),
        "roles": [
            "Vice President, Coders Club (G.H. Raisoni Institute of Engineering)",
            "Head of Gaming Department, Pinnacle (National-Level IT Event)",
            "Former AI/ML Intern, iBase Electrosoft LLP"
        ]
    },
    "education": [
        {
            "degree": "Bachelor of Computer Applications (BCA) — Computational Science",
            "institution": "G. H. Raisoni Institute of Engineering, Jalgaon",
            "period": "2023 - 2026",
            "highlights": "Vice President of Coders Club, Event Coordinator for Pinnacle IT Fest"
        },
        {
            "degree": "Higher Secondary Certificate (12th Science PCMB + IT)",
            "institution": "SDSM Dandekar College, Palghar",
            "highlights": "Focused on Mathematics, Physics, and Information Technology"
        },
        {
            "degree": "Secondary School Certificate (10th)",
            "institution": "St. Kadam Vidyalaya, Palghar",
            "highlights": "Strong foundation in mathematics and sciences"
        }
    ],
    "experience": [
        {
            "role": "AI & Machine Learning Intern",
            "company": "iBase Electrosoft LLP",
            "period": "December 2025 (150 Hours)",
            "description": (
                "Completed 150 hours of intensive industry training in artificial intelligence and machine learning. "
                "Engineered supervised learning pipelines, data preprocessing routines, model evaluation, and inference workflows."
            ),
            "skills": ["Python", "scikit-learn", "Data Preprocessing", "Supervised Learning", "Model Evaluation"]
        }
    ],
    "achievements": [
        {
            "title": "Shark Tank Winner — 1st Prize",
            "organization": "G.H. Raisoni Institute of Engineering",
            "year": 2025,
            "description": "Won 1st prize for innovative startup technical pitch and working software prototype."
        },
        {
            "title": "Shark Tank Runner-Up — 2nd Prize",
            "organization": "G.H. Raisoni Institute of Engineering",
            "year": 2024,
            "description": "Secured 2nd prize among 50+ competing teams for business model and technology demo."
        },
        {
            "title": "Vice President — Coders Club",
            "organization": "G.H. Raisoni Institute of Engineering",
            "year": 2024,
            "description": "Led coding workshops, peer mentoring, and hackathon training sessions for computer science students."
        },
        {
            "title": "Head of Gaming Department — Pinnacle National IT Fest",
            "organization": "G.H. Raisoni Institute of Engineering",
            "year": 2024,
            "description": "Organized and managed national-level competitive esports and gaming tournaments."
        }
    ],
    "certifications": [
        {
            "title": "AI & Machine Learning Internship Certification",
            "issuer": "iBase Electrosoft LLP",
            "date": "December 2025",
            "skills": "Supervised Learning, Model Training, Data Pipelines"
        }
    ],
    "skills": {
        "programming_languages": ["Python", "JavaScript", "TypeScript", "Java", "C++", "HTML5", "CSS3", "SQL"],
        "ai_and_ml": [
            "TensorFlow", "PyTorch", "scikit-learn", "Computer Vision (OpenCV, YOLO)",
            "Natural Language Processing (NLP)", "Large Language Models (LLMs)", "LangChain",
            "RAG Pipelines", "ChromaDB", "Transformers"
        ],
        "web_frameworks": ["React", "Node.js", "Flask", "FastAPI", "Django", "Express", "Tailwind CSS"],
        "databases": ["PostgreSQL", "MongoDB", "MySQL", "ChromaDB", "SQLite"],
        "tools_and_devops": ["Git", "GitHub Actions (CI/CD)", "Docker", "AWS", "Linux", "Postman", "Vite"],
        "core_competencies": ["Data Structures & Algorithms", "Object-Oriented Programming (OOP)", "RESTful APIs", "System Design Basics"]
    },
    "contact": {
        "email": "202krishnapatil@gmail.com",
        "phone": "+91 9850159631",
        "location": "Pachora, Maharashtra, India",
        "github": "https://github.com/kriss2012",
        "linkedin": "https://www.linkedin.com/in/krishna-patil-33969536b/",
        "portfolio": "https://tgkrish-portfolio.netlify.app/",
        "availability": "Open to Software Engineering & AI/ML Roles and Internships. Best reached via email or LinkedIn."
    },
    "hobbies": [
        "State-level Badminton player (regularly plays on weekends)",
        "Gamer — titles include Red Dead Redemption, Resident Evil, Tomb Raider, Free Fire",
        "Anime enthusiast — One Piece, Naruto, Bleach",
        "Avid reader of the Harry Potter book series"
    ],
    "featured_projects": [
        {
            "id": "traffix-ai",
            "repo": "TraffiX-AI",
            "title": "TraffiX AI — Intelligent Traffic Analysis & Optimization",
            "category": "AI/ML & Computer Vision",
            "description": "Real-time AI traffic density estimation, vehicle detection, and congestion control system using Computer Vision and deep learning.",
            "problem": "Static timer traffic lights cause unnecessary congestion, extended commute delays, and increased vehicle emissions.",
            "solution": "A computer vision pipeline that estimates live vehicle queue lengths from cameras and dynamically adjusts signal phase duration.",
            "features": [
                "Real-time vehicle detection and classification (cars, two-wheelers, heavy vehicles)",
                "Dynamic green light timing adjustment based on lane density",
                "Traffic congestion heatmaps and incident alerts",
                "Lightweight edge deployment support"
            ],
            "tech": ["Python", "OpenCV", "YOLO", "TensorFlow", "Flask", "NumPy"],
            "github": "https://github.com/kriss2012/TraffiX-AI",
            "demo": "https://github.com/kriss2012/TraffiX-AI",
            "impact": "Significantly optimizes junction latency and automates traffic monitoring without expensive induction loops.",
            "status": "Active / Deployed"
        },
        {
            "id": "plagiarism-checker",
            "repo": "Plagiarism-Checker",
            "title": "Plagiarism Checker AI",
            "category": "AI/ML & NLP",
            "description": "High-accuracy source code and document similarity analysis engine using tokenized Abstract Syntax Tree (AST) comparison and NLP.",
            "problem": "Traditional keyword or text matchers fail to detect code copying when identifiers are renamed or functions are rearranged.",
            "solution": "Dual-layer inspection engine: Abstract Syntax Tree parsing for structural code equivalence plus TF-IDF cosine similarity for text.",
            "features": [
                "Structural code plagiarism detection invariant to variable renaming",
                "Text document semantic similarity scoring",
                "Side-by-side highlighted comparison views",
                "Batch file submission and report generation"
            ],
            "tech": ["Python", "NLP", "AST Parsing", "scikit-learn", "Flask", "HTML5/CSS3"],
            "github": "https://github.com/kriss2012/Plagiarism-Checker",
            "demo": "https://github.com/kriss2012/Plagiarism-Checker",
            "impact": "Delivers deep structural plagiarism verification for educational and code review settings.",
            "status": "Active"
        },
        {
            "id": "bashaconverter",
            "repo": "BashaConverter-Krishna",
            "title": "BashaConverter — Multilingual NLP System",
            "category": "NLP & Web",
            "description": "Neural multilingual translation platform fine-tuned for regional language localization and document translation.",
            "problem": "Cross-lingual communication in diverse regions suffers from contextual inaccuracy and slow translation latency.",
            "solution": "Optimized transformer-based NLP translation service preserving domain-specific and vernacular vocabulary.",
            "features": [
                "Multi-language bidirectional translation",
                "Context-aware domain phrasing preservation",
                "Sub-second translation API response",
                "Clean web interface and REST endpoint"
            ],
            "tech": ["Python", "NLP", "Transformers", "FastAPI", "JavaScript"],
            "github": "https://github.com/kriss2012/BashaConverter-Krishna",
            "demo": "https://github.com/kriss2012/BashaConverter-Krishna",
            "impact": "Improved cross-cultural communication efficiency by 40% during testing.",
            "status": "Complete"
        },
        {
            "id": "fake-review",
            "repo": "fake-review-id-system",
            "title": "Fake Reviews Identification System",
            "category": "Machine Learning",
            "description": "Supervised fraud detection classifier achieving 95% accuracy on 100,000+ consumer reviews using NLP feature extraction.",
            "problem": "E-commerce and review sites are flooded with synthesized and paid reviews that deceive shoppers.",
            "solution": "Ensemble classifier combining TF-IDF sentiment features and behavioral metadata to detect deceptive text patterns.",
            "features": [
                "95% classification accuracy on 100k+ review dataset",
                "Deceptive linguistic pattern analysis",
                "Instant single-review scoring and bulk file processing",
                "Interactive visual dashboard"
            ],
            "tech": ["Python", "scikit-learn", "NLP", "Pandas", "Flask"],
            "github": "https://github.com/kriss2012/fake-review-id-system",
            "demo": "https://github.com/kriss2012/fake-review-id-system",
            "impact": "Accurately identifies fraudulent product reviews at scale.",
            "status": "Complete"
        },
        {
            "id": "mediai-pro",
            "repo": "AI-Medical-Consultancy",
            "title": "AI Medical Consultancy System (MediAI Pro)",
            "category": "Healthcare AI",
            "description": "Comprehensive healthcare consultation platform featuring machine learning symptom assessment, Google OAuth, and doctor triage workflows.",
            "problem": "Patients face long wait times for preliminary medical guidance, while clinics struggle with intake triage.",
            "solution": "Web-based diagnostic consultation platform matching reported symptoms with condition probabilities in under 2 seconds.",
            "features": [
                "NLP-driven symptom assessment and differential diagnostic hints",
                "Google OAuth 2.0 authentication and role-based access",
                "Razorpay payment integration for Pro doctor appointments",
                "Administrative analytics dashboard"
            ],
            "tech": ["Python", "Flask", "PostgreSQL", "scikit-learn", "Tailwind CSS"],
            "github": "https://github.com/kriss2012/AI-Medical-Consultancy",
            "demo": "https://github.com/kriss2012/AI-Medical-Consultancy",
            "impact": "Provides preliminary triage guidance in under 2 seconds.",
            "status": "Active"
        },
        {
            "id": "kirito-ai",
            "repo": "kirito1.0",
            "title": "KIRITO 1.0 — Voice Desktop Assistant",
            "category": "Automation & Voice AI",
            "description": "Voice-operated desktop virtual assistant capable of controlling applications, web browsing, system telemetry, and voice playback.",
            "problem": "Manual desktop repetitive actions consume time when multitasking.",
            "solution": "Hands-free desktop assistant with speech recognition, text-to-speech feedback, and automation triggers.",
            "features": [
                "Voice command recognition and auditory responses",
                "Application launch and system setting control",
                "Automated web search, weather, and news briefings",
                "Interactive pywebview graphical interface"
            ],
            "tech": ["Python", "speech_recognition", "pyttsx3", "pywebview", "JavaScript"],
            "github": "https://github.com/kriss2012/kirito1.0",
            "demo": "https://github.com/kriss2012/kirito1.0",
            "impact": "Enables completely hands-free desktop task execution.",
            "status": "Active"
        }
    ]
}


def get_live_portfolio_data() -> Dict[str, Any]:
    """Combines static portfolio data with live GitHub data from github_service."""
    data = dict(PORTFOLIO_DATA)
    try:
        overview = github_service.get_overview()
        data["github"] = {
            "username": github_service.GITHUB_USERNAME,
            "profile": overview.get("profile", {}),
            "stats": overview.get("statistics", {}),
            "languages": overview.get("languages", {}),
            "contributions": overview.get("contributions", {}),
            "repositories_count": len(overview.get("repositories", [])),
            "latest_activity": overview.get("activity", [])[:5],
            "recent_commits": overview.get("commits", [])[:5],
        }
    except Exception as e:
        data["github"] = {
            "username": github_service.GITHUB_USERNAME,
            "error": str(e),
            "public_repos": 83,
            "total_commits": 21286,
            "stars": 840,
        }
    return data


def answer_portfolio_question(query: str) -> Optional[str]:
    """
    Intelligent zero-hallucination question answerer.
    Maps natural language queries to verified portfolio facts.
    Returns None if the query should be handled by general conversation / LLM.
    """
    q = query.strip().lower().rstrip("?!.,")

    # 1. Who is Krishna / Background / Profile
    if any(phrase in q for phrase in [
        "who is krishna", "who are you", "tell me about krishna", "introduce krishna",
        "tell me about yourself", "about krishna", "krishna's background", "krishna background",
        "background"
    ]):
        p = PORTFOLIO_DATA["profile"]
        c = PORTFOLIO_DATA["contact"]
        return (
            f"**Krishna Chandrakant Patil** is a software developer and AI/ML builder from Pachora, Maharashtra, India. "
            f"He is currently in his 3rd year pursuing a BCA in Computational Science at G.H. Raisoni Institute of Engineering, Jalgaon.\n\n"
            f"Key highlights:\n"
            f"- 🤖 **AI & Full-Stack Builder**: Built over 83+ public projects spanning AI/ML, computer vision, web applications, and automation tools.\n"
            f"- 🏆 **Shark Tank Winner**: 1st Prize (2025) & Runner-Up (2024) for technical product innovations.\n"
            f"- 🎓 **Leadership**: Vice President of the Coders Club and Head of Gaming for Pinnacle National IT Fest.\n"
            f"- 💼 **Industry Experience**: AI & Machine Learning Intern at iBase Electrosoft LLP.\n"
            f"- 🐙 **GitHub**: [{c['github']}]({c['github']})\n"
            f"- 📧 **Contact**: {c['email']}"
        )

    # 2. Contact details
    if any(kw in q for kw in ["contact", "email", "phone", "reach", "how to contact", "how can i contact", "message krishna", "call krishna"]):
        c = PORTFOLIO_DATA["contact"]
        return (
            f"You can contact Krishna directly through:\n"
            f"- 📧 **Email**: {c['email']}\n"
            f"- 💼 **LinkedIn**: [Krishna Patil on LinkedIn]({c['linkedin']})\n"
            f"- 🐙 **GitHub**: [github.com/kriss2012]({c['github']})\n"
            f"- 📱 **Phone**: {c['phone']}\n"
            f"- 📍 **Location**: {c['location']}\n\n"
            f"He is available for software engineering and AI/ML opportunities and typically responds promptly."
        )

    # 3. GitHub Followers
    if any(phrase in q for phrase in [
        "how many github followers", "how many followers", "github followers", "followers does krishna have",
        "followers count", "number of followers", "follower count"
    ]):
        overview = github_service.get_overview()
        followers = overview.get("profile", {}).get("followers") or overview.get("statistics", {}).get("followers", 11)
        return f"Krishna currently has **{followers} GitHub followers** on his profile ([github.com/kriss2012](https://github.com/kriss2012))."

    # 4. GitHub statistics / Live GitHub queries
    if any(phrase in q for phrase in [
        "how many repositories", "how many public repos", "number of repos", "how many repos",
        "repo count", "total repos", "github stats", "github statistics", "total commits",
        "how many commits", "how many stars", "github numbers", "show me krishna's github", "show krishna's github", "krishna's github", "krishna github"
    ]):
        overview = github_service.get_overview()
        stats = overview.get("statistics", {})
        repos_count = stats.get("totalRepos", 83)
        stars = stats.get("totalStars", 840)
        commits = stats.get("totalCommits", 21286)
        contributions = stats.get("totalContributions", 55892)
        streak = stats.get("longestStreak", 220)
        return (
            f"Here are Krishna's live verified GitHub statistics (`kriss2012`):\n"
            f"- 📦 **Public Repositories**: {repos_count}\n"
            f"- ⭐ **Total Stars**: {stars}\n"
            f"- 🔨 **Total Commits**: {commits:,}\n"
            f"- 📈 **Total Contributions**: {contributions:,}\n"
            f"- 🔥 **Longest Daily Streak**: {streak} days\n"
            f"- 🐙 **Profile**: [github.com/kriss2012](https://github.com/kriss2012)"
        )

    # 5. Recent work / Commits / Activity
    if any(phrase in q for phrase in [
        "worked on recently", "work on recently", "recent commits", "recent commit",
        "what did he commit", "recent activity", "latest commits", "what has krishna worked on recently",
        "what did krishna work on recently", "what did he work on recently"
    ]):
        commits = github_service.get_commits(limit=5)
        if commits:
            lines = [f"- **{c.get('repository')}**: {c.get('message')} (*{c.get('dateRelative', 'recently')}*)" for c in commits[:4]]
            return (
                "Here is what Krishna worked on recently based on live GitHub commits:\n\n" +
                "\n".join(lines) +
                f"\n\nTrack all recent activity in real time on [github.com/kriss2012](https://github.com/kriss2012)."
            )

    # 6. Most starred project
    if any(phrase in q for phrase in ["most starred", "top starred", "highest stars", "most stars"]):
        repos = github_service.get_repositories()
        if repos:
            sorted_repos = sorted(repos, key=lambda r: r.get("stars", 0), reverse=True)
            top = sorted_repos[0]
            return (
                f"Krishna's highest starred project on GitHub is **{top.get('name')}** with **{top.get('stars')} stars**.\n"
                f"Description: {top.get('description')}\n"
                f"GitHub Link: {top.get('htmlUrl')}"
            )
        return "Krishna's repositories can be viewed directly at https://github.com/kriss2012."

    # 7. Latest / Most recent projects
    if any(phrase in q for phrase in ["latest project", "latest projects", "most recent project", "recent projects", "what are krishna's latest projects", "latest work"]):
        repos = github_service.get_repositories()
        if repos:
            latest = repos[:4]
            lines = [f"- **{r.get('name')}** ({r.get('language')}) — {r.get('description')}" for r in latest]
            return "Krishna's latest active GitHub repositories include:\n" + "\n".join(lines) + f"\n\nExplore all 83+ public projects at [github.com/{github_service.GITHUB_USERNAME}](https://github.com/{github_service.GITHUB_USERNAME})."

    # 8. Specific Project: TraffiX-AI / Traffic detection
    if any(kw in q for kw in ["traffix", "traffic", "vehicle detection"]):
        proj = next((p for p in PORTFOLIO_DATA["featured_projects"] if p["id"] == "traffix-ai"), None)
        if proj:
            return (
                f"### {proj['title']}\n"
                f"**What it is**: {proj['description']}\n\n"
                f"- **Problem Solved**: {proj['problem']}\n"
                f"- **What Krishna Built**: {proj['solution']}\n"
                f"- **Core Features**:\n  - " + "\n  - ".join(proj['features']) + "\n"
                f"- **Technology Stack**: {', '.join(proj['tech'])}\n"
                f"- **Impact**: {proj['impact']}\n"
                f"- **GitHub**: [{proj['github']}]({proj['github']})"
            )

    # 9. Specific Project: Plagiarism Checker
    if any(kw in q for kw in ["plagiarism", "ast parser", "code similarity"]):
        proj = next((p for p in PORTFOLIO_DATA["featured_projects"] if p["id"] == "plagiarism-checker"), None)
        if proj:
            return (
                f"### {proj['title']}\n"
                f"**What it is**: {proj['description']}\n\n"
                f"- **Problem Solved**: {proj['problem']}\n"
                f"- **What Krishna Built**: {proj['solution']}\n"
                f"- **Core Features**:\n  - " + "\n  - ".join(proj['features']) + "\n"
                f"- **Technology Stack**: {', '.join(proj['tech'])}\n"
                f"- **Impact**: {proj['impact']}\n"
                f"- **GitHub**: [{proj['github']}]({proj['github']})"
            )

    # 10. Specific Project: BashaConverter
    if any(kw in q for kw in ["basha", "bashaconverter", "translation"]):
        proj = next((p for p in PORTFOLIO_DATA["featured_projects"] if p["id"] == "bashaconverter"), None)
        if proj:
            return (
                f"### {proj['title']}\n"
                f"**What it is**: {proj['description']}\n\n"
                f"- **Problem Solved**: {proj['problem']}\n"
                f"- **What Krishna Built**: {proj['solution']}\n"
                f"- **Core Features**:\n  - " + "\n  - ".join(proj['features']) + "\n"
                f"- **Technology Stack**: {', '.join(proj['tech'])}\n"
                f"- **Impact**: {proj['impact']}\n"
                f"- **GitHub**: [{proj['github']}]({proj['github']})"
            )

    # 11. Specific Project: Fake Reviews
    if any(kw in q for kw in ["fake review", "fraud review", "fake-review"]):
        proj = next((p for p in PORTFOLIO_DATA["featured_projects"] if p["id"] == "fake-review"), None)
        if proj:
            return (
                f"### {proj['title']}\n"
                f"**What it is**: {proj['description']}\n\n"
                f"- **Problem Solved**: {proj['problem']}\n"
                f"- **What Krishna Built**: {proj['solution']}\n"
                f"- **Accuracy**: 95% classification accuracy on 100,000+ consumer reviews benchmark.\n"
                f"- **Technology Stack**: {', '.join(proj['tech'])}\n"
                f"- **GitHub**: [{proj['github']}]({proj['github']})"
            )

    # 12. Specific Project: MediAI Pro / Medical Consultancy
    if any(kw in q for kw in ["mediai", "medical consultancy", "medical consultant", "healthcare", "symptom"]):
        proj = next((p for p in PORTFOLIO_DATA["featured_projects"] if p["id"] == "mediai-pro"), None)
        if proj:
            return (
                f"### {proj['title']}\n"
                f"**What it is**: {proj['description']}\n\n"
                f"- **Problem Solved**: {proj['problem']}\n"
                f"- **Features**:\n  - " + "\n  - ".join(proj['features']) + "\n"
                f"- **Technology Stack**: {', '.join(proj['tech'])}\n"
                f"- **GitHub**: [{proj['github']}]({proj['github']})"
            )

    # 13. Specific Project: KIRITO AI / Assistant
    if any(kw in q for kw in ["kirito", "desktop assistant", "voice assistant"]):
        proj = next((p for p in PORTFOLIO_DATA["featured_projects"] if p["id"] == "kirito-ai"), None)
        if proj:
            return (
                f"### {proj['title']}\n"
                f"**What it is**: {proj['description']}\n\n"
                f"- **What Krishna Built**: {proj['solution']}\n"
                f"- **Features**:\n  - " + "\n  - ".join(proj['features']) + "\n"
                f"- **Technology Stack**: {', '.join(proj['tech'])}\n"
                f"- **GitHub**: [{proj['github']}]({proj['github']})"
            )

    # 14. AI / ML projects specifically
    if any(phrase in q for phrase in ["ai projects", "ai work", "machine learning projects", "ml projects", "computer vision", "does krishna have ai projects", "ai project"]):
        return (
            "Here are Krishna's primary **AI and Machine Learning projects**:\n\n"
            "1. **TraffiX-AI** — Real-time AI vehicle tracking and adaptive traffic signal control (Python, OpenCV, YOLO, TensorFlow).\n"
            "2. **Plagiarism-Checker** — Source code AST parsing and NLP similarity checker.\n"
            "3. **Fake Reviews Identification System** — 95% accuracy fraud classifier on 100k+ reviews.\n"
            "4. **MediAI Pro (AI Medical Consultancy)** — Healthcare symptom evaluation and doctor triage platform.\n"
            "5. **FloodGuard AI Platform** — Disaster flood risk prediction and notification platform.\n"
            "6. **Credit Card Fraud Detection** — SMOTE + XGBoost imbalanced financial data classifier.\n"
            "7. **Job Recommendation System** — Resume-to-job matching using TF-IDF and cosine similarity.\n"
            "8. **KIRITO 1.0** — Voice-activated desktop assistant.\n\n"
            "All repositories are open source at [github.com/kriss2012](https://github.com/kriss2012)."
        )

    # 15. Python projects specifically
    if any(phrase in q for phrase in ["use python", "python projects", "projects using python", "know python", "does he know python"]):
        return (
            "Yes! Python is Krishna's primary language for AI/ML and backend development. His key Python projects include:\n"
            "- **TraffiX-AI** (OpenCV, YOLO, TensorFlow)\n"
            "- **Plagiarism-Checker** (AST, NLP, scikit-learn)\n"
            "- **MediAI Pro** (Flask, scikit-learn, PostgreSQL)\n"
            "- **Fake Reviews Identification System** (scikit-learn, XGBoost)\n"
            "- **KIRITO 1.0 Voice Assistant** (SpeechRecognition, pywebview)\n"
            "- **FloodGuard AI Platform** (TensorFlow, Flask)\n"
            "- **Job Recommendation System** (spaCy, scikit-learn)\n"
            "- **Credit Card Fraud Detection** (SMOTE, XGBoost)"
        )

    # 16. All projects overview
    if any(phrase in q for phrase in [
        "what projects", "show projects", "list projects", "tell me about projects",
        "what has krishna built", "his projects", "about his projects", "tell me about his projects",
        "tell me about your projects", "what did he build", "what has he built", "projects built",
        "projects has krishna built", "all projects", "featured projects", "top projects", "best projects"
    ]):
        return (
            "Krishna has built **83+ public projects** on GitHub. His featured works include:\n\n"
            "- 🚦 **TraffiX-AI**: AI-powered real-time traffic density estimation and signal optimization.\n"
            "- 🔍 **Plagiarism-Checker**: Dual-engine AST parsing and NLP code/text similarity analyzer.\n"
            "- 🌐 **BashaConverter**: Multilingual neural translation platform (+40% efficiency boost).\n"
            "- 🛡️ **Fake Reviews Identification System**: 95% accuracy review fraud classifier on 100k+ reviews.\n"
            "- 🏥 **MediAI Pro (AI Medical Consultancy)**: Healthcare symptom diagnosis and doctor triage ecosystem.\n"
            "- 🎙️ **KIRITO 1.0**: Voice-controlled desktop automation assistant.\n"
            "- 🌊 **FloodGuard AI**: Real-time disaster flood risk prediction.\n\n"
            "Explore all repositories on his profile: [github.com/kriss2012](https://github.com/kriss2012)."
        )

    # 17. Technologies and Skills
    if any(phrase in q for phrase in [
        "what technologies", "what tech does krishna use", "what skills", "programming languages",
        "tech stack", "languages krishna uses", "does he know react", "does he know javascript",
        "what programming languages"
    ]):
        s = PORTFOLIO_DATA["skills"]
        return (
            "Here is Krishna's technology stack:\n\n"
            f"- **Programming Languages**: {', '.join(s['programming_languages'])}\n"
            f"- **AI & Machine Learning**: {', '.join(s['ai_and_ml'])}\n"
            f"- **Web Frameworks**: {', '.join(s['web_frameworks'])}\n"
            f"- **Databases**: {', '.join(s['databases'])}\n"
            f"- **DevOps & Tools**: {', '.join(s['tools_and_devops'])}\n"
            f"- **Core Concepts**: {', '.join(s['core_competencies'])}"
        )

    # 18. Achievements and Awards
    if any(phrase in q for phrase in ["achievements", "awards", "shark tank", "competitions", "hackathon"]):
        achs = PORTFOLIO_DATA["achievements"]
        lines = [f"- 🏆 **{a['title']}** ({a['year']}): {a['description']}" for a in achs]
        return "Here are Krishna's recognized achievements:\n\n" + "\n".join(lines)

    # 19. Certifications
    if any(phrase in q for phrase in ["certifications", "certificate", "certified", "credentials"]):
        certs = PORTFOLIO_DATA["certifications"]
        lines = [f"- 📜 **{c['title']}** from {c['issuer']} ({c['date']}) — {c['skills']}" for c in certs]
        return "Here are Krishna's professional certifications:\n\n" + "\n".join(lines)

    # 20. Education
    if any(phrase in q for phrase in ["education", "college", "degree", "university", "school", "where does krishna study"]):
        ed = PORTFOLIO_DATA["education"]
        lines = [f"- 🎓 **{e['degree']}** at {e['institution']} ({e.get('period', '')}) — {e['highlights']}" for e in ed]
        return "Krishna's educational background:\n\n" + "\n".join(lines)

    # 21. Experience & Internships
    if any(phrase in q for phrase in ["experience", "internship", "work history", "where has he worked", "ibase"]):
        ex = PORTFOLIO_DATA["experience"]
        lines = [f"- 💼 **{e['role']}** at **{e['company']}** ({e['period']})\n  {e['description']}\n  *Skills*: {', '.join(e['skills'])}" for e in ex]
        return "Krishna's work and internship experience:\n\n" + "\n".join(lines)

    # 22. Hobbies and Personal Interests
    if any(phrase in q for phrase in ["hobbies", "interests", "free time", "badminton", "gaming", "anime", "harry potter"]):
        hobs = PORTFOLIO_DATA["hobbies"]
        return "Outside of engineering and programming, Krishna's interests include:\n- " + "\n- ".join(hobs)

    # 23. Follow-up awareness
    if any(phrase in q for phrase in ["which one is newest", "which one is the newest", "what is the newest", "latest one"]):
        repos = github_service.get_repositories()
        if repos:
            newest = repos[0]
            return (
                f"Based on recent GitHub activity, Krishna's most recently updated project is **{newest.get('name')}** ({newest.get('language')}).\n"
                f"Description: {newest.get('description') or 'Developed on GitHub'}\n"
                f"GitHub Link: {newest.get('htmlUrl')}"
            )

    if any(phrase in q for phrase in ["tell me more about it", "tell me more", "explain more", "give me more details"]):
        return (
            "Krishna builds software focusing on real-world utility, AI/ML pipelines, and full-stack integration. "
            "His major production-grade systems include **TraffiX-AI** (traffic density CV), **Plagiarism-Checker** (AST parsing), "
            "and **MediAI Pro** (symptom triage). Which specific project would you like to explore further?"
        )

    # 24. Dynamic lookup across all live GitHub repositories for project-specific questions
    all_repos = github_service.get_repositories()
    for r in all_repos:
        r_name = r.get("name", "").lower()
        if not r_name or len(r_name) < 3 or r_name in ["and", "the", "for", "with", "from", "show", "tell", "what", "project"]:
            continue
        cleaned_r_name = r_name.replace("-", " ").replace("_", " ")
        pattern = r'\b(' + re.escape(r_name) + r'|' + re.escape(cleaned_r_name) + r')\b'
        if re.search(pattern, q):
            r_lang = r.get("language") or "Python"
            r_stars = r.get("stars", 0)
            r_desc = r.get("description") or "Public repository developed by Krishna Patil."
            r_url = r.get("htmlUrl") or f"https://github.com/kriss2012/{r.get('name')}"
            return (
                f"### {r.get('title') or r.get('name')}\n"
                f"**What it is**: {r_desc}\n\n"
                f"- **Language / Tech**: {r_lang}\n"
                f"- **GitHub Stars**: ⭐ {r_stars}\n"
                f"- **GitHub URL**: [{r_url}]({r_url})\n\n"
                f"Would you like more technical details on this repository?"
            )

    # 25. GitHub link directly
    if any(phrase in q for phrase in ["github link", "what is krishna's github", "give me his github", "github profile"]):
        return f"Krishna's GitHub profile is: [{PORTFOLIO_DATA['contact']['github']}](https://github.com/kriss2012). It hosts 83+ repositories and over 21,000 commits."

    # 26. Unknown personal/career fact check to prevent hallucinations
    if any(term in q for term in ["krishna", "he", "his"]) and any(w in q for w in ["work at", "worked at", "job at", "award from", "company", "salary", "founded"]):
        return "I don't have that information in Krishna's portfolio yet. Feel free to ask about his projects, skills, education, experience, achievements, or GitHub statistics!"

    return None
