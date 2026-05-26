# --- CRITICAL RENDER FIX FOR CHROMA DB ---
try:
    __import__('pysqlite3')
    import sys
    sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')
except ImportError:
    # Use built-in sqlite3 (default on Windows/MacOS development machines)
    pass
# -----------------------------------------

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
import requests
import json
from datetime import datetime, date as date_obj
from dotenv import load_dotenv

from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_chroma import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.tools import tool
from langchain_community.utilities import SerpAPIWrapper

# History management
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.chat_history import BaseChatMessageHistory

load_dotenv(dotenv_path="../.env")
load_dotenv()

# Map the .env keys to what LangChain expects, handling different cases and stripping leading/trailing spaces
gemini_key = os.getenv("Gemini_Api_Key") or os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
groq_key = os.getenv("Groq_Api_Key") or os.getenv("GROQ_API_KEY")
serp_key = os.getenv("Serp_Api_Key") or os.getenv("SERP_API_KEY") or os.getenv("SERPAPI_API_KEY")

os.environ["GOOGLE_API_KEY"] = gemini_key.strip() if gemini_key else "dummy_google_key"
os.environ["GROQ_API_KEY"] = groq_key.strip() if groq_key else "dummy_groq_key"
os.environ["SERPAPI_API_KEY"] = serp_key.strip() if serp_key else "dummy_serp_key"

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health_check():
    """Lightweight health check — used by frontend to wake up Render and confirm the server is alive."""
    return {"status": "ok", "service": "krishna-ai-twin"}

@app.get("/api/ping")
async def ping():
    """Alias ping endpoint for wake-up calls."""
    return {"pong": True}

# Use llama-3.1-8b-instant to prevent daily token rate limit issues on the free tier,
# while maintaining fast and accurate tool-calling.
llm = ChatGroq(
    model="llama-3.1-8b-instant",  
    temperature=0.3,
    max_tokens=1024,
)

# --- Global Vector Store / RAG Setup ---
retriever = None
try:
    # Auto-build RAG database if it's missing or empty
    if not os.path.exists("./twin_chroma_db") or len(os.listdir("./twin_chroma_db")) == 0:
        print("Chroma DB not found or empty. Auto-building RAG database...")
        try:
            from rag_setup import build_rag
            build_rag()
        except Exception as build_err:
            print(f"Failed to auto-build RAG database: {build_err}")

    embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
    vector_store = Chroma(
        persist_directory="./twin_chroma_db",
        collection_name="krishna_knowledge",
        embedding_function=embeddings
    )
    retriever = vector_store.as_retriever(search_kwargs={"k": 5})
except Exception as e:
    print(f"Failed to initialize Chroma DB with Google Embeddings: {e}")

# --- Tools Setup (Defined in global scope to ensure proper serialization) ---

