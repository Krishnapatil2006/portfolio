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

# Map the .env keys to what LangChain expects if they differ
# AND provide fallback dummy keys so the app doesn't crash at startup if missing!
os.environ["GOOGLE_API_KEY"] = os.getenv("Gemini_Api_Key", os.getenv("GOOGLE_API_KEY", "dummy_google_key"))
os.environ["GROQ_API_KEY"] = os.getenv("Groq_Api_Key", os.getenv("GROQ_API_KEY", "dummy_groq_key"))
os.environ["SERPAPI_API_KEY"] = os.getenv("Serp_Api_Key", os.getenv("SERPAPI_API_KEY", "dummy_serp_key"))

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

llm = ChatGroq(
    model="llama-3.1-8b-instant",  
    temperature=0.3,
    max_tokens=1024,
)

# --- Tools Setup ---
def create_rag_tool():
    try:
        embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
        vector_store = Chroma(
            persist_directory="./twin_chroma_db",
            collection_name="krishna_knowledge",
            embedding_function=embeddings
        )
        retriever = vector_store.as_retriever(search_kwargs={"k": 5})
        
        @tool
        def resume_knowledge_base(query: str) -> str:
            """Use this tool to answer questions about Krishna Patil's personal background, education, skills, projects, and experiences."""
            docs = retriever.invoke(query)
            context = "\n".join([d.page_content for d in docs])
            prompt = f"Answer the following question based only on the provided context:\n\n<context>\n{context}\n</context>\n\nQuestion: {query}"
            response = llm.invoke(prompt)
            return response.content
        return resume_knowledge_base
    except Exception as e:
        print(f"Failed to initialize Chroma DB with Google Embeddings: {e}")
        @tool
        def resume_knowledge_base(query: str) -> str:
            """Use this tool to answer questions about Krishna Patil's personal background, education, skills, projects, and experiences."""
            try:
                with open("knowledge_base.md", "r", encoding="utf-8") as f:
                    return f.read()
            except:
                return "I am Krishna Patil, a passionate BCA student."
        return resume_knowledge_base

resume_tool = create_rag_tool()

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
def get_current_datetime() -> str:
    """Get the current date and time."""
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

tools = [resume_tool, web_search, calculator, get_weather, get_current_datetime, schedule_meeting, check_schedule]

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
        return {"error": str(e)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
