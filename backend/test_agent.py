import os
from dotenv import load_dotenv

# Run the imports just like main.py
try:
    __import__('pysqlite3')
    import sys
    sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')
except ImportError:
    pass

load_dotenv(dotenv_path="../.env")
load_dotenv()

# Map keys
os.environ["GOOGLE_API_KEY"] = os.getenv("Gemini_Api_Key", os.getenv("GOOGLE_API_KEY", ""))
os.environ["GROQ_API_KEY"] = os.getenv("Groq_Api_Key", os.getenv("GROQ_API_KEY", ""))
os.environ["SERPAPI_API_KEY"] = os.getenv("Serp_Api_Key", os.getenv("SERPAPI_API_KEY", ""))

from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_chroma import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.tools import tool
from langchain_community.utilities import SerpAPIWrapper

llm = ChatGroq(
    model="llama-3.1-8b-instant",  
    temperature=0.3,
    max_tokens=1024,
)

@tool
def dummy_tool(query: str) -> str:
    """A dummy tool."""
    return "Dummy"

tools = [dummy_tool]

qa_system_prompt = "You are a helpful assistant."
prompt = ChatPromptTemplate.from_messages(
    [
        ("system", qa_system_prompt),
        MessagesPlaceholder("history"),
        ("human", "{input}"),
        MessagesPlaceholder("agent_scratchpad"),
    ]
)

try:
    agent = create_tool_calling_agent(llm, tools, prompt)
    agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)
    print("Agent executor successfully created!")
    
    # Try calling the agent
    response = agent_executor.invoke({"input": "Hello", "history": []})
    print("Response:", response)
except Exception as e:
    import traceback
    print("Error occurred:")
    traceback.print_exc()