@tool
def resume_knowledge_base(query: str = "") -> str:
    """Use this tool to retrieve information about Krishna Patil's personal background, education, skills, projects, and experiences."""
    global retriever
    if not query:
        query = "Krishna Patil overview"
        
    if retriever is not None:
        try:
            docs = retriever.invoke(query)
            if docs:
                return "\n\n".join([d.page_content for d in docs])
        except Exception as e:
            print(f"Error querying retriever: {e}")
            
    # Fallback: read from all knowledge files directly (no embeddings needed)
    # Priority: Projects_Info.md first for project queries, then knowledge_base.md
    fallback_files = [
        ("Projects_Info.md", ["project", "github", "repo", "mediai", "kirito", "floodguard",
                              "job recommend", "fake review", "fake news", "credit card",
                              "bashaconvert", "basha", "kiri", "echo", "jarvis", "student",
                              "iot", "game", "spotify", "elearning", "nlp", "ml project",
                              "machine learning project", "work", "built", "created", "developed"]),
        ("knowledge_base.md", []),  # default fallback
    ]
    try:
        query_lower = query.lower()
        chosen_file = "knowledge_base.md"  # default
        for fname, keywords in fallback_files:
            if keywords and any(k in query_lower for k in keywords):
                if os.path.exists(fname):
                    chosen_file = fname
                    break

        with open(chosen_file, "r", encoding="utf-8") as f:
            content = f.read()

        # For Projects_Info.md, do section-based search
        if chosen_file == "Projects_Info.md":
            sections = content.split("\n### ")
            matched = []
            for sec in sections:
                title_line = sec.split("\n")[0].lower()
                if any(k in title_line for k in query_lower.split()) or \
                   any(k in query_lower for k in ["all", "best", "list", "project", "repo", "github"]):
                    matched.append("### " + sec)
            if matched:
                # Return top 5 matching sections to keep response tight but complete
                return "\n\n".join(matched[:5])
            return content[:4000]  # Return first 4000 chars if no section match

        # For knowledge_base.md, use keyword section matching
        sections = content.split("\n## ")
        matching_sections = []
        for i, sec in enumerate(sections):
            sec_title = sec.split("\n")[0].lower()
            if any(k in query_lower for k in ["project", "work", "experience", "mediai", "kirito", "job", "fake review", "basha"]):
                if "project" in sec_title or "work" in sec_title:
                    matching_sections.append(("## " + sec) if i > 0 else sec)
            elif any(k in query_lower for k in ["hobby", "interest", "sport", "game", "music", "badminton", "anime", "harry potter"]):
                if "interest" in sec_title:
                    matching_sections.append(("## " + sec) if i > 0 else sec)
            elif any(k in query_lower for k in ["skill", "expert", "tech", "language", "programming"]):
                if "skill" in sec_title:
                    matching_sections.append(("## " + sec) if i > 0 else sec)
            elif any(k in query_lower for k in ["contact", "email", "phone", "linkedin", "github"]):
                if "contact" in sec_title:
                    matching_sections.append(("## " + sec) if i > 0 else sec)
            elif any(k in query_lower for k in ["schedul", "availab", "free", "weekend", "saturday", "sunday", "meeting", "interview"]):
                if "schedul" in sec_title or "availab" in sec_title:
                    matching_sections.append(("## " + sec) if i > 0 else sec)
        if matching_sections:
            return "\n\n".join(matching_sections)
        return "\n\n## ".join(sections[:4])
    except Exception as e:
        return "I am Krishna Patil, a passionate BCA student specializing in Computational Science from Pachora, Maharashtra. I have built 48+ projects including AI systems, web apps, games, and tools."

@tool
def calculator(expression: str = "") -> str:
    """Evaluate a mathematical expression. Use this tool for any math-related queries."""
    if not expression:
        return "Error: No expression provided."
    try:
        allowed_chars = "0123456789+-*/(). "
        if not all(c in allowed_chars for c in expression):
            return "Error: Invalid characters in expression."
        result = eval(expression)
        return str(result)
    except Exception as e:
        return f"Error evaluating expression: {e}"

@tool
def get_weather(city: str) -> str:
    """Get the current weather information for a specific city."""
    api_key = os.getenv("WeatherStack_Api_Key", "")
    if not api_key:
        return f"Cannot fetch weather. WeatherStack API key is missing. Assuming it's sunny in {city}!"
    url = f"http://api.weatherstack.com/current?access_key={api_key}&query={city}"
    try:
        result = requests.get(url).json()
        if "current" in result:
            temp = result["current"]["temperature"]
            desc = result["current"]["weather_descriptions"][0]
            return f"The current weather in {city} is {desc} with a temperature of {temp} degrees Celsius."
        else:
            return "Could not fetch weather data."
    except Exception as e:
        return f"Error fetching weather: {e}"

@tool
def get_current_datetime(query: str = "") -> str:
    """Get the current date and time. The query argument is optional and ignored."""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

@tool
def schedule_meeting(date: str, time: str, name: str, email: str) -> str:
    """Schedule a meeting, interview, or meetup with Krishna Patil.
    Krishna is ALWAYS free on Saturdays and Sundays.
    Provide date (YYYY-MM-DD), time (HH:MM 24-hour format), name, and email.
    """
    meeting_file = "meetings.json"
    try:
        # Validate date format
        try:
            parsed_date = datetime.strptime(date, "%Y-%m-%d").date()
        except ValueError:
            return f"Invalid date format '{date}'. Please use YYYY-MM-DD (e.g. 2025-06-07)."

        # Validate time format
        try:
            datetime.strptime(time, "%H:%M")
        except ValueError:
            return f"Invalid time format '{time}'. Please use HH:MM (e.g. 10:30)."

        # Check if it's a weekday — Krishna prefers weekends but is flexible
        weekday = parsed_date.weekday()  # 0=Mon ... 5=Sat, 6=Sun
        day_name = parsed_date.strftime("%A")
        weekend_note = ""
        if weekday < 5:
            weekend_note = f" Note: {day_name} is a weekday — Krishna prefers Saturdays or Sundays for interviews/meetups, but is flexible."

        if os.path.exists(meeting_file):
            with open(meeting_file, "r") as f:
                meetings = json.load(f)
        else:
            meetings = []

        # Check for time conflicts
        for m in meetings:
            if m["date"] == date and m["time"] == time:
                return (f"Sorry, Krishna already has a meeting on {date} at {time}. "
                        f"Please pick a different time slot.{weekend_note}")

        meetings.append({"date": date, "time": time, "name": name, "email": email})
        with open(meeting_file, "w") as f:
            json.dump(meetings, f, indent=4)
        return (f"Done! Meeting scheduled with {name} on {date} ({day_name}) at {time}. "
                f"Krishna will reach out to {email} to confirm.{weekend_note}")
    except Exception as e:
        return f"Failed to schedule meeting: {str(e)}"

