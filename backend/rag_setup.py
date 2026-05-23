import os
from dotenv import load_dotenv
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_chroma import Chroma

# Load env variables
load_dotenv(dotenv_path="../.env")
load_dotenv()

# Files to index into the RAG vector DB
KNOWLEDGE_FILES = [
    "knowledge_base.md",       # Main personal info, skills, scheduling
    "Projects_Info.md",        # Deep project analysis for all 48 GitHub repos
    "chatbot_details.md",      # Technical twin documentation
    "resume_text.txt",         # Raw resume content
]

def build_rag():
    all_docs = []

    for fname in KNOWLEDGE_FILES:
        if not os.path.exists(fname):
            print(f"  [SKIP] {fname} not found, skipping.")
            continue
        print(f"  [LOAD] Loading {fname}...")
        try:
            loader = TextLoader(fname, encoding="utf-8")
            docs = loader.load()
            all_docs.extend(docs)
            print(f"         -> {len(docs)} document(s) loaded.")
        except Exception as e:
            print(f"  [WARN] Failed to load {fname}: {e}")

    if not all_docs:
        print("[ERROR] No documents loaded. Aborting RAG build.")
        return

    print(f"\nTotal documents loaded: {len(all_docs)}. Splitting into chunks...")
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=100,
        separators=["\n## ", "\n### ", "\n\n", "\n", " ", ""]
    )
    splits = text_splitter.split_documents(all_docs)
    print(f"Total chunks created: {len(splits)}")

    print("\nGenerating Google embeddings and storing in Chroma DB...")
    gemini_key = os.getenv("Gemini_Api_Key") or os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    if not gemini_key:
        print("[ERROR] No Gemini/Google API key found. Cannot build embeddings.")
        return
    os.environ["GOOGLE_API_KEY"] = gemini_key.strip()

    embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")

    # Wipe old DB and rebuild fresh so no stale vectors remain
    import shutil
    if os.path.exists("./twin_chroma_db"):
        shutil.rmtree("./twin_chroma_db")
        print("Old Chroma DB wiped. Rebuilding from scratch...")

    vector_store = Chroma.from_documents(
        documents=splits,
        embedding=embeddings,
        persist_directory="./twin_chroma_db",
        collection_name="krishna_knowledge"
    )

    print(f"\n[SUCCESS] RAG database built at './twin_chroma_db' with {len(splits)} chunks from {len(all_docs)} docs!")

if __name__ == "__main__":
    build_rag()
