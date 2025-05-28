# Use a stable version of Selenium standalone chrome.
# Consider pinning to a specific version instead of 'latest' for reproducibility,
# e.g., selenium/standalone-chrome:125.0
FROM selenium/standalone-chrome:latest

# Set working directory inside the container
WORKDIR /app

# Switch to root for all system-level operations and installations
USER root

# Install system dependencies (jq, curl, unzip) using apt-get.
RUN rm -rf /var/lib/apt/lists/* && \
    mkdir -p /var/lib/apt/lists/partial && \
    chmod 777 /var/lib/apt/lists/partial && \
    DEBIAN_FRONTEND=noninteractive apt-get update -y --allow-unauthenticated && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
    apt-utils \
    jq \
    curl \
    unzip \
    && rm -rf /var/lib/apt/lists/*

# Allure Commandline installation:
ARG ALLURE_VERSION="2.25.0"
ENV ALLURE_HOME="/opt/allure-commandline"

RUN curl -o /tmp/allure-commandline.zip -L "https://repo.maven.apache.org/maven2/io/qameta/allure/allure-commandline/${ALLURE_VERSION}/allure-commandline-${ALLURE_VERSION}.zip" \
    && unzip /tmp/allure-commandline.zip -d /opt \
    && mv /opt/allure-${ALLURE_VERSION} ${ALLURE_HOME} \
    && rm /tmp/allure-commandline.zip \
    && chmod +x ${ALLURE_HOME}/bin/allure

# --- IMPORTANT FIX FOR requirements.txt DELETION ---
# Copy Python requirements file
COPY requirements.txt .
# Install them using pip (this command will run as root as we are currently root)
RUN /opt/venv/bin/pip install --no-cache-dir -r requirements.txt
# Remove requirements.txt after installation to reduce final image size.
# This RUN command executes as root, resolving the permission issue.
RUN rm requirements.txt
# --- END IMPORTANT FIX ---

# Switch back to the 'seluser' for running the application/tests (best practice for security)
USER seluser

# Create Selenium cache directory and set permissive permissions for the 'seluser'
RUN mkdir -p /home/seluser/.cache/selenium && \
    chmod -R 777 /home/seluser/.cache

# Add Allure's bin directory to the PATH so 'allure' command can be found by seluser
ENV PATH="${ALLURE_HOME}/bin:${PATH}"

# Copy your application (test) code into the container as seluser.
# This assumes your Dockerfile is at the root of your project and 'src' contains tests.
COPY . .

# Re-confirm working directory (redundant if already set above, but doesn't hurt)
WORKDIR /app

# Optional: Define an entrypoint or command to run tests directly when the container starts.
# ENTRYPOINT ["/opt/venv/bin/pytest"]
# CMD ["src/tests"]