@tool
def check_schedule(date: str) -> str:
    """Check Krishna's availability for a specific date (YYYY-MM-DD).
    Krishna is ALWAYS available on Saturdays and Sundays for interviews and meetups.
    """
    meeting_file = "meetings.json"
    try:
        try:
            parsed_date = datetime.strptime(date, "%Y-%m-%d").date()
        except ValueError:
            return f"Invalid date format '{date}'. Please use YYYY-MM-DD."

        weekday = parsed_date.weekday()  # 5=Sat, 6=Sun
        day_name = parsed_date.strftime("%A")
        is_weekend = weekday >= 5

        if not os.path.exists(meeting_file):
            if is_weekend:
                return f"Krishna is completely free on {date} ({day_name})! Weekends are perfect for interviews and meetups."
            return f"Krishna is free on {date} ({day_name}), though he prefers Saturdays or Sundays for interviews."

        with open(meeting_file, "r") as f:
            meetings = json.load(f)

        day_meetings = [m for m in meetings if m["date"] == date]
        if not day_meetings:
            if is_weekend:
                return f"Krishna is completely free on {date} ({day_name})! Great day for an interview or meetup."
            return f"Krishna is free on {date} ({day_name}). He prefers weekends (Sat/Sun) for meetings."

        schedule = "\n".join([f"- {m['time']} with {m['name']}" for m in day_meetings])
        return (f"Krishna's schedule on {date} ({day_name}):\n{schedule}\n"
                f"He may still have open slots — just pick a different time!")
    except Exception as e:
        return f"Failed to check schedule: {str(e)}"

@tool
def get_free_slots(query: str = "") -> str:
    """Get Krishna's general availability and preferred meeting days.
    Use this when someone asks when Krishna is free, available, or wants to schedule.
    """
    return (
        "Krishna is available EVERY Saturday and Sunday for interviews, meetups, and calls. "
        "He is flexible with time slots — morning (10:00-12:00) and afternoon (14:00-18:00) work best. "
        "For weekday meetings, he can arrange something after 5:00 PM. "
        "To book a slot, share your name, email, preferred date (Sat or Sun), and time."
    )

# Set up SERP API search tool
try:
    search_tool_func = SerpAPIWrapper()
except Exception as e:
    print(f"Failed to initialize SerpAPI: {e}")
    search_tool_func = None

@tool
def web_search(query: str) -> str:
    """A search engine. Useful for when you need to answer questions about current events. Input should be a search query."""
    if search_tool_func:
        return search_tool_func.run(query)
    return "Web search is currently unavailable."

tools = [resume_knowledge_base, web_search, calculator, get_weather, get_current_datetime, schedule_meeting, check_schedule, get_free_slots]

