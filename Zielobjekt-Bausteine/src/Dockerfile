# Dockerfile
#
# This file defines the steps to build the Docker container image for the
# OSCAL generation pipeline.
#
# IMPORTANT: The build context for this Dockerfile is expected to be the
# application root directory ('Zielobjekt-Bausteine/src'), not the repository root.
# The 'deploy.sh' script handles changing to the correct directory before
# running 'docker build'.
#

# --- Base Image ---
# Use an official Python runtime as a parent image.
# Using a specific version ensures build reproducibility.
FROM python:3.9-slim

# --- Metadata ---
LABEL maintainer="Jules"
LABEL description="Container for the OSCAL Generation Pipeline."

# --- Environment ---
# Set the working directory in the container.
WORKDIR /app

# Set environment variables to prevent Python from writing .pyc files.
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# --- Dependencies ---
# Copy the dependency file first to leverage Docker's layer caching.
# This ensures that dependencies are only re-installed if requirements.txt changes.
COPY requirements.txt .

# Install the dependencies.
RUN pip install --no-cache-dir -r requirements.txt

# --- Application Code ---
# Copy the application source code into the container.
# These paths are relative to the build context, which is the application root.
COPY ./src ./src
COPY ./assets ./assets

# --- Execution ---
# Specify the command to run on container startup.
CMD ["python3", "src/main.py"]
