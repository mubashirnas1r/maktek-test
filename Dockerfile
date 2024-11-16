# Use the official Python 3.11 image as the base image
FROM python:3.10-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file to the container
COPY requirements.txt .

# Install Python dependencies
RUN pip install -r requirements.txt --upgrade

# Copy the rest of the application code to the container
COPY . .

# Expose the FastAPI default port
EXPOSE 8000

# Command to run the FastAPI application using Uvicorn
CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000"]
