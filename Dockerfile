# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container at /app
COPY config/requirements.txt /app/

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Install node and npm
RUN apt-get update && apt-get install -y nodejs npm

# Copy the frontend package.json and package-lock.json
COPY frontend/package*.json /app/frontend/

# Install frontend dependencies
RUN npm install --prefix frontend

# Copy the rest of the application's code from the host to the container at /app
COPY . /app/

# Build the frontend
RUN npm run build --prefix frontend

# Run the application
CMD ["python", "src/main_production.py"]
