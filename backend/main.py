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
            
    # Fallback to smart local keyword-matching if Chroma failed or is empty (saves massive tokens)
    try:
        with open("knowledge_base.md", "r", encoding="utf-8") as f:
            content = f.read()
        
        # Split content by markdown section headers
        sections = content.split("\n## ")
        matching_sections = []
        
        query_lower = query.lower()
        for i, sec in enumerate(sections):
            sec_title = sec.split("\n")[0].lower()
            
            # Match keywords to return specific relevant sections
            if any(k in query_lower for k in ["project", "work", "experience", "mediai", "kirito", "job", "fake review", "basha"]):
                if "project" in sec_title or "work" in sec_title:
                    matching_sections.append("## " + sec if i > 0 else sec)
            elif any(k in query_lower for k in ["hobby", "interest", "sport", "game", "music", "badminton", "anime", "harry potter"]):
                if "interest" in sec_title:
                    matching_sections.append("## " + sec if i > 0 else sec)
            elif any(k in query_lower for k in ["skills", "expert", "tech", "languages", "programming"]):
                if "skills" in sec_title:
                    matching_sections.append("## " + sec if i > 0 else sec)
            elif any(k in query_lower for k in ["contact", "email", "phone", "social", "linkedin", "github"]):
                if "contact" in sec_title:
                    matching_sections.append("## " + sec if i > 0 else sec)
                    
        if matching_sections:
            return "\n\n".join(matching_sections)
            
        # Default to first 3 sections (Background + Skills + Contact) if no specific keywords matched
        # sections[0] is the main title, sections[1] is Section 1 (Personal Identity), etc.
        return "\n\n## ".join(sections[:4])
    except Exception as e:
        return "I am Krishna Patil, a passionate BCA student specializing in Computational Science from Pachora, Maharashtra."

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
You speak exactly like him: confident, casual, and direct. You are a 3rd-year BCA student specializing
in Computational Science from Pachora, Maharashtra, India. You are talking to a recruiter or portfolio visitor.

CRITICAL RULES:
1. Be SHORT and DIRECT. One or two sentences max unless asked for detail.
2. Handle typos, misspellings, and indirect questions gracefully — always infer intent and respond helpfully.
3. Never say you are an AI, bot, or language model. You ARE Krishna.
4. For ANY question about yourself, skills, projects, or background — use the 'resume_knowledge_base' tool FIRST.
5. For scheduling/availability: Krishna is FREE every Saturday and Sunday for interviews, calls, and meetups.
   - Use 'get_free_slots' if someone asks when he is free.
   - Use 'check_schedule' then 'schedule_meeting' to book a slot.
   - Use 'get_current_datetime' to determine today's date if needed.
6. For nonsensical or totally off-topic questions, gently redirect: "That's a fun one! But let's keep it focused — want to know about my projects or skills?"
7. If a tool fails, answer from memory or ask for clarification. NEVER crash or show errors to the user.
8. Speak in first person always: "I built...", "I'm currently...", "My project..."
9. Keep it natural — avoid unnecessary markdown like **bold** or bullet lists in short replies.
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

@app.post("/api/chat")
async def chat_endpoint(req: ChatRequest):
    # Layer 1: Try the full conversational agent
    try:
        response = conversational_agent.invoke(
            {"input": req.message},
            config={"configurable": {"session_id": req.session_id}}
        )
        reply = response.get("output", "")
        if reply:
            return {"reply": reply}
    except Exception as e:
        print(f"[Agent Error] {str(e)}")

    # Layer 2: Try the bare LLM with the system persona (no tools)
    try:
        from langchain_core.messages import HumanMessage, SystemMessage
        bare_response = llm.invoke([
            SystemMessage(content=qa_system_prompt),
            HumanMessage(content=req.message)
        ])
        return {"reply": bare_response.content}
    except Exception as e2:
        print(f"[LLM Fallback Error] {str(e2)}")

    # Layer 3: Static safe fallback — the chatbot will NEVER return nothing
    return {"reply": "Hey! I'm having a tiny technical moment. Could you ask me again, or try asking about my projects, skills, or availability for a meetup?"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
