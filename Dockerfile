# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Install Node.js for building the frontend
RUN apt-get update && apt-get install -y nodejs npm && apt-get clean

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container at /app
COPY config/requirements.txt /app/

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application's code from the host to the container at /app
COPY . /app/

# Build the frontend
WORKDIR /app/frontend
RUN npm install
RUN npm run build
WORKDIR /app

# Run the application
CMD ["python", "src/main_production.py"]
