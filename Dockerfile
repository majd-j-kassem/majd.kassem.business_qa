# Use a stable version of Selenium standalone chrome.
# Consider pinning to a specific version instead of 'latest' for reproducibility,
# e.g., selenium/standalone-chrome:125.0
FROM selenium/standalone-chrome:latest

# Set working directory inside the container
WORKDIR /app

# --- FIX START: Switch to root for apt operations and back to seluser ---

# Temporarily switch to root user to perform apt-get operations
USER root

# Install system dependencies (jq, curl, unzip) using apt-get.
# This section ensures that apt-get operations run with necessary permissions.
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

# Switch back to the default 'seluser' for subsequent operations
# This is crucial for security and compatibility with Selenium.
USER seluser

# --- FIX END ---

# Create Selenium cache directory and set permissive permissions for the 'seluser'
# (This RUN command will now execute as 'seluser')
RUN mkdir -p /home/seluser/.cache/selenium && \
    chmod -R 777 /home/seluser/.cache

# Copy Python requirements file and install them using pip.
# (This RUN command will also execute as 'seluser')
COPY requirements.txt .
RUN /opt/venv/bin/pip install --no-cache-dir -r requirements.txt
# Remove requirements.txt after installation to reduce final image size
RUN rm requirements.txt

# Allure Commandline installation:
# This requires root privileges for installing into /opt.
# So, we need to temporarily switch to root again.
ARG ALLURE_VERSION="2.25.0"
ENV ALLURE_HOME="/opt/allure-commandline"

USER root
RUN curl -o /tmp/allure-commandline.zip -L "https://repo.maven.apache.org/maven2/io/qameta/allure/allure-commandline/${ALLURE_VERSION}/allure-commandline-${ALLURE_VERSION}.zip" \
    && unzip /tmp/allure-commandline.zip -d /opt \
    && mv /opt/allure-${ALLURE_VERSION} ${ALLURE_HOME} \
    && rm /tmp/allure-commandline.zip \
    && chmod +x ${ALLURE_HOME}/bin/allure
USER seluser


# Add Allure's bin directory to the PATH so 'allure' command can be found
ENV PATH="${ALLURE_HOME}/bin:${PATH}"

# Copy your application (test) code into the container.
# This assumes your Dockerfile is at the root of your project.
COPY . .

# Re-confirm working directory (redundant if already set above, but doesn't hurt)
WORKDIR /app

# Optional: Define an entrypoint or command to run tests directly when the container starts.
# You would typically set this if this Dockerfile is for a test runner.
# ENTRYPOINT ["/opt/venv/bin/pytest"]
# CMD ["src/tests"] # Assuming your tests are in src/tests