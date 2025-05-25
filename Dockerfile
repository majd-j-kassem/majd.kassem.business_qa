# Use a robust base image that already has Chrome and ChromeDriver installed.
FROM selenium/standalone-chrome:latest

# Define a non-root user and group
ARG USER_NAME=appuser
ARG USER_ID=1001
ARG GROUP_ID=1001

# Set the working directory inside the container
WORKDIR /app

# --- Temporarily switch to root user to perform system-level operations ---
USER root

# Create the user and group
RUN groupadd -g ${GROUP_ID} ${USER_NAME} && \
    useradd -m -u ${USER_ID} -g ${USER_NAME} -s /bin/bash ${USER_NAME} && \
    usermod -aG users ${USER_NAME} # Only add to 'users' group, which typically exists

# Create the /var/lib/apt/lists/partial directory and set appropriate permissions
RUN mkdir -p /var/lib/apt/lists/partial && \
    chmod 755 /var/lib/apt/lists/partial

# Install Python and pip.
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    python3 \
    python3-pip && \
    rm -rf /var/lib/apt/lists/*

# Link python3 to python if not already done, for systems expecting 'python' command
RUN update-alternatives --install /usr/bin/python python /usr/bin/python3 1

# Ensure the WORKDIR is owned by the new user BEFORE switching users
# This makes sure appuser can write the application code into /app later
RUN chown -R ${USER_NAME}:${USER_NAME} /app

# --- IMPORTANT: Grant appuser write permissions to the virtual environment's site-packages
# This is the crucial step to allow pip to install packages into the venv
RUN chown -R ${USER_NAME}:${USER_NAME} /opt/venv

# --- Now, switch to the newly created non-root user ---
USER ${USER_NAME}

# Set the PATH to include the virtual environment's bin directory
# This ensures that pip and other venv executables are found
ENV PATH="/opt/venv/bin:${PATH}"

# Copy just the requirements.txt file first to leverage Docker's build cache.
COPY requirements.txt .

# Install Python dependencies directly into the virtual environment (no --user flag)
# The virtual environment should be active, so pip will install there.
RUN pip install --no-cache-dir -r requirements.txt

# Ensure pytest is installed
RUN pip install --no-cache-dir pytest

# Copy the rest of your application code into the container
# This will now copy files owned by the appuser by default as the USER is appuser
COPY . .

# CMD ["pytest", "src/tests"] # Jenkins will override this, but useful for manual runs