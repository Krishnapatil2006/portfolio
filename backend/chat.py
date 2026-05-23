"""
Terminal chat interface for Krishna's AI Twin.
Uses the same hardened agent + RAG pipeline as main.py (FastAPI backend).
Run:  cd backend && python chat.py
"""

import os
import sys
import json
from datetime import datetime
from dotenv import load_dotenv

# --- SQLITE FIX (needed if pysqlite3 is installed, skip if not) ---
try:
    __import__('pysqlite3')
    sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')
except ImportError:
    pass

# Load env
load_dotenv(dotenv_path="../.env")
load_dotenv()

# Normalize API keys
gemini_key = os.getenv("Gemini_Api_Key") or os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
groq_key   = os.getenv("Groq_Api_Key")   or os.getenv("GROQ_API_KEY")
serp_key   = os.getenv("Serp_Api_Key")   or os.getenv("SERP_API_KEY") or os.getenv("SERPAPI_API_KEY")

os.environ["GOOGLE_API_KEY"]   = gemini_key.strip() if gemini_key else ""
os.environ["GROQ_API_KEY"]     = groq_key.strip()   if groq_key   else ""
os.environ["SERPAPI_API_KEY"]  = serp_key.strip()   if serp_key   else ""

# --- LangChain imports ---
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.tools import tool
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.chat_history import BaseChatMessageHistory

import requests

# ─── LLM ────────────────────────────────────────────────────────────────────
llm = ChatGroq(model="llama-3.1-8b-instant", temperature=0.3, max_tokens=1024)

# ─── RAG / Vector Store ──────────────────────────────────────────────────────
retriever = None
try:
    from langchain_chroma import Chroma
    from langchain_google_genai import GoogleGenerativeAIEmbeddings

    if not os.path.exists("./twin_chroma_db") or len(os.listdir("./twin_chroma_db")) == 0:
        print("[INFO] Chroma DB not found. Auto-building RAG database (this may take a moment)...")
        try:
            from rag_setup import build_rag
            build_rag()
        except Exception as build_err:
            print(f"   [WARN] Auto-build failed: {build_err}")

    embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
    vector_store = Chroma(
        persist_directory="./twin_chroma_db",
        collection_name="krishna_knowledge",
        embedding_function=embeddings
    )
    retriever = vector_store.as_retriever(search_kwargs={"k": 5})
    print("[OK] RAG (Chroma DB) connected successfully.")
except Exception as e:
    print(f"[WARN] RAG unavailable: {e}. Will use local knowledge_base.md fallback.")

# ─── TOOLS ───────────────────────────────────────────────────────────────────

@tool
def resume_knowledge_base(query: str = "") -> str:
    """Retrieve information about Krishna Patil's background, education, skills, projects, and experiences."""
    global retriever
    if not query:
        query = "Krishna Patil overview"

    if retriever is not None:
        try:
            docs = retriever.invoke(query)
            if docs:
                return "\n\n".join([d.page_content for d in docs])
        except Exception as e:
            print(f"   [RAG Error] {e}")

    # Fallback: read from all knowledge files directly
    fallback_files = [
        ("Projects_Info.md", ["project", "github", "repo", "mediai", "kirito", "floodguard",
                              "job recommend", "fake review", "fake news", "credit card",
                              "bashaconvert", "basha", "kiri", "echo", "jarvis", "student",
                              "iot", "game", "spotify", "elearning", "nlp",
                              "work", "built", "created", "developed"]),
        ("knowledge_base.md", []),
    ]
    try:
        query_lower = query.lower()
        chosen_file = "knowledge_base.md"
        for fname, keywords in fallback_files:
            if keywords and any(k in query_lower for k in keywords):
                if os.path.exists(fname):
                    chosen_file = fname
                    break

        with open(chosen_file, "r", encoding="utf-8") as f:
            content = f.read()

        if chosen_file == "Projects_Info.md":
            sections = content.split("\n### ")
            matched = []
            for sec in sections:
                title_line = sec.split("\n")[0].lower()
                if any(k in title_line for k in query_lower.split()) or \
                   any(k in query_lower for k in ["all", "best", "list", "project", "repo", "github"]):
                    matched.append("### " + sec)
            if matched:
                return "\n\n".join(matched[:5])
            return content[:4000]

        sections = content.split("\n## ")
        q = query_lower
        matched = []
        for i, sec in enumerate(sections):
            title = sec.split("\n")[0].lower()
            if any(k in q for k in ["project","work","experience","mediai","kirito","fake review","basha"]):
                if "project" in title or "work" in title: matched.append(("## "+sec) if i>0 else sec)
            elif any(k in q for k in ["hobby","interest","sport","game","music","badminton","anime","harry potter"]):
                if "interest" in title: matched.append(("## "+sec) if i>0 else sec)
            elif any(k in q for k in ["skill","tech","language","programming","expert"]):
                if "skill" in title: matched.append(("## "+sec) if i>0 else sec)
            elif any(k in q for k in ["contact","email","phone","linkedin","github"]):
                if "contact" in title: matched.append(("## "+sec) if i>0 else sec)
            elif any(k in q for k in ["schedul","availab","free","weekend","saturday","sunday","meeting","interview"]):
                if "schedul" in title or "availab" in title: matched.append(("## "+sec) if i>0 else sec)
        if matched:
            return "\n\n".join(matched)
        return "\n\n## ".join(sections[:4])
    except Exception:
        return "I am Krishna Patil, a passionate BCA student specializing in Computational Science from Pachora, Maharashtra. I have built 48+ projects including AI systems, web apps, games, and tools."


