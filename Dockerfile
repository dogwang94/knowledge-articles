# Use the Python base image
FROM python:3.11.4-slim

# Set the working directory to /app
WORKDIR /app

# Install system dependencies required for psycopg2 and other packages
# RUN apt-get update && \
#     apt-get install -y libpq-dev gcc python3-dev && \
#     apt-get upgrade -y && \
#     rm -rf /var/lib/apt/lists/*

# Install system dependencies required for psycopg2 and other packages
RUN apt-get update && \
    apt-get install -y libpq-dev=15.3-0+deb12u1 gcc python3-dev && \ 
    apt-get upgrade -y && \
    rm -rf /var/lib/apt/lists/*



# Copy the requirements file to the container
# COPY requirements.txt .
COPY *.txt . 

# Install the required packages
RUN pip install -r psycopg2-binary.txt
# RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir --no-build-isolation -r requirements.txt

# Copy the rest of the application files to the container
COPY . .

# Expose port 5000 for the Flask app
EXPOSE 5000

# Define the entry point command
# ENTRYPOINT ["gunicorn", "app:app", "-w", "4", "-b", "0.0.0.0:5000"]
ENTRYPOINT ["gunicorn", "app.app:app", "-w", "4", "-b", "0.0.0.0:5000"]
