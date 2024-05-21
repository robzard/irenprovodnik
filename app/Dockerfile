# Use the official Python image as a base image
FROM python:3.10-slim

# Set the working directory in the container
WORKDIR /app

# Install Gunicorn
RUN pip install gunicorn
RUN apt-get update && apt-get install -y curl
RUN apt-get update && apt-get install -y libpq-dev


# Copy the requirements file into the container at /app
COPY requirements.txt /app

# Install any needed packages specified in requirements.txt
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy the rest of the application code into the container at /app
COPY . /app

# Make port 5000 available to the world outside this container
EXPOSE 5000

# Создайте символическую ссылку для common
RUN ln -s /common /app/common

ENV PYTHONPATH="/app:/common"

# Define environment variable
ENV FLASK_ENV=production
