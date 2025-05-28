# Use a stable version of Selenium standalone chrome.
# Consider pinning to a specific version instead of 'latest' for reproducibility,
# e.g., selenium/standalone-chrome:125.0
FROM selenium/standalone-chrome:latest

# Set working directory inside the container
WORKDIR /app

# Install system dependencies (jq, curl, unzip) using apt-get.
# This section has been specifically adjusted to address the 'Permission denied' error
# with apt-get by:
# 1. Forcefully removing existing apt lists to clear any corruption.
# 2. Creating and setting permissive permissions on the 'partial' directory which was reported as missing/problematic.
# 3. Using DEBIAN_FRONTEND=noninteractive to prevent interactive prompts during apt operations.
# 4. Using --no-install-recommends to keep the image lean.
# 5. Using --allow-unauthenticated (use with caution in production) to bypass potential
#    authentication issues during package fetching.
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

# Create Selenium cache directory and set permissive permissions for the 'seluser'
# which is the default user in selenium/standalone-chrome images.
RUN mkdir -p /home/seluser/.cache/selenium && \
    chmod -R 777 /home/seluser/.cache

# Copy Python requirements file and install them using pip.
# The virtual environment is located at /opt/venv in the base image.
COPY requirements.txt .
RUN /opt/venv/bin/pip install --no-cache-dir -r requirements.txt
# Remove requirements.txt after installation to reduce final image size
RUN rm requirements.txt

# Allure Commandline installation:
# 1. Define the Allure version as an ARG to make it easily configurable.
# 2. Define ALLURE_HOME as an ENV variable for easy reference.
# 3. Download the Allure Commandline zip.
# 4. Unzip it to /opt.
# 5. Move the unzipped directory (which is allure-<version>) to the ALLURE_HOME path.
# 6. Remove the downloaded zip file.
# 7. Make the Allure executable.
ARG ALLURE_VERSION="2.25.0" # This is the version that was successful in your previous logs.
ENV ALLURE_HOME="/opt/allure-commandline"

RUN curl -o /tmp/allure-commandline.zip -L "https://repo.maven.apache.org/maven2/io/qameta/allure/allure-commandline/${ALLURE_VERSION}/allure-commandline-${ALLURE_VERSION}.zip" \
    && unzip /tmp/allure-commandline.zip -d /opt \
    && mv /opt/allure-${ALLURE_VERSION} ${ALLURE_HOME} \
    && rm /tmp/allure-commandline.zip \
    && chmod +x ${ALLURE_HOME}/bin/allure

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