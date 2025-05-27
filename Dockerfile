# Use your custom Selenium base image
FROM majdkassemt/selenium-qa:latest

# Switch to the root user temporarily to install dependencies and ChromeDriver
USER root

# Set a working directory inside the container for our operations
WORKDIR /tmp

# Install general dependencies needed for curl, unzip, wget, gnupg, ca-certificates, AND jq
RUN apt-get update && apt-get install -y \
    curl \
    unzip \
    wget \
    gnupg \
    ca-certificates \
    jq \
    && rm -rf /var/lib/apt/lists/*

# --- EXPLICITLY INSTALL CHROMEDRIVER (REVISED LOOKUP) ---
# This is the most crucial part to bypass Selenium Manager's issues.
# We'll fetch the LATEST_STABLE_CHROMEDRIVER_VERSION for the detected Chrome MAJOR version.

RUN CHROME_VERSION=$(google-chrome --version | grep -oE '[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+' | head -n 1) \
    && CHROME_MAJOR_VERSION=$(echo "$CHROME_VERSION" | cut -d. -f1) \
    && echo "Detected Chrome Major version: $CHROME_MAJOR_VERSION" \
    \
    # --- DEBUGGING CURL OUTPUT ---
    && echo "Attempting to curl ChromeDriver info..." \
    && CHROMEDRIVER_JSON_OUTPUT=$(curl -s "https://googlechromelabs.github.io/chrome-for-testing/last-known-good-versions-int.json") \
    && echo "CURL Exit Code: $?" \
    && echo "CURL Output Start >>>" \
    && echo "$CHROMEDRIVER_JSON_OUTPUT" \
    && echo "<<< CURL Output End" \
    \
    # Check if CURL output is empty or not JSON-like
    && if [ -z "$CHROMEDRIVER_JSON_OUTPUT" ]; then \
        echo "ERROR: curl returned empty output. Possible network issue or API failure." && exit 1; \
    fi \
    && if ! echo "$CHROMEDRIVER_JSON_OUTPUT" | jq -e . > /dev/null; then \
        echo "ERROR: curl returned non-JSON output. Output was:" && echo "$CHROMEDRIVER_JSON_OUTPUT" && exit 1; \
    fi \
    \
    # Now proceed with jq if checks pass
    && CHROMEDRIVER_DATA=$(echo "$CHROMEDRIVER_JSON_OUTPUT" | \
                              jq -r ".versions[] | select(.version | startswith(\"$CHROME_MAJOR_VERSION.\")) | .chromedriver") \
    && echo "JQ Parsing Result (CHROMEDRIVER_DATA): $CHROMEDRIVER_DATA" \
    \
    # Check if jq found any data
    && if [ -z "$CHROMEDRIVER_DATA" ] || [ "$CHROMEDRIVER_DATA" = "null" ]; then \
        echo "ERROR: jq could not find ChromeDriver info for Chrome $CHROME_MAJOR_VERSION. API might have changed or version not found." && exit 1; \
    fi \
    \
    && CHROMEDRIVER_VERSION=$(echo "$CHROMEDRIVER_DATA" | jq -r ".version") \
    && CHROMEDRIVER_URL=$(echo "$CHROMEDRIVER_DATA" | jq -r ".downloads.linux64[0].url") \
    && echo "Downloading ChromeDriver version: $CHROMEDRIVER_VERSION from URL: $CHROMEDRIVER_URL" \
    && wget -q "$CHROMEDRIVER_URL" -O chromedriver-linux64.zip \
    && unzip chromedriver-linux64.zip -d /usr/local/bin/ \
    && rm chromedriver-linux64.zip \
    && chmod +x /usr/local/bin/chromedriver \
    && echo "ChromeDriver installed at /usr/local/bin/chromedriver"

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
RUN mkdir -p /home/seluser && chown -R seluser:seluser /home/seluser && chmod -R 777 /home/seluser

# Set the working directory for subsequent commands to the seluser's home directory.
WORKDIR /home/seluser

# Switch back to the non-root 'seluser' for security
USER seluser