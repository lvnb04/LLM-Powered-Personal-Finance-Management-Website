# financial_chatbot.py (Using Hardcoded TEST_USER_ID from .env)
# Description: FastAPI backend for a financial chatbot using LangChain, Gemini, and Supabase.
# Uses a hardcoded User ID from .env for all database operations. 

# --- Core Libraries ---
import os
import re
import warnings
from dotenv import load_dotenv

# --- LangChain & AI ---
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits import SQLDatabaseToolkit
from langchain.agents import create_sql_agent, AgentExecutor

# --- Database ---
from sqlalchemy import create_engine

# --- Web Framework & Utils ---
import uvicorn
from fastapi import FastAPI, HTTPException # Removed Header import
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional

# --- Removed Supabase Auth ---
# from supabase import create_client, Client # No longer needed for auth

print("--- Chatbot API Server Loading (Hardcoded User Mode) ---")
print("Loading environment variables and libraries...")

# --- Environment Variable Loading ---
load_dotenv()

# --- Configuration ---
# Google AI
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
# Supabase Database (Using Pooler based on previous debugging)
SUPABASE_DB_PASSWORD = os.getenv("SUPABASE_DB_PASSWORD")
SUPABASE_DB_HOST = os.getenv("SUPABASE_DB_HOST") # Should be Pooler host
SUPABASE_DB_PORT = os.getenv("SUPABASE_DB_PORT", "6543") # Pooler port
SUPABASE_DB_USER = os.getenv("SUPABASE_DB_USER", "postgres")
SUPABASE_DB_NAME = os.getenv("SUPABASE_DB_NAME", "postgres")
# Hardcoded User ID for Testing
TEST_USER_ID = os.getenv("TEST_USER_ID") # Load the hardcoded User ID

# --- Critical Configuration Validation ---
# Removed SUPABASE_URL, SUPABASE_ANON_KEY from checks
required_env_vars = {
    "GOOGLE_API_KEY": GOOGLE_API_KEY,
    "SUPABASE_DB_PASSWORD": SUPABASE_DB_PASSWORD,
    "SUPABASE_DB_HOST": SUPABASE_DB_HOST,
    "TEST_USER_ID": TEST_USER_ID, # Added TEST_USER_ID check
}
missing_vars = [k for k, v in required_env_vars.items() if not v]
if missing_vars:
    print(f"❌ FATAL ERROR: Missing required environment variables: {', '.join(missing_vars)}")
    print("   Please ensure these are set in your .env file.")
    exit()

# Set Google API Key for LangChain libraries
os.environ["GOOGLE_API_KEY"] = GOOGLE_API_KEY

print("✅ Environment variables loaded.")
print(f"   Using DB: postgresql+psycopg2://{SUPABASE_DB_USER}:***@{SUPABASE_DB_HOST}:{SUPABASE_DB_PORT}/{SUPABASE_DB_NAME}")
print(f"❗ WARNING: Using hardcoded User ID for ALL requests: {TEST_USER_ID}")

# --- Global Variables for Initialized Components ---
llm: Optional[ChatGoogleGenerativeAI] = None
db: Optional[SQLDatabase] = None
toolkit: Optional[SQLDatabaseToolkit] = None
agent_executor: Optional[AgentExecutor] = None
# supabase_client: Optional[Client] = None # Removed Supabase client variable
_SQL_AGENT_SUFFIX: str = ""