# --- Agent Setup ---
qa_system_prompt = """You are the AI Twin of Krishna Chandrakant Patil — a real person, not a bot.
You speak exactly like him: confident, casual, and direct.
You are a 3rd-year BCA student specializing in Computational Science from Pachora, Maharashtra, India.
You are talking to a recruiter or portfolio visitor.

CRITICAL RULES:

1. RESPONSE LENGTH — Read the question type:
   - Small talk, greetings, yes/no questions → 1-2 sentences max.
   - Questions about projects, skills, experience, background → Give a FULL, DETAILED answer.
     NEVER say "would you like to know more?" — just TELL THEM everything directly.
     NEVER just redirect. If they ask "what are your projects?", list ALL projects with tech stack and what they do.
   - Always COMPLETE the answer. Do not stop halfway and ask if they want details.

2. TOOL USAGE — For ANY question about yourself, skills, projects, background, or availability:
   ALWAYS call the 'resume_knowledge_base' tool FIRST and use its output as your answer.
   Do NOT answer from memory alone when a tool is available.

3. PROJECTS — When asked about projects (even with typos like "Proejcts", "proyects"):
   List ALL projects: MediAI Pro, Job Recommendation System, KIRITO AI, Fake Reviews System, BashaConverter, Twin AI Chatbot.
   For each, mention: what it does, the tech stack, and something impressive about it.

4. SCHEDULING — Krishna is FREE every Saturday and Sunday for interviews, calls, and meetups.
   - Use 'get_free_slots' when asked about availability.
   - Use 'check_schedule' then 'schedule_meeting' to book a slot.
   - Use 'get_current_datetime' to determine today's date if needed.

5. TYPOS & MISSPELLINGS — Handle gracefully. Infer intent. "Proejcts" = projects. Never ask for clarification on obvious typos.

6. PERSONA — Never say you are an AI, bot, or language model. You ARE Krishna.
   Speak first person: "I built...", "My project...", "I'm currently..."

7. OFF-TOPIC — For completely unrelated questions, respond briefly and redirect:
   "Ha, interesting! But I'd love to talk about my work — want to see my projects?"

8. ERRORS — If a tool fails, answer from your knowledge base memory. NEVER show technical errors.
"""

prompt = ChatPromptTemplate.from_messages(
    [
        ("system", qa_system_prompt),
        MessagesPlaceholder("history"),
        ("human", "{input}"),
        MessagesPlaceholder("agent_scratchpad"),
    ]
)

agent = create_tool_calling_agent(llm, tools, prompt)
agent_executor = AgentExecutor(
    agent=agent,
    tools=tools,
    verbose=True,
    handle_parsing_errors=True,   # Never crash on malformed LLM output
    max_iterations=6,             # Prevent infinite loops
    return_intermediate_steps=False,
)

store = {}

def get_session_history(session_id: str) -> BaseChatMessageHistory:
    if session_id not in store:
        store[session_id] = ChatMessageHistory()
    return store[session_id]

conversational_agent = RunnableWithMessageHistory(
    agent_executor,
    get_session_history,
    input_messages_key="input",
    history_messages_key="history",
)

class ChatRequest(BaseModel):
    message: str
    session_id: str = "portfolio_visitor"

# --- Fast-path: instant answers for greetings & one-word queries (no agent round-trip) ---

# Pure greetings — return instantly without touching the LLM at all
INSTANT_REPLIES = {
    "hi": "Hey! I'm Krishna's AI Twin. Ask me about my projects, skills, or schedule a meeting!",
    "hey": "Hey there! What would you like to know about Krishna?",
    "hello": "Hello! I'm Krishna Patil's AI Twin. What can I help you with?",
    "yo": "Yo! What's up? Ask me anything about Krishna's work or projects!",
    "hii": "Hey! I'm Krishna's AI Twin. Ask me about my projects, skills, or schedule a meeting!",
    "hiii": "Hey! I'm Krishna's AI Twin. Ask me about my projects, skills, or schedule a meeting!",
    "helo": "Hello! I'm Krishna Patil's AI Twin. What can I help you with?",
    "heloo": "Hello! I'm Krishna Patil's AI Twin. What can I help you with?",
    "sup": "Hey! Ready to chat. Ask me about my skills, projects, or when we can meet!",
    "whats up": "Hey! Ready to chat. Ask me about my skills, projects, or when we can meet!",
    "what's up": "Hey! Ready to chat. Ask me about my skills, projects, or when we can meet!",
    "ok": "Sure! What else would you like to know?",
    "okay": "Sure! What else would you like to know?",
    "thanks": "Happy to help! Anything else you'd like to know about Krishna?",
    "thank you": "You're welcome! Feel free to ask about projects, skills, or scheduling a call!",
    "thankyou": "You're welcome! Feel free to ask about projects, skills, or scheduling a call!",
    "bye": "Thanks for stopping by! Reach out anytime on LinkedIn or email. Goodbye!",
    "goodbye": "Thanks for visiting! Feel free to connect on LinkedIn. Goodbye!",
    "cya": "Thanks for stopping by! Reach out anytime on LinkedIn or email. Goodbye!",
}

