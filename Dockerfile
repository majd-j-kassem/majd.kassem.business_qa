# Use the official Selenium standalone Chrome image as the base
FROM selenium/standalone-chrome:4.20.0-20240520

# Switch to the root user temporarily to install dependencies
# This bypasses the permission issues faced by the 'seluser'
USER root

# Set a working directory inside the container for our operations
# This can be any temporary directory, e.g., /tmp
WORKDIR /tmp

# Copy your requirements.txt file into the Docker image
COPY requirements.txt .

# Install Python dependencies using pip
# Use --no-cache-dir to avoid storing pip cache data in the image layer, saving space
# Ensure we use the pip from the existing virtual environment if it's preferred
# The selenium image typically has its venv at /opt/venv
RUN /opt/venv/bin/pip install --no-cache-dir -r requirements.txt

# Clean up the copied requirements.txt to keep the image lean
RUN rm requirements.txt

# Switch back to the non-root 'seluser' for security
# All subsequent commands in the Dockerfile, and when the container runs,
# will be executed as 'seluser'.
USER seluser

# Set the working directory for subsequent commands to the seluser's home directory.
# This is where Jenkins will mount your workspace.
WORKDIR /home/seluser