from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI
from routers import (
    auth,
    dashboard,
    chatbots
)

app = FastAPI(
    title="Chatbot Creation Platfom Assesment",
    description="This is API Documentation for Chatbot Creation Platform.",
    version="1.0.0",
    docs_url="/docs"
)

origins = [
    "*"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"], 
)


app.include_router(auth.router)
app.include_router(dashboard.router)
app.include_router(chatbots.router)
