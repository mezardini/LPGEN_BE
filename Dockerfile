# Use the official Python image from the Docker Hub
FROM python:3.9-slim-buster

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set work directory
WORKDIR /code

# Copy project requirements
COPY requirements.txt /code/

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the project
COPY . /code/

# Run the application
ENTRYPOINT ["powershell.exe"]
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
