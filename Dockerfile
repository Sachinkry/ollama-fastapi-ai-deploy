# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set environment variables
# Prevents Python from writing pyc files to disc
ENV PYTHONDONTWRITEBYTECODE 1
# Ensures Python output is sent straight to the terminal without buffering
ENV PYTHONUNBUFFERED 1
# Set the python path to include the project root
ENV PYTHONPATH=.

# Set the working directory in the container
WORKDIR /app

# Install dependencies
# Copy the requirements file first to leverage Docker cache
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code into the container
COPY ./app /app/app

# The command to run the application will be specified in docker-compose.yml
