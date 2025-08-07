# Multi-stage build
# Stage 1: Build frontend
FROM node:18-alpine as frontend-builder

WORKDIR /app

# Copy package files first for better caching
COPY package*.json ./
COPY vite.config.js ./
COPY index.html ./

# Install dependencies
RUN npm install

# Set production environment variables for build
ENV VITE_API_BASE_URL=https://lane-google.onrender.com
ENV VITE_APP_NAME="Lane AI"
ENV VITE_APP_VERSION="2.0.0"
ENV VITE_ENVIRONMENT=production

# Copy source files
COPY src ./src

# Build the frontend (output will be in src/static)
RUN npm run build

# Stage 2: Python application
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container at /app
COPY requirements.txt /app/

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application's code from the host to the container at /app
COPY . /app/

# Copy built frontend from the frontend-builder stage
COPY --from=frontend-builder /app/src/static /app/src/static

# Run the application (fixed build issue)
CMD ["python", "src/main_production.py"]
