# Use the official Selenium Chrome image as your base.
# This image already contains Chrome, ChromeDriver, and necessary dependencies
# for headless execution, including Xvfb.
FROM selenium/standalone-chrome:latest

# Switch to the root user temporarily for system package installations
# The official images run as 'seluser' by default, but apt-get needs root.
USER root

# Set a working directory for your application files.
# It's good practice to place your application code in a directory other than /tmp
# to avoid conflicts and for better organization.
WORKDIR /app

# Install any additional system dependencies your tests might need.
# The official Selenium images are quite comprehensive, but if you have
# unique requirements (e.g., specific image manipulation libraries, database clients),
# you'd add them here.
# Removed many common libraries already present in the selenium image.
# Only keeping 'jq' if you still need it for other purposes.
RUN apt-get update && apt-get install -y \
    jq \
    # Add other system packages here if your tests explicitly need them, e.g.:
    # imagemagick \
    # other-dev-libs \
    && rm -rf /var/lib/apt/lists/*

RUN mkdir -p /home/seluser/.cache/selenium && \
    chmod -R 777 /home/seluser/.cache

# --- REMOVED THE ENTIRE CHROMEDRIVER INSTALLATION BLOCK ---
# This is no longer needed because selenium/standalone-chrome:latest
# already provides a working Chrome and ChromeDriver setup.
# Attempting to re-download and install it can cause conflicts or break the image.

# Copy your Python requirements file and install Python dependencies.
# Install into the virtual environment used by the base image if desired,
# or simply let pip install globally within the container's Python setup.
# The /opt/venv/bin/pip path is common for these images.
COPY requirements.txt .
RUN /opt/venv/bin/pip install --no-cache-dir -r requirements.txt
# Remove requirements.txt after installation to keep the image cleaner (optional)
RUN rm requirements.txt

# --- NEW: Add Allure Commandline to the Docker image ---
ARG ALLURE_VERSION="2.25.0" # Use a stable version, e.g., 2.25.0 or 2.34.0 as seen in your logs
ENV ALLURE_HOME="/opt/allure-commandline"

RUN curl -o /tmp/allure-commandline.zip -L "https://repo.maven.apache.org/maven2/io/qameta/allure/allure-commandline/${ALLURE_VERSION}/allure-commandline-${ALLURE_VERSION}.zip" \
    && unzip /tmp/allure-commandline.zip -d /opt \
    && mv /opt/allure-commandline-${ALLURE_VERSION} ${ALLURE_HOME} \
    && rm /tmp/allure-commandline.zip \
    && chmod +x ${ALLURE_HOME}/bin/allure

ENV PATH="${ALLURE_HOME}/bin:${PATH}"
# --- END NEW ---

# Copy your entire test project into the image.
# This should be done after installing dependencies to leverage Docker's build cache.
# If your project changes but requirements.txt doesn't, this layer will be rebuilt,
# but the pip install layer won't.
COPY . .

# Set up a virtual display for Chrome.
# These environment variables are usually already set by the Selenium image,
# but explicitly setting them here doesn't hurt and provides clarity.
ENV DISPLAY=:99
ENV XAUTHORITY=/tmp/.Xauthority

# The seluser already exists and has appropriate permissions in the base image.
# No need to create or chown /home/seluser.

# Switch back to the non-root 'seluser' for running your tests.
# This is a security best practice.
USER seluser

# Set the working directory for subsequent commands (like your tests) to the seluser's home directory.
# This is where your copied application code will reside if you copy it to /home/seluser instead of /app
# If you copy to /app, then your WORKDIR should be /app for the 'seluser'.
# Based on the WORKDIR /app above, we should keep it consistent.
WORKDIR /app

# Optional: Define the default command to run when the container starts.
# This makes it easier to run your tests by just `docker run your-image-name`.
# Example: If your tests are run with `pytest` from the `/app` directory:
# CMD ["pytest"]
# Or if you have a specific script:
# CMD ["python", "run_tests.py"]