# Self-introduction triggers (any message that says "introduce yourself" in any form)
INTRO_TRIGGERS = [
    "introduce yourself", "introduction", "introduce", "tell me about yourself",
    "tell me about you", "who are you", "who r u", "who ru", "about you",
    "about yourself", "wat r u", "what r u", "what are you", "whos this",
    "who is this", "who is krishna", "who are you", "describe yourself",
    "inntroduce", "intrroduce", "inroduce", "introdue", "intrdoce",
]

INTRO_REPLY = (
    "Hey! I'm **Krishna Chandrakant Patil** — or rather, his AI Twin 😄\n\n"
    "I'm a 3rd-year BCA student specialising in Computational Science at G.H. Raisoni Institute of Engineering, "
    "Jalgaon. I'm from Pachora, Maharashtra, India.\n\n"
    "Here's a quick snapshot of who I am:\n"
    "- 🤖 **AI & ML enthusiast** — I've built 12+ ML projects including fraud detection, medical AI, and flood prediction systems\n"
    "- 💻 **Full-Stack Developer** — React, Node.js, Python/Flask/Django, REST APIs\n"
    "- 🏆 **Shark Tank Winner** (1st Prize 2025 & Runner-up 2024)\n"
    "- 🎓 **Vice President** of the Coders Club at my college\n"
    "- 🏸 **State-level Badminton player** & avid gamer (RDR, Resident Evil, Free Fire)\n\n"
    "I've built **48+ projects** on GitHub — from KIRITO AI (voice desktop assistant) to MediAI Pro (healthcare AI) to this very Twin Chatbot you're talking to!\n\n"
    "Ask me about my **projects**, **skills**, **experience**, or **schedule a meeting** with me!"
)

# One-word topic triggers — fetch context immediately and skip agent tool loop
TOPIC_KEYWORDS = {
    # Projects (with common typos)
    "projects":   "projects",
    "project":    "projects",
    "proejcts":   "projects",
    "projcts":    "projects",
    "porjects":   "projects",
    "projecs":    "projects",
    "projecst":   "projects",
    "projecta":   "projects",  # as seen in user query "best projecta"
    "proyects":   "projects",
    "repos":      "projects",
    "repo":       "projects",
    "work":       "projects",
    "built":      "projects",
    # Skills
    "skills":     "skills",
    "skill":      "skills",
    "skils":      "skills",
    "sklils":     "skills",
    "tech":       "skills",
    "stack":      "skills",
    "technologies": "skills",
    "programming": "skills",
    "languages":  "skills",
    # Contact
    "contact":    "contact",
    "email":      "contact",
    "linkedin":   "contact",
    "github":     "contact",
    "links":      "contact",
    "portfolio":  "contact",
    "reach":      "contact",
    # Schedule
    "schedule":   "schedule",
    "meeting":    "schedule",
    "meetup":     "schedule",
    "available":  "schedule",
    "availability": "schedule",
    "free":       "schedule",
    "saturday":   "schedule",
    "sunday":     "schedule",
    "interview":  "schedule",
    "call":       "schedule",
    # Education
    "education":  "education",
    "college":    "education",
    "bca":        "education",
    "degree":     "education",
    "study":      "education",
    "studying":   "education",
    "university": "education",
    # Experience
    "experience": "experience",
    "internship": "experience",
    "intern":     "experience",
    "worked":     "experience",
    "job":        "experience",
    "achievement": "experience",
    "achievements": "experience",
    # Hobbies
    "hobbies":    "hobbies",
    "hobby":      "hobbies",
    "interests":  "hobbies",
    "sports":     "hobbies",
    "badminton":  "hobbies",
    "gaming":     "hobbies",
    "anime":      "hobbies",
    "games":      "hobbies",
    "music":      "hobbies",
}

TOPIC_CONTEXT = {
    "projects":   "List all of Krishna's GitHub projects with tech stacks and what they do",
    "skills":     "What are Krishna's technical skills, programming languages, and expertise",
    "contact":    "What are Krishna's contact details, portfolio links, LinkedIn, GitHub, email",
    "schedule":   "What is Krishna's availability for meetings and interviews",
    "education":  "What is Krishna's educational background and qualifications",
    "experience": "What is Krishna's work experience, internships, and achievements",
    "hobbies":    "What are Krishna's hobbies, interests, sports, and personal life",
}

