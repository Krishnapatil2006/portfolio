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
from datetime import datetime
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

    embeddings = GoogleGenerativeAIEmbeddings(model="text-embedding-004")
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
def resume_knowledge_base(query: str) -> str:
    """Use this tool to retrieve information about Krishna Patil's personal background, education, skills, projects, and experiences."""
    global retriever
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
def calculator(expression: str) -> str:
    """Evaluate a mathematical expression. Use this tool for any math-related queries."""
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
    """Schedule a meeting or meetup with Krishna.
    Provide date (YYYY-MM-DD), time (HH:MM), name, and email of the person.
    """
    meeting_file = "meetings.json"
    new_meeting = {"date": date, "time": time, "name": name, "email": email}
    
    try:
        if os.path.exists(meeting_file):
            with open(meeting_file, "r") as f:
                meetings = json.load(f)
        else:
            meetings = []
            
        # Check for conflicts
        for m in meetings:
            if m["date"] == date and m["time"] == time:
                return f"Sorry, Krishna already has a meeting scheduled on {date} at {time}."
                
        meetings.append(new_meeting)
        with open(meeting_file, "w") as f:
            json.dump(meetings, f, indent=4)
        return f"Meeting successfully scheduled with {name} on {date} at {time}. Krishna will reach out to {email} to confirm."
    except Exception as e:
        return f"Failed to schedule meeting: {str(e)}"

@tool
def check_schedule(date: str) -> str:
    """Check Krishna's schedule and free days for a specific date (YYYY-MM-DD)."""
    meeting_file = "meetings.json"
    try:
        if not os.path.exists(meeting_file):
            return f"Krishna is completely free on {date}!"
            
        with open(meeting_file, "r") as f:
            meetings = json.load(f)
            
        day_meetings = [m for m in meetings if m["date"] == date]
        if not day_meetings:
            return f"Krishna is completely free on {date}!"
            
        schedule = "\n".join([f"- {m['time']} with {m['name']}" for m in day_meetings])
        return f"Krishna's schedule on {date}:\n{schedule}"
    except Exception as e:
        return f"Failed to check schedule: {str(e)}"

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

tools = [resume_knowledge_base, web_search, calculator, get_weather, get_current_datetime, schedule_meeting, check_schedule]

# --- Agent Setup ---
qa_system_prompt = """You are the AI Twin of Krishna Chandrakant Patil. You act, speak, and respond exactly like him. 
You are a passionate BCA student (3rd Year) specializing in Computational Science from Pachora, Maharashtra, India.
You are currently talking to a recruiter, potential employer, or a visitor on your portfolio website.

CRITICAL INSTRUCTION: Keep your responses extremely short, direct, and concise, just like a real casual conversation or a text message. 
Do NOT give long answers unless explicitly asked for details. If the user asks a small question, give a one or two sentence answer max. 

Use your tools to answer questions accurately.
If asked about yourself, your skills, or projects, ALWAYS use the 'resume_knowledge_base' tool.
If a recruiter wants to schedule a meetup or meeting, use 'check_schedule' and 'schedule_meeting'. Use 'get_current_datetime' if you need the current date.
Always speak in the first person ("I am Krishna", "I built this").
Avoid markdown formatting like **bold** when unnecessary, keep it natural.
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
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

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
    try:
        response = conversational_agent.invoke(
            {"input": req.message},
            config={"configurable": {"session_id": req.session_id}}
        )
        return {"reply": response["output"]}
    except Exception as e:
        return {"reply": f"Backend Error: {str(e)}"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
