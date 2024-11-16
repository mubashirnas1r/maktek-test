from fastapi import APIRouter, HTTPException, UploadFile, Cookie,File
from routers.models import ChatbotBase, PersonalityConfig, ChatbotMessage
from langchain_community.document_loaders import UnstructuredPDFLoader, TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from datetime import datetime
from typing import List
import os
import shutil
from routers.utils import (
    uuid4,
    CHATBOT_DIR,
    CONVERSATIONS_DIR,
    VECTOR_DB_DIR,
    LLM,
    Embedding_Function,
    list_folders,
    save_chatbot_data, 
    save_uploaded_file, 
    validate_session,
    load_json_data,
    save_conversation
)


router = APIRouter()

# Step 1: Create Chatbot Basic Info
@router.post("/v1/user/chatbots", tags=["Chatbots"])
async def create_chatbot(
    payload: ChatbotBase,
    session_id: str = Cookie(None)
):
    # Validate session
    if not session_id or not validate_session(session_id):
        raise HTTPException(status_code=403, detail="Session expired or invalid")
    
    # Fetch user ID from session
    session = load_json_data(f"database/sessions/{session_id}.json")
    user_id = session["user_id"]
    
    # Create chatbot ID and save
    chatbot_id = str(uuid4())
    chatbot_data = {
        "id": chatbot_id,
        "user_id": user_id,
        "name": payload.name,
        "description": payload.description,
        "created_at": datetime.utcnow().isoformat(),
        "system_prompt": None,
        "knowledge_base_files": []
    }
    save_chatbot_data(chatbot_id, chatbot_data)
    return {"message": "Chatbot created successfully", "chatbot_id": chatbot_id}

# Step 2: Configure Chatbot Personality
@router.post("/v1/user/chatbots/{chatbot_id}/personality", tags=["Chatbots"])
async def configure_personality(
    chatbot_id: str,
    payload: PersonalityConfig,
    session_id: str = Cookie(None)
):
    # Validate session
    if not session_id or not validate_session(session_id):
        raise HTTPException(status_code=403, detail="Session expired or invalid")
    
    # Load chatbot data
    chatbot_path = f"{CHATBOT_DIR}/{chatbot_id}.json"
    chatbot_data = load_json_data(chatbot_path)
    if not chatbot_data:
        raise HTTPException(status_code=404, detail="Chatbot not found")
    
    # Update system prompt
    chatbot_data["system_prompt"] = payload.system_prompt
    save_chatbot_data(chatbot_id, chatbot_data)
    return {"message": "Chatbot personality updated successfully"}

# Step 3: Upload Knowledge Base
@router.post("/v1/user/chatbots/{chatbot_id}/knowledge-base", tags=["Chatbots"])
async def upload_knowledge_base(
    chatbot_id: str,
    files: List[UploadFile] = File(...),
    session_id: str = Cookie(None)
):
    # Validate session
    if not session_id or not validate_session(session_id):
        raise HTTPException(status_code=403, detail="Session expired or invalid")
    
    # Intializing Text Splitter
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=4000, chunk_overlap=100)
    
    #Creating temp folder to save incomng file
    temp_folder = f"temp_{uuid4()}"
    os.makedirs(temp_folder, exist_ok=True)
    
    for file in files:
        # Validate file type
        if file.content_type not in ["application/pdf", "text/plain"]:
            raise HTTPException(
                status_code=400,
                detail=f"File '{file.filename}' is not a valid type. Only PDF and TXT files are allowed."
            )

        # Validate file size
        # Read file content to check size
        file_content = await file.read()
        if len(file_content) > 5 * 1024 * 1024:  # Max 5MB
            raise HTTPException(
                status_code=400,
                detail=f"File '{file.filename}' exceeds the 5MB limit."
            )
        
        # Save the file
        

        file_path =  f"{temp_folder}/{file.filename}"
        with open(file_path, 'wb') as f:
            f.write(file_content)
        
        if file.content_type == "application/pdf":
            documents = UnstructuredPDFLoader(file_path=file_path).load()  

        elif file.content_type == "text/plain":
            documents = TextLoader(file_path=file_path).load()

        
        document_chunks = text_splitter.split_documents(documents) 
        vector_store = FAISS.from_documents(documents=document_chunks, embedding=Embedding_Function)
        vector_store_id = str(uuid4())
        vector_store.add_documents(document_chunks)
        vector_store.save_local(f"{VECTOR_DB_DIR}/{chatbot_id}/{vector_store_id}")
        
        save_uploaded_file(chatbot_id, file.filename, vector_store_id)
    
    shutil.rmtree(temp_folder)
    return {"message": f"{len(files)} file(s) uploaded successfully"}