@tool
def get_free_slots(query: str = "") -> str:
    """Get Krishna's general availability and preferred meeting days."""
    return (
        "Krishna is available EVERY Saturday and Sunday for interviews, meetups, and calls. "
        "Morning (10:00–12:00) and afternoon (14:00–18:00) work best. "
        "For weekday meetings he can do after 5:00 PM. "
        "To book a slot, share your name, email, preferred date (Sat or Sun), and time."
    )


@tool
def schedule_meeting(date: str, time: str, name: str, email: str) -> str:
    """Schedule an interview, call, or meetup with Krishna. Krishna is always free on Sat & Sun.
    date: YYYY-MM-DD, time: HH:MM (24h), name: your name, email: your email."""
    meeting_file = "meetings.json"
    try:
        try:
            parsed_date = datetime.strptime(date, "%Y-%m-%d").date()
        except ValueError:
            return f"Invalid date '{date}'. Use YYYY-MM-DD (e.g. 2025-06-07)."
        try:
            datetime.strptime(time, "%H:%M")
        except ValueError:
            return f"Invalid time '{time}'. Use HH:MM (e.g. 10:30)."

        weekday  = parsed_date.weekday()
        day_name = parsed_date.strftime("%A")
        note = "" if weekday >= 5 else f" Note: {day_name} is a weekday — Krishna prefers Sat/Sun but is flexible."

        meetings = []
        if os.path.exists(meeting_file):
            with open(meeting_file, "r") as f:
                meetings = json.load(f)

        for m in meetings:
            if m["date"] == date and m["time"] == time:
                return f"That slot ({date} {time}) is already taken. Please pick another time.{note}"

        meetings.append({"date": date, "time": time, "name": name, "email": email})
        with open(meeting_file, "w") as f:
            json.dump(meetings, f, indent=4)
        return f"Done! Meeting booked with {name} on {date} ({day_name}) at {time}. Krishna will reach out to {email}.{note}"
    except Exception as e:
        return f"Failed to schedule meeting: {e}"


@tool
def check_schedule(date: str) -> str:
    """Check Krishna's availability for a specific date (YYYY-MM-DD). He is always free on weekends."""
    meeting_file = "meetings.json"
    try:
        try:
            parsed_date = datetime.strptime(date, "%Y-%m-%d").date()
        except ValueError:
            return f"Invalid date '{date}'. Use YYYY-MM-DD."

        weekday  = parsed_date.weekday()
        day_name = parsed_date.strftime("%A")
        is_weekend = weekday >= 5

        meetings = []
        if os.path.exists(meeting_file):
            with open(meeting_file, "r") as f:
                meetings = json.load(f)

        day_mtgs = [m for m in meetings if m["date"] == date]
        if not day_mtgs:
            return (f"Krishna is completely free on {date} ({day_name})! "
                    + ("Great day for an interview." if is_weekend else "He prefers Sat/Sun for meetings."))

        sched = "\n".join([f"  - {m['time']} with {m['name']}" for m in day_mtgs])
        return f"Krishna's bookings on {date} ({day_name}):\n{sched}\nHe may still have open slots — pick a different time!"
    except Exception as e:
        return f"Failed to check schedule: {e}"


@tool
def get_current_datetime(query: str = "") -> str:
    """Get the current date and time."""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


@tool
def calculator(expression: str = "") -> str:
    """Evaluate a safe math expression."""
    if not expression:
        return "No expression provided."
    try:
        if not all(c in "0123456789+-*/(). " for c in expression):
            return "Invalid characters in expression."
        return str(eval(expression))
    except Exception as e:
        return f"Error: {e}"


@tool
def get_weather(city: str = "") -> str:
    """Get current weather for a city."""
    api_key = os.getenv("WeatherStack_Api_Key", "")
    if not city:
        return "Please specify a city name."
    if not api_key:
        return f"Weather API key not configured. Assuming it's nice in {city}!"
    try:
        r = requests.get(f"http://api.weatherstack.com/current?access_key={api_key}&query={city}").json()
        if "current" in r:
            return f"{city}: {r['current']['weather_descriptions'][0]}, {r['current']['temperature']}°C"
        return "Could not fetch weather data."
    except Exception as e:
        return f"Weather fetch error: {e}"


tools = [
    resume_knowledge_base, get_free_slots,
    schedule_meeting, check_schedule, get_current_datetime,
    calculator, get_weather,
]

# ─── AGENT ───────────────────────────────────────────────────────────────────

SYSTEM_PROMPT = """You are the AI Twin of Krishna Chandrakant Patil — a real person, not a bot.
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

prompt = ChatPromptTemplate.from_messages([
    ("system", SYSTEM_PROMPT),
    MessagesPlaceholder("history"),
    ("human", "{input}"),
    MessagesPlaceholder("agent_scratchpad"),
])

agent = create_tool_calling_agent(llm, tools, prompt)
agent_executor = AgentExecutor(
    agent=agent, tools=tools, verbose=False,
    handle_parsing_errors=True, max_iterations=6,
)

store = {}

def get_session_history(session_id: str) -> BaseChatMessageHistory:
    if session_id not in store:
        store[session_id] = ChatMessageHistory()
    return store[session_id]

conversational_agent = RunnableWithMessageHistory(
    agent_executor, get_session_history,
    input_messages_key="input",
    history_messages_key="history",
)

# ─── TERMINAL CHAT LOOP ───────────────────────────────────────────────────────

def start_chat():
    print("\n" + "="*62)
    print("  Krishna's AI Twin  --  Terminal Chat")
    print("  Ask about skills, projects, availability, or anything!")
    print("  Type 'quit' or 'exit' to stop.")
    print("="*62 + "\n")

    session_id = "terminal_session"

    while True:
        try:
            user_input = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nKrishna's Twin: Goodbye! Feel free to reach out on LinkedIn anytime.")
            break

        if not user_input:
            continue
        if user_input.lower() in ("quit", "exit"):
            print("Krishna's Twin: Thanks for stopping by! Reach out via email or LinkedIn -- I'd love to chat more.")
            break

        # Layer 1: Full agent
        try:
            result = conversational_agent.invoke(
                {"input": user_input},
                config={"configurable": {"session_id": session_id}}
            )
            reply = result.get("output", "").strip()
            if reply:
                print(f"\nKrishna's Twin: {reply}\n")
                continue
        except Exception as e:
            print(f"   [agent error] {e}")

        # Layer 2: Bare LLM fallback
        try:
            from langchain_core.messages import HumanMessage, SystemMessage
            bare = llm.invoke([SystemMessage(content=SYSTEM_PROMPT), HumanMessage(content=user_input)])
            print(f"\nKrishna's Twin: {bare.content.strip()}\n")
            continue
        except Exception as e2:
            print(f"   [llm fallback error] {e2}")

        # Layer 3: Static fallback
        print("\nKrishna's Twin: Hey, I had a small glitch! Try asking again or ask about my projects/availability.\n")


if __name__ == "__main__":
    start_chat()
