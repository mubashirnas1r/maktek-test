import os
from fastapi import APIRouter, HTTPException, Cookie
from fastapi.responses import JSONResponse
from routers.utils import (
    CHATBOT_DIR,
    validate_session,
    load_json_data,
)

router = APIRouter()
@router.get("/v1/user/dashboard", tags=["Dashboard"])
async def get_dashboard_data(session_id: str = Cookie(None)):
    # Validate session
    print(session_id)
    if not session_id or not validate_session(session_id):
        raise HTTPException(status_code=403, detail="Session expired or invalid")
    
    # Fetch user ID from the session
    session = load_json_data(f"database/sessions/{session_id}.json")
    user_id = session["user_id"]

    # List all chatbots for the user
    chatbots = []
    for file in os.listdir(CHATBOT_DIR):
        chatbot_path = f"{CHATBOT_DIR}/{file}"
        chatbot = load_json_data(chatbot_path)
        if chatbot and chatbot["user_id"] == user_id:
            chatbots.append(chatbot)

    # Return chatbot list with quick stats
    return {
        "total_bots": len(chatbots),
        "chatbots": chatbots
    }