# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container at /app
COPY config/requirements.txt /app/

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application's code from the host to the container at /app
COPY . /app/

# Create a placeholder for the frontend build
RUN mkdir -p /app/src/static && \
    echo '<!DOCTYPE html><html><head><title>Lane MCP</title></head><body><h1>Frontend not built</h1><p>The frontend needs to be built separately.</p></body></html>' > /app/src/static/index.html

# Run the application
CMD ["python", "src/main_production.py"]