# Static intelligent fallbacks per topic (used when LLM is down)
TOPIC_STATIC_FALLBACKS = {
    "projects": (
        "Here are my top projects:\n"
        "- **MediAI Pro** — Flask + ML healthcare app with symptom diagnosis, Google OAuth, Razorpay payments\n"
        "- **KIRITO AI** — Voice-activated desktop assistant (Python + speech recognition + pywebview)\n"
        "- **FloodGuard AI** — Real-time flood prediction & alert platform (Python + TensorFlow + Leaflet.js)\n"
        "- **Job Recommendation System** — Resume-to-job matching using TF-IDF & cosine similarity (Flask + MongoDB + Docker)\n"
        "- **Fake Reviews Detector** — 95% accuracy ML classifier on 100k+ reviews\n"
        "- **Credit Card Fraud Detection** — SMOTE + XGBoost on imbalanced financial datasets\n"
        "- **Twin AI Chatbot** — This chatbot! LangChain + Groq + RAG pipeline with Chroma DB\n"
        "- **BashaConverter** — Multilingual NLP translation system (+40% communication efficiency)\n"
        "...and 40+ more on GitHub: github.com/kriss2012"
    ),
    "skills": (
        "My tech stack:\n"
        "- **Languages**: Python, JavaScript/TypeScript, Java, C++\n"
        "- **Web**: React, Node.js, Flask, Django, FastAPI, REST APIs\n"
        "- **AI/ML**: TensorFlow, PyTorch, scikit-learn, LangChain, NLP, LLMs, Computer Vision\n"
        "- **Databases**: PostgreSQL, MongoDB, MySQL, ChromaDB\n"
        "- **Cloud/DevOps**: AWS, Docker, GitHub Actions, CI/CD\n"
        "- **Other**: WebRTC, Socket.io, MQTT, RAG pipelines, Generative AI"
    ),
    "contact": (
        "Here's how to reach me:\n"
        "- 📧 Email: 202krishnapatil@gmail.com\n"
        "- 💼 LinkedIn: linkedin.com/in/krishna-patil-33969536b\n"
        "- 🐙 GitHub: github.com/kriss2012\n"
        "- 🌐 Portfolio: tgkrish-portfolio.netlify.app\n"
        "- 📱 Phone: +91 9850159631"
    ),
    "schedule": (
        "I'm available every **Saturday and Sunday** for interviews, calls, and meetups!\n"
        "- Morning: 10:00 AM – 12:00 PM IST\n"
        "- Afternoon: 2:00 PM – 6:00 PM IST\n"
        "- Weekdays: After 5:00 PM if needed\n"
        "Share your name, email, preferred date & time and I'll confirm via email!"
    ),
    "education": (
        "I'm a 3rd-year **BCA student** (Computational Science) at G.H. Raisoni Institute of Engineering, Jalgaon (graduating 2026).\n"
        "I'm the **Vice President of the Coders Club** and Head of Gaming at our national-level IT event 'Pinnacle'.\n"
        "Before this: SDSM Dandekar College (12th, Science stream + IT) and St. Kadam Vidyalaya (10th)."
    ),
    "experience": (
        "- **AI & ML Intern** at iBase Electrosoft LLP (Dec 2025, 150 hours) — real-world ML workflows, supervised learning\n"
        "- **Shark Tank Winner** — 1st Prize 2025, Runner-up 2024\n"
        "- **Vice President**, Coders Club\n"
        "- **Head of Gaming Dept** for 'Pinnacle' (National Level IT Event)"
    ),
    "hobbies": (
        "Outside of coding:\n"
        "- 🏸 State-level **Badminton player** — I'm on the court every weekend\n"
        "- 🎮 Avid gamer — RDR, Resident Evil, Tomb Raider, Free Fire (6-7 years!)\n"
        "- 🎌 Anime fan — One Piece, Naruto, Bleach\n"
        "- 📚 Big Harry Potter nerd — read all the books!\n"
        "- 🎵 Music: 90s classics, lofi, rock, Yo Yo Honey Singh\n"
        "- 📺 Shows: Game of Thrones, Lord of the Rings"
    ),
}

