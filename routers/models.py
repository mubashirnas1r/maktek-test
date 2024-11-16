from pydantic import BaseModel, Field
from typing import Optional, List, Literal
import re

class User(BaseModel):
    username: str = Field(..., min_length=3, max_length=50, pattern="^[a-zA-Z0-9_]+$")
    email: str = "user@email.com"
    password: str = Field(..., min_length=8)
    password_confirmation: str = Field(..., min_length=8)

    def validate_passwords_match(self):
        if self.password != self.password_confirmation:
            raise ValueError("Passwords do not match")
        
        # Check password strength
        password_regex = r'^(?=.*[A-Za-z])(?=.*\d)(?=.*[@$!%*?&#])[A-Za-z\d@$!%*?&#]{8,}$'
        if not re.match(password_regex, self.password):
            raise ValueError(
                "Password must be at least 8 characters long, "
                "include a number, and a special character"
            )
    def validate_email_format(self):
        email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_regex, self.email):
            raise ValueError("Invalid email format")


class ChatbotBase(BaseModel):
    name: str = Field(..., max_length=100)
    description: Optional[str] = None

class PersonalityConfig(BaseModel):
    system_prompt: str = Field(..., max_length=1000)

class KnowledgeBaseFile(BaseModel):
    file_name: str
    file_size: int

# class Message(BaseModel):
#     role: Literal["user", "assistant"]
#     content: str

class ChatbotMessage(BaseModel):
    user_message: str