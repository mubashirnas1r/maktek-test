import os
import time
import json
import hashlib
from uuid import uuid4
from datetime import datetime
# from langchain_community.embeddings import HuggingFaceBgeEmbeddings
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from dotenv import load_dotenv
import nltk

nltk.download('punkt_tab')
nltk.download('averaged_perceptron_tagger_eng')

load_dotenv()

BASE_USER_DIR = "database/users"
CHATBOT_DIR = "database/chatbots"
BASE_SESSION_DIR = "database/sessions"
CONVERSATIONS_DIR = "database/conversations"
VECTOR_DB_DIR = "database/VectorDB"

SESSION_TIMEOUT = 24 * 60 * 60

os.makedirs(BASE_USER_DIR, exist_ok=True)
os.makedirs(BASE_SESSION_DIR, exist_ok=True)
os.makedirs(CHATBOT_DIR, exist_ok=True)
os.makedirs(CONVERSATIONS_DIR, exist_ok=True)
os.makedirs(VECTOR_DB_DIR, exist_ok=True)

# Loading embedding model
# EMBEDDING_MODEL_NAME  = "./BAAI_bge-small-en"
# EMBEDDING_MODEL_KWARGS = {"device": "cpu"}
# EMBEDDING_MODEL_ENCODE_KWARGS = {"normalize_embeddings": True}
# Embedding_Function = HuggingFaceBgeEmbeddings(
#     model_name=EMBEDDING_MODEL_NAME, model_kwargs=EMBEDDING_MODEL_KWARGS, encode_kwargs=EMBEDDING_MODEL_ENCODE_KWARGS
# )

Embedding_Function = GoogleGenerativeAIEmbeddings(model="models/embedding-001")

LLM = ChatGoogleGenerativeAI(
    model="gemini-1.5-pro",
    temperature=0,
    max_tokens=None,
    timeout=None,
    max_retries=2,
 
)
# Utility to hash password
def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def save_user_data(user_id: str, data: dict) -> None:
    with open(f"{BASE_USER_DIR}/{user_id}.json", "w") as file:
        json.dump(data, file,indent = 4)

def is_username_taken(username: str) -> bool:
    for file in os.listdir(BASE_USER_DIR):
        with open(f"{BASE_USER_DIR}/{file}", "r") as f:
            user = json.load(f)
            if user["username"] == username:
                return True
    return False

def list_folders(directory_path):
    try:
        folder_names = [folder for folder in os.listdir(directory_path) if os.path.isdir(os.path.join(directory_path, folder))]
        if folder_names == []:
            return False
        return folder_names
    except FileNotFoundError:
        print(f"The directory '{directory_path}' does not exist.")
        return False
    
# Save JSON data to a file
def save_json_data(file_path: str, data: dict) -> None:
    with open(file_path, "w") as file:
        json.dump(data, file,indent = 4)


# Load JSON data from a file
def load_json_data(file_path: str) -> dict:
    if os.path.exists(file_path):
        with open(file_path, "r") as file:
            return json.load(file)
    return None


# Check if username or email exists
def find_user_by_credentials(username_or_email: str, password: str) -> dict:
    for file in os.listdir(BASE_USER_DIR):
        user_path = f"{BASE_USER_DIR}/{file}"
        user = load_json_data(user_path)
        if user and (
            (user["username"] == username_or_email or user["email"] == username_or_email)
            and user["password"] == hash_password(password)
        ):
            return user
    return None


# Create a session file
def create_session(user_id: str, remember_me: bool) -> dict:
    session_id = str(uuid4())
    expiration = None if remember_me else int(time.time()) + SESSION_TIMEOUT
    session_data = {
        "user_id": user_id,
        "session_id": session_id,
        "created_at": int(time.time()),
        "expires_at": expiration,
    }
    save_json_data(f"{BASE_SESSION_DIR}/{session_id}.json", session_data)
    return session_data


# Validate session
def validate_session(session_id: str) -> bool:
    session_path = f"{BASE_SESSION_DIR}/{session_id}.json"
    session = load_json_data(session_path)
    if session:
        if session["expires_at"] is None or session["expires_at"] > int(time.time()):
            return True
    return False

def save_chatbot_data(chatbot_id: str, data: dict):

    with open(f"{CHATBOT_DIR}/{chatbot_id}.json", "w") as file:
        json.dump(data, file,indent = 4)

def save_uploaded_file(chatbot_id: str, file_name: str, vector_store_id:str):
    # Load the existing chatbot data
    chatbot_path = f"{CHATBOT_DIR}/{chatbot_id}.json"
    if os.path.exists(chatbot_path):
        with open(chatbot_path, "r") as file:
            chatbot_data = json.load(file)
    
    
    # Append the file data to the knowledge_base attribute
    chatbot_data["knowledge_base_files"].append({
        "file_name": file_name,
        "vector_store_id": vector_store_id
    })
    
    # Save updated chatbot data
    save_chatbot_data(chatbot_id, chatbot_data)

def save_conversation(conversation_id: str, chatbot_id:str, user_id: str, messages: list):

    
    conversation_path = f"{CONVERSATIONS_DIR}/{conversation_id}.json"
    
    # Load existing conversation or initialize a new one
    if os.path.exists(conversation_path):
        with open(conversation_path, "r") as file:
            conversation_data = json.load(file)
    else:
        conversation_data = {
            "user_id": user_id,
            "conversation_id": conversation_id,
            "chatbot_id": chatbot_id,
            "created_at": datetime.utcnow().isoformat(),
            "messages": []
        }
    
    # Append new conversation entry
    conversation_data["messages"] += messages

    # Save updated conversation
    with open(conversation_path, "w") as file:
        json.dump(conversation_data, file, indent=4)