def _fuzzy_topic_match(clean_msg: str) -> str | None:
    """Detect topic even in multi-word typo-heavy messages. Returns topic key or None."""
    # Check for intro triggers first
    for trigger in INTRO_TRIGGERS:
        if trigger in clean_msg:
            return "__intro__"
    
    # Check all words in message against TOPIC_KEYWORDS
    words = clean_msg.split()
    for word in words:
        # Direct match
        if word in TOPIC_KEYWORDS:
            return TOPIC_KEYWORDS[word]
        # Substring match for longer words (catches "projecta", "proejctss" etc)
        if len(word) >= 5:
            for kw, topic in TOPIC_KEYWORDS.items():
                if len(kw) >= 5 and (word.startswith(kw[:4]) or kw.startswith(word[:4])):
                    return topic
    return None


def fast_path_reply(msg: str):
    """Returns an instant reply for simple/short queries, or None to proceed to the full agent."""
    clean = msg.strip().lower().rstrip("!?.,")

    # Exact match for greetings
    if clean in INSTANT_REPLIES:
        return INSTANT_REPLIES[clean]
    
    # Check for self-introduction triggers (check before topic routing)
    for trigger in INTRO_TRIGGERS:
        if trigger in clean:
            return INTRO_REPLY

    # Single-word or very short (<=3 words) topic queries
    words = clean.split()
    topic = None
    if len(words) <= 3:
        for word in words:
            if word in TOPIC_KEYWORDS:
                topic = TOPIC_KEYWORDS[word]
                break
        # If no direct hit, try fuzzy match on short messages
        if topic is None and len(words) <= 3:
            topic = _fuzzy_topic_match(clean)
    
    if topic == "__intro__":
        return INTRO_REPLY
    
    if topic:
        # Pre-fetch context — cap at 3000 chars to avoid token overflow
        try:
            context = resume_knowledge_base.func(TOPIC_CONTEXT[topic])
            context = context[:3000]  # CRITICAL: prevent token overflow
        except Exception:
            return TOPIC_STATIC_FALLBACKS.get(topic, None)
        
        try:
            from langchain_core.messages import HumanMessage, SystemMessage
            resp = llm.invoke([
                SystemMessage(content=qa_system_prompt),
                HumanMessage(content=f"Context (use this to answer):\n{context}\n\nUser asked: {msg}"),
            ])
            return resp.content
        except Exception:
            # LLM failed — use smart static fallback instead of raw markdown
            return TOPIC_STATIC_FALLBACKS.get(topic, context[:600])
    
    return None  # Not a fast-path query, let the full agent handle it


@app.post("/api/chat")
async def chat_endpoint(req: ChatRequest):
    # Layer 0: Instant fast-path for greetings and one-word topics (zero agent overhead)
    fast = fast_path_reply(req.message)
    if fast:
        return {"reply": fast}

    # Layer 1: Full conversational agent (multi-turn, tool-calling)
    try:
        response = conversational_agent.invoke(
            {"input": req.message},
            config={"configurable": {"session_id": req.session_id}}
        )
        reply = response.get("output", "").strip()
        if reply:
            return {"reply": reply}
    except Exception as e:
        print(f"[Agent Error] {str(e)}")

    # Layer 2: Bare LLM with persona (no tools, still intelligent)
    try:
        from langchain_core.messages import HumanMessage, SystemMessage
        bare_response = llm.invoke([
            SystemMessage(content=qa_system_prompt),
            HumanMessage(content=req.message)
        ])
        return {"reply": bare_response.content}
    except Exception as e2:
        print(f"[LLM Fallback Error] {str(e2)}")

    # Layer 3: Try fuzzy fast-path as last resort before total fallback
    fuzzy_topic = _fuzzy_topic_match(req.message.strip().lower())
    if fuzzy_topic and fuzzy_topic != "__intro__" and fuzzy_topic in TOPIC_STATIC_FALLBACKS:
        return {"reply": TOPIC_STATIC_FALLBACKS[fuzzy_topic]}
    if fuzzy_topic == "__intro__":
        return {"reply": INTRO_REPLY}
    
    # Layer 4: Smart static fallback — chatbot will NEVER return nothing
    return {"reply": (
        "Hey! I'm Krishna's AI Twin. Here's what I can help you with:\n"
        "- **Projects** — Ask about any of my 48+ GitHub projects\n"
        "- **Skills** — Python, React, AI/ML, LangChain, and more\n"
        "- **Schedule** — Book a meeting with me on weekends!\n"
        "- **Background** — Education, internship, achievements\n\n"
        "Try asking: *'What are your best projects?'* or *'Tell me about yourself'*"
    )}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
