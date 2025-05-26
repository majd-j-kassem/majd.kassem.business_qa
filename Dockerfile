# Use the official Selenium standalone Chrome image as the base
FROM majdkassemt/selenium-qa:latest
#majdkassemt/selenium-qa
#

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

# --- START IMPORTANT ADDITIONS FOR CHROME HEADLESS RELIABILITY ---

# Install essential runtime dependencies for Chrome in a headless environment.
# These libraries are often required by Chrome/Chromedriver to run correctly,
# even if Chrome is already installed in the base image.
RUN apt-get update && apt-get install -y \
    fonts-liberation \
    libappindicator3-1 \
    libasound2 \
    libatk-bridge2.0-0 \
    libatk1.0-0 \
    libcairo2 \
    libcups2 \
    libdbus-glib-1-2 \
    libfontconfig1 \
    libgdk-pixbuf2.0-0 \
    libgconf-2-4 \
    libglib2.0-0 \
    libgtk-3-0 \
    libnspr4 \
    libnss3 \
    libpango-1.0-0 \
    libpangocairo-1.0-0 \
    libu2f-udev \
    libvulkan1 \
    libxcomposite1 \
    libxdamage1 \
    libxext6 \
    libxfixes3 \
    libxrandr2 \
    libxrender1 \
    libxtst6 \
    xdg-utils \
    --no-install-recommends \
    && rm -rf /var/lib/apt/lists/*

# Ensure the seluser's home directory has correct permissions BEFORE switching user.
# This is crucial for Chrome to write its user data and for Selenium Manager's cache.
RUN mkdir -p /home/seluser && chown -R seluser:seluser /home/seluser && chmod -R 777 /home/seluser

# --- END IMPORTANT ADDITIONS ---

# Set the working directory for subsequent commands to the seluser's home directory.
# This is where Jenkins will mount your workspace.
WORKDIR /home/seluser

# Switch back to the non-root 'seluser' for security
# All subsequent commands in the Dockerfile, and when the container runs,
# will be executed as 'seluser'.
USER seluser

# You can add any CMD or ENTRYPOINT here if needed for your image
# For Jenkins, it often overrides the ENTRYPOINT with its own command anyway.