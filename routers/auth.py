from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from routers.models import User
from routers.utils import (
    uuid4,
    find_user_by_credentials,
    create_session,
    validate_session,
    load_json_data,
    is_username_taken,
    hash_password,
    save_user_data,
    save_json_data
)

router = APIRouter()

@router.post("/v1/user/register", tags=["Authorization"])
async def register_user(user: User):
    
    # Validate email format
    try:
        user.validate_email_format()
        user.validate_passwords_match()
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    # Check for duplicate username
    if is_username_taken(user.username):
        raise HTTPException(status_code=400, detail="Username already taken")
    
    # Hash the password and save the user
    user_id = str(uuid4())
    user_data = {
        "id": user_id,
        "username": user.username,
        "email": user.email,
        "password": hash_password(user.password),
    }
    save_user_data(user_id, user_data)
    return {"message": "User registered successfully", "user_id": user_id}

@router.post("/v1/user/login", tags=["Authorization"])
async def login_user(username_or_email: str, password: str, remember_me: bool = False):
    # Check credentials
    user = find_user_by_credentials(username_or_email, password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    # Create session
    session_data = create_session(user["id"], remember_me)
    response = JSONResponse(
        content={"message": "Login successful", "session_id": session_data["session_id"]}
    )
    response.set_cookie(key="session_id", value=session_data["session_id"], httponly=True)
    return response