# --- Initialization Block (Run Once on Startup) ---
try:
    # 1. Initialize LLM (No change)
    print("Initializing LLM (gemini-1.5-flash-latest)...")
    llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash-latest", temperature=0.1)
    print("✅ LLM Initialized.")

    # 2. Create Database Connection URI (No change)
    print("Creating DB Connection URI...")
    db_uri = f"postgresql+psycopg2://{SUPABASE_DB_USER}:{SUPABASE_DB_PASSWORD}@{SUPABASE_DB_HOST}:{SUPABASE_DB_PORT}/{SUPABASE_DB_NAME}"
    print("✅ DB URI Created.")

    # 3. Initialize LangChain SQLDatabase (No change)
    print("Connecting to Database via SQLAlchemy...")
    include_tables = ["profiles", "expense_categories", "expenses", "savings_goals"]
    db = SQLDatabase.from_uri(db_uri, include_tables=include_tables, sample_rows_in_table_info=2)
    print(f"✅ SQLDatabase connection established.")

    # 4. Define Agent Instructions (Suffix - Kept same as before, expecting prefix)
    # The agent logic will prepend the HARDCODED TEST_USER_ID to the input.
    print("Defining Agent Suffix/Instructions...")
    _SQL_AGENT_SUFFIX = """
TOOLS:
------
You have access to ONE tool named `sql_db_query` for querying the user's personal financial database. Use this tool ONLY as instructed below.

USER CONTEXT & SECURITY MANDATE (for SQL Tool):
-----------------------------------------------
The user's query about their personal data will be prefixed with 'UserID [USER_ID_UUID]:'.
**You MUST extract the USER_ID_UUID from the beginning of the input query.**
**You MUST use this extracted USER_ID_UUID to filter queries** on relevant tables:
Use `WHERE id = '[EXTRACTED_USER_ID_UUID]'` for `public.profiles`.
Use `WHERE user_id = '[EXTRACTED_USER_ID_UUID]'` for `public.expense_categories`, `public.expenses`, `public.savings_goals`.
**CRITICAL (SQL Tool): Do NOT query data for any other user_id.** If the UserID prefix is missing for a database query, state that you cannot proceed without user context.

*** TASK ROUTING & RESPONSE INSTRUCTIONS ***
--------------------------------------------
**1. Analyze the User's Query (the part AFTER the 'UserID [...]' prefix if present):** Determine the *type* of question:
    * **Type A: Personal Data Query:** Does it ask about the user's *specific* financial details stored in the database? These require using the `sql_db_query` tool.
    * **Type B: General Finance Question:** Is it a request for general financial knowledge, definitions, advice, tips, or explanations? These do **NOT** use the database tool.

**2. Execute Based on Type:**
    * **If Type A (Personal Data):**
        * Extract the USER_ID_UUID from the input prefix.
        * Use the `sql_db_query` tool.
        * Construct an accurate PostgreSQL query, ensuring you include the **mandatory filter using the extracted user ID**. Query only necessary columns.
        * Formulate your response based *only* on the data returned by the query. Handle errors gracefully.
    * **If Type B (General Finance):**
        * **DO NOT use the `sql_db_query` tool.**
        * Answer the question directly using your own extensive financial knowledge base.
        * **Keep your answer concise and focused, aiming for a maximum of 4 lines.**
        * DO NOT just say "I don't know".

**3. General Response Style:** Maintain a clear, encouraging, and advisory tone. Be accurate.
"""
    print("✅ Agent Suffix Defined (still expects UserID in input).")

    # 5. Create SQL Toolkit (No change)
    print("Creating SQL Toolkit...")
    toolkit = SQLDatabaseToolkit(db=db, llm=llm)
    print("✅ SQL Toolkit Created.")

    # 6. Create Agent Executor (No change)
    print("Creating Agent Executor ('tool-calling')...")
    agent_executor = create_sql_agent(
        llm=llm,
        toolkit=toolkit,
        verbose=True,
        agent_type="tool-calling",
        suffix=_SQL_AGENT_SUFFIX,
        handle_parsing_errors=True
    )
    print("✅ Agent Executor Created.")

except Exception as e:
    print(f"❌ FATAL ERROR during component initialization: {e}")
    # Set components to None to prevent server start
    llm = None
    db = None
    toolkit = None
    agent_executor = None
    # supabase_client = None # Removed

