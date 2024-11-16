# Chatbot Creation Platform Assessment

This repository contains the source code for the **Chatbot Creation Platform Assessment**, a FastAPI-based project designed to handle chatbot creation and management.

## Project Overview

- **Title:** Chatbot Creation Platform Assessment
- **Description:** This is API Documentation for Chatbot Creation Platform.
- **Version:** 1.0.0
- **Documentation URL:** `/docs`

## Features

- User authentication and management
- Chatbot creation and deployment
- Session and conversation tracking
- Integration with VectorDB for data storage
- Dashboard functionalities

## Directory Structure

```plaintext
├── database/                # Database models and interactions
│   ├── chatbots/            # Data storage related to chatbots
│   ├── conversations/       # Conversation tracking
│   ├── sessions/            # Session management
│   ├── users/               # User management
│   └── VectorDB/            # Integration with vector databases
├── routers/                 # API route handlers
│   ├── auth.py              # Authentication endpoints
│   ├── chatbots.py          # Chatbot management endpoints
│   ├── dashboard.py         # Dashboard-related endpoints
│   ├── models.py            # Data models
│   ├── utils.py             # Utility functions
│   └── __pycache__/         # Compiled Python files
├── .env                     # Environment variables (not tracked in Git)
├── .gitignore               # Git ignore rules
├── api.py                   # Entry point for the FastAPI application
├── Dockerfile               # Docker configuration for containerization
├── README.md                # Project documentation
├── requirements.txt         # Python dependencies
```

## Prerequisites

Before running the application, ensure you have the following installed:

- Python 3.10 or higher
- Docker (if running the application inside a container)
- `pip` (Python package manager)

## Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/mubashirnas1r/maktek-test.git
   cd chatbot-platform
   ```

2. Create a virtual environment and activate it:

   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. Create a `.env` file to store environment variables. Use the following format:

   ```env
   GOOGLE_API_KEY= YOUR-KEY
   ```

## Running the Application

1. Start the FastAPI application:

   ```bash
   uvicorn api:app --reload
   ```

   By default, the app will run on `http://127.0.0.1:8000`.

2. Access the API documentation at:

   ```
   http://127.0.0.1:8000/docs
   ```

## Running with Docker

1. Build the Docker image:

   ```bash
   docker build -t chatbot-platform .
   ```

2. Run the Docker container:

   ```bash
   docker run -d -p 8000:8000 --env-file .env chatbot-platform
   ```

3. Access the API at:

   ```
   http://localhost:8000/docs
   ```