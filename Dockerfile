# Use your custom Selenium base image
FROM majdkassemt/selenium-qa:latest

# Switch to the root user temporarily to install dependencies and ChromeDriver
USER root

# Set a working directory inside the container for our operations
WORKDIR /tmp

# Install general dependencies needed for curl and unzip if not already in base image
RUN apt-get update && apt-get install -y \
    curl \
    unzip \
    wget \
    gnupg \
    ca-certificates \
    # Clean up apt caches to keep image size down
    && rm -rf /var/lib/apt/lists/*

# --- EXPLICITLY INSTALL CHROMEDRIVER ---
# This is the most crucial part to bypass Selenium Manager's issues.
# We need to know which version of Chrome is in your base image.
# You can find this by running `google-chrome --version` inside a container
# launched from `majdkassemt/selenium-qa:latest`.
# For example, let's assume it's Chrome 125.0.6422.112 (ADJUST THIS BASED ON YOUR BASE IMAGE'S CHROME VERSION)
# If your base image keeps Chrome updated, you might need a more dynamic way,
# but for stability in a custom image, knowing the exact Chrome version is best.

# Method 1: Dynamically determine Chrome version and download compatible ChromeDriver (preferred)
RUN CHROME_VERSION=$(google-chrome --version | grep -oE '[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+' | head -n 1) \
    && echo "Detected Chrome version from base image: $CHROME_VERSION" \
    && CHROMEDRIVER_VERSION=$(curl -s "https://googlechromelabs.github.io/chrome-for-testing/last-known-good-versions-int.json" | \
                              grep -oE "\"$CHROME_VERSION\"[^{]*\"chromedriver\":\"([0-9]+\.[0-9]+\.[0-9]+\.[0-9]+)\"" | \
                              sed -nE 's/.*"chromedriver":"([^"]+)".*/\1/p') \
    && echo "Downloading ChromeDriver version: $CHROMEDRIVER_VERSION" \
    && wget -q https://storage.googleapis.com/chrome-for-testing-public/$CHROMEDRIVER_VERSION/linux64/chromedriver-linux64.zip \
    && unzip chromedriver-linux64.zip -d /usr/local/bin/ \
    && rm chromedriver-linux64.zip \
    && chmod +x /usr/local/bin/chromedriver \
    && echo "ChromeDriver installed at /usr/local/bin/chromedriver"

# Method 2: Hardcode if dynamic fails or if your base image's Chrome version is fixed
# Uncomment and use this if Method 1 causes issues:
# ENV CHROMEDRIVER_VERSION="125.0.6422.112" # <--- IMPORTANT: REPLACE WITH YOUR CHROME VERSION'S COMPATIBLE CHROMEDRIVER
# RUN wget -q https://storage.googleapis.com/chrome-for-testing-public/$CHROMEDRIVER_VERSION/linux64/chromedriver-linux64.zip \
#     && unzip chromedriver-linux64.zip -d /usr/local/bin/ \
#     && rm chromedriver-linux64.zip \
#     && chmod +x /usr/local/bin/chromedriver \
#     && echo "ChromeDriver ${CHROMEDRIVER_VERSION} installed at /usr/local/bin/chromedriver"

# --- END EXPLICIT CHROMEDRIVER INSTALLATION ---

# Install Python dependencies using pip
COPY requirements.txt .
RUN /opt/venv/bin/pip install --no-cache-dir -r requirements.txt
RUN rm requirements.txt

# --- IMPORTANT ADDITIONS FOR CHROME HEADLESS RELIABILITY ---
# These are still relevant as base Selenium images might not have all needed fonts/libraries.
# You already had many of these, just consolidating.
RUN apt-get update && apt-get install -y \
    fonts-liberation \
    fonts-noto-color-emoji \
    libappindicator3-1 \
    libatk-bridge2.0-0 \
    libatk1.0-0 \
    libcairo2 \
    libcups2 \
    libdbus-glib-1-2 \
    libfontconfig1 \
    libgdk-pixbuf2.0-0 \
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
    xkb-data \
    xvfb \
    --no-install-recommends \
    && rm -rf /var/lib/apt/lists/*

# Set up a virtual display for Chrome.
ENV DISPLAY=:99
ENV XAUTHORITY=/tmp/.Xauthority

# Ensure the seluser's home directory has correct permissions BEFORE switching user.
# This is crucial for Chrome to write its user data and for Selenium Manager's cache.
# Also for temporary directories for Chrome, which often default to /tmp or home dir
RUN mkdir -p /home/seluser && chown -R seluser:seluser /home/seluser && chmod -R 777 /home/seluser

# Set the working directory for subsequent commands to the seluser's home directory.
# This is where Jenkins will mount your workspace.
WORKDIR /home/seluser

# Switch back to the non-root 'seluser' for security
USER seluser

# You can add any CMD or ENTRYPOINT here if needed for your image
# For Jenkins, it often overrides the ENTRYPOINT with its own command anyway.