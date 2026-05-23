# --- CRITICAL RENDER FIX FOR CHROMA DB ---
__import__('pysqlite3')
import sys
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')
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
    "helo": "Hello! I'm Krishna Patil's AI Twin. What can I help you with?",
    "sup": "Hey! Ready to chat. Ask me about my skills, projects, or when we can meet!",
    "ok": "Sure! What else would you like to know?",
    "okay": "Sure! What else would you like to know?",
    "thanks": "Happy to help! Anything else you'd like to know about Krishna?",
    "thank you": "You're welcome! Feel free to ask about projects, skills, or scheduling a call!",
    "bye": "Thanks for stopping by! Reach out anytime on LinkedIn or email. Goodbye!",
    "goodbye": "Thanks for visiting! Feel free to connect on LinkedIn. Goodbye!",
}

# One-word topic triggers — fetch context immediately and skip agent tool loop
TOPIC_KEYWORDS = {
    "projects":   "projects",
    "project":    "projects",
    "proejcts":   "projects",
    "projcts":    "projects",
    "porjects":   "projects",
    "skills":     "skills",
    "skill":      "skills",
    "skils":      "skills",
    "tech":       "skills",
    "stack":      "skills",
    "contact":    "contact",
    "email":      "contact",
    "linkedin":   "contact",
    "github":     "contact",
    "links":      "contact",
    "portfolio":  "contact",
    "schedule":   "schedule",
    "meeting":    "schedule",
    "meetup":     "schedule",
    "available":  "schedule",
    "free":       "schedule",
    "saturday":   "schedule",
    "sunday":     "schedule",
    "education":  "education",
    "college":    "education",
    "bca":        "education",
    "degree":     "education",
    "experience": "experience",
    "internship": "experience",
    "intern":     "experience",
    "work":       "experience",
    "hobbies":    "hobbies",
    "hobby":      "hobbies",
    "interests":  "hobbies",
    "sports":     "hobbies",
    "badminton":  "hobbies",
    "gaming":     "hobbies",
    "anime":      "hobbies",
}

TOPIC_CONTEXT = {
    "projects":   "give me full details of all my GitHub projects",
    "skills":     "what are Krishna's technical skills and expertise",
    "contact":    "what are Krishna's contact details, portfolio links, LinkedIn, GitHub",
    "schedule":   "what is Krishna's availability for meetings and interviews",
    "education":  "what is Krishna's educational background and qualifications",
    "experience": "what is Krishna's work experience and internships",
    "hobbies":    "what are Krishna's hobbies, interests and personal life",
}

def fast_path_reply(msg: str):
    """Returns an instant reply for simple/short queries, or None to proceed to the full agent."""
    clean = msg.strip().lower().rstrip("!?.,")

    # Exact match for greetings
    if clean in INSTANT_REPLIES:
        return INSTANT_REPLIES[clean]

    # Single-word or very short (<=2 words) topic queries
    words = clean.split()
    if len(words) <= 2:
        for word in words:
            if word in TOPIC_KEYWORDS:
                topic = TOPIC_KEYWORDS[word]
                # Pre-fetch context and do a bare LLM call — no tool round-trip
                context = resume_knowledge_base.func(TOPIC_CONTEXT[topic])
                try:
                    from langchain_core.messages import HumanMessage, SystemMessage
                    resp = llm.invoke([
                        SystemMessage(content=qa_system_prompt),
                        HumanMessage(content=f"Context:\n{context}\n\nQuestion: {msg}"),
                    ])
                    return resp.content
                except Exception:
                    return context[:800]  # Return raw context if LLM fails
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

    # Layer 3: Static safe fallback — chatbot will NEVER return nothing
    return {"reply": "Hey! I'm having a tiny moment. Could you ask again, or try asking about my projects, skills, or when we can meet?"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
