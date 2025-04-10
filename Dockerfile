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

# Копирование и установка прав для entrypoint скрипта
COPY ./entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Expose port 8000 for the Django app
EXPOSE 8000

ENTRYPOINT ["/entrypoint.sh"]

# Command to run the application using gunicorn
CMD ["gunicorn", "Rackito.wsgi:application", "--bind", "0.0.0.0:8000"] 