# --- FastAPI Application Setup ---
print("Setting up FastAPI application...")
app = FastAPI(
    title="Financial Chatbot API (Hardcoded User Mode)",
    description="API endpoint for the personal finance chatbot. WARNING: Uses a single hardcoded User ID for all requests.",
    version="1.0.0-test",
)

# CORS Configuration (No change)
origins = ["http://localhost", "http://localhost:3000", "http://localhost:5173", "http://localhost:8080"]
app.add_middleware(CORSMiddleware, allow_origins=origins, allow_credentials=True, allow_methods=["POST", "GET"], allow_headers=["*"])

# --- API Request/Response Models (No change) ---
class ChatRequest(BaseModel):
    query: str

class ChatResponse(BaseModel):
    response: str

# --- API Endpoints ---
@app.get("/")
async def root():
    """ Basic endpoint to check if the API is running. """
    return {"message": "Financial Chatbot API (Hardcoded User Mode) is running. Use the /chat endpoint (POST). No Auth needed."}

# MODIFIED: Removed Auth Header parameter and validation
@app.post("/chat", response_model=ChatResponse)
async def handle_chat(request: ChatRequest):
    """
    Handles chat requests. Uses HARDCODED TEST_USER_ID from .env file.
    Routes query to SQL agent (if prefixed with 'DB:') or General LLM.
    Returns the chatbot's response.
    """
    user_query = request.query
    print("-" * 50)
    print(f"Received request for /chat")
    print(f"Raw Query: {user_query}")
    print(f"❗ Acting as hardcoded User ID: {TEST_USER_ID}") # Log the user ID being used

    # Check if components initialized correctly on startup
    if not agent_executor or not llm:
         print("❌ ERROR: Chatbot components not initialized during startup.")
         raise HTTPException(status_code=503, detail="Chatbot service is not ready.")

    # --- Authentication REMOVED ---
    # No token validation needed in this version

    # --- Processing ---
    output = "An unexpected error occurred."
    try:
        # --- Manual Routing Logic ---
        if re.match(r"^\s*DB:", user_query, re.IGNORECASE):
            # --- Route to Database Agent ---
            print(f"   Routing to Database Agent (as user: {TEST_USER_ID})")
            db_query = re.sub(r"^\s*DB:", "", user_query, flags=re.IGNORECASE).strip()

            if not db_query:
                output = "Please provide a specific question about your data after 'DB:'."
            else:
                # --- Augment Input with HARDCODED UserID for the Agent ---
                # Uses TEST_USER_ID loaded from .env at startup
                augmented_input = f"UserID {TEST_USER_ID}: {db_query}"
                print(f"   Augmented agent input: \"{augmented_input}\"")
                agent_input = {"input": augmented_input}

                # Invoke the SQL agent asynchronously
                response = await agent_executor.ainvoke(agent_input)
                output = response.get('output', "Sorry, I couldn't retrieve or process the database information.")

        else:
            # --- Route to General LLM ---
            print("   Routing to General LLM for concise answer...")
            general_prompt = f"Answer the following financial question concisely, providing a helpful summary within a maximum of 4 lines:\n\nQuestion: {user_query}\n\nAnswer:"
            llm_response = await llm.ainvoke(general_prompt)

            if hasattr(llm_response, 'content'):
                output = llm_response.content
            else:
                output = str(llm_response)

    except Exception as e:
        print(f"❌ Error processing query (as user {TEST_USER_ID}): {e}")
        raise HTTPException(status_code=500, detail="An internal error occurred while processing your request.")

    # --- Return Response ---
    print(f"   Responding with (first 100 chars): {output[:100]}...")
    print("-" * 50)
    return ChatResponse(response=output)


# --- Main Execution Block ---
if __name__ == "__main__":
    # Check if all critical components were initialized successfully
    # Removed supabase_client check
    if llm and db and toolkit and agent_executor:
        print("✅ All components initialized successfully.")
        print("--- Starting FastAPI Server (Hardcoded User Mode) ---")
        uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
    else:
        print("❌ FastAPI server cannot start due to initialization errors. Please check logs.")
