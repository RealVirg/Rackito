# Use an official Python runtime as a parent image
FROM python:3.9-slim-buster

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set work directory
WORKDIR /app

# Install dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . /app/

# Expose port 8000 for the Django app
EXPOSE 8000

# Command to run the application using gunicorn (will be overridden in docker-compose for development)
#CMD ["gunicorn", "Rackito.wsgi:application", "--bind", "0.0.0.0:8000"] 