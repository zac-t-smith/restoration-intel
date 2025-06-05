# Base Python image
FROM python:3.11-slim

WORKDIR /app

# Install build tools needed to compile pmdarima
RUN apt-get update && apt-get install -y build-essential gfortran libatlas-base-dev

# Install numpy first (as it's needed for pmdarima)
RUN pip install --upgrade pip && pip install numpy==1.23.5

# Copy requirements and install the rest
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
