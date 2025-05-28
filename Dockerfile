# Your existing base image
FROM selenium/standalone-chrome:latest

# Set working directory (as you already have)
WORKDIR /app

# Install jq and dependencies (as you already have)
# Also add curl and unzip for downloading/extracting Allure CLI
# --- FIX START: Add a preliminary apt clean and reinstall apt-utils ---
RUN apt-get clean && rm -rf /var/lib/apt/lists/* && \
    apt-get update && apt-get install -y apt-utils && \
    apt-get update && apt-get install -y \
    jq \
    curl \
    unzip \
    && rm -rf /var/lib/apt/lists/*
# --- FIX END ---

# Create cache directory (as you already have)
RUN mkdir -p /home/seluser/.cache/selenium && \
    chmod -R 777 /home/seluser/.cache

# Copy requirements.txt and install Python dependencies (as you already have)
COPY requirements.txt .
RUN /opt/venv/bin/pip install --no-cache-dir -r requirements.txt
RUN rm requirements.txt

# Allure CLI installation (your last fix was correct for this part)
ARG ALLURE_VERSION="2.25.0"
ENV ALLURE_HOME="/opt/allure-commandline"

RUN curl -o /tmp/allure-commandline.zip -L "https://repo.maven.apache.org/maven2/io/qameta/allure/allure-commandline/${ALLURE_VERSION}/allure-commandline-${ALLURE_VERSION}.zip" \
    && unzip /tmp/allure-commandline.zip -d /opt \
    && mv /opt/allure-${ALLURE_VERSION} ${ALLURE_HOME} \
    && rm /tmp/allure-commandline.zip \
    && chmod +x ${ALLURE_HOME}/bin/allure

ENV PATH="${ALLURE_HOME}/bin:${PATH}"

# Copy your application code (as you already have)
COPY . .

# Set WORKDIR again (as you already have)
WORKDIR /app