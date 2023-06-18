FROM python:3.9-slim-buster

# Set the working directory to /app
WORKDIR /app

# Copy the requirements file to the container
COPY requirements.txt .

# Install the required packages
RUN pip install -r requirements.txt

# Copy the rest of the application files to the container
COPY . .

# Expose port 5000 for the Flask app
EXPOSE 5000

ENTRYPOINT ["gunicorn", "app:app", "-w", "4", "-b", "0.0.0.0:5000"]