# Chat with AI
@router.post("/v1/user/chatbots/{chatbot_id}/conversations/{conversation_id}/chat", tags=["Chatbots"])
async def start_chat(
    chatbot_id: str,
    conversation_id: str,
    payload: ChatbotMessage,
    session_id: str = Cookie(None)
):
    # Validate session
    if not session_id or not validate_session(session_id):
        raise HTTPException(status_code=403, detail="Session expired or invalid")

    session = load_json_data(f"database/sessions/{session_id}.json")
    user_id = session["user_id"]

    # Load chatbot
    chatbot = load_json_data(f"{CHATBOT_DIR}/{chatbot_id}.json")
    if not chatbot:
        raise HTTPException(status_code=404, detail="Chatbot not found")
    user_message = {"message_id": str(uuid4()), "timestamp": datetime.utcnow().isoformat(),"role": "user", "content": payload.user_message}
    prev_messages = []

    # Load conversation
    conversation = load_json_data(f"{CONVERSATIONS_DIR}/{conversation_id}.json")
    if not conversation:
        conversation = []
    else:
        conversation = conversation["messages"]

    for message in conversation:
        if message["role"] == "user":
            prev_messages.append(
                (
                    "human",
                    message["content"],
                )
            )
        elif message["role"] == "assistant":
            prev_messages.append(
                (
                    "ai",
                    message["content"],
                )
            )
    
    prev_messages = [("system",chatbot["system_prompt"])] + prev_messages + [("human", payload.user_message)]


    knowledge_docs = ""
    found_knowledge = ""
    found_sources = []
    persist_directory = f'{VECTOR_DB_DIR}/{chatbot_id}'  # f'database/{page_type}'
    indexes = list_folders(persist_directory)
    print(indexes)
    if indexes != False:
        print("Found Indexes...")
        vector_db = FAISS.load_local(f'{persist_directory}/{indexes[0]}', Embedding_Function, allow_dangerous_deserialization=True)
        print("Merging Indexes..")
        for index in range(1, len(indexes)):
            new_persist_directory = f'{persist_directory}/{indexes[index]}'
            newVectordb = FAISS.load_local(new_persist_directory, Embedding_Function, allow_dangerous_deserialization=True)
            vector_db.merge_from(newVectordb)

        print("Searching for Questions in VectorDB...")
        retriever = vector_db.as_retriever(search_type="mmr")
        knowledge_docs = retriever.invoke(payload.user_message, k=3)

        print("Found Something...")
        found_knowledge = "Knowledge Docs: \n\n"
        
        for i, doc in enumerate(knowledge_docs):
            found_knowledge += str(f"{i + 1}. SOURCE: {doc.metadata['source'].split('/')[-1]} \n {doc.page_content}\n____\n")
            found_sources.append(doc.metadata['source'].split("/")[-1])

        user_message["content"] = found_knowledge + "\n" + user_message["content"]
    

    try:
        ai_msg = {"message_id": str(uuid4()), "timestamp": datetime.utcnow().isoformat(),"role": "assistant", "content": LLM.invoke(prev_messages).content, "sources": found_sources}
        new_messages = [user_message] + [ai_msg]
        save_conversation(conversation_id=conversation_id,chatbot_id=chatbot_id,user_id=user_id, messages=new_messages)

        return {
            "ai_message": ai_msg
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))