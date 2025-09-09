# Use Ubuntu as base image
FROM ubuntu:22.04

# Set environment variables
ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1
ENV DISPLAY=:99

# Install system dependencies
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    python3-dev \
    wget \
    curl \
    unzip \
    xvfb \
    fonts-liberation \
    libasound2 \
    libatk-bridge2.0-0 \
    libatspi2.0-0 \
    libdrm2 \
    libgtk-3-0 \
    libnspr4 \
    libnss3 \
    libwayland-client0 \
    libxcomposite1 \
    libxdamage1 \
    libxfixes3 \
    libxkbcommon0 \
    libxrandr2 \
    xdg-utils \
    libu2f-udev \
    libvulkan1 \
    && rm -rf /var/lib/apt/lists/*

# Install Google Chrome
RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - \
    && echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google.list \
    && apt-get update \
    && apt-get install -y google-chrome-stable \
    && rm -rf /var/lib/apt/lists/*

# Set up Python environment
RUN python3 -m pip install --upgrade pip

# Install SeleniumBase and related packages
RUN pip3 install seleniumbase selenium webdriver-manager

# Install ChromeDriver using SeleniumBase
RUN seleniumbase install chromedriver

# Set up working directory
WORKDIR /app

# Copy application files
COPY . /app

# Install Python dependencies from requirements.txt if it exists
RUN if [ -f requirements.txt ]; then pip3 install --no-cache-dir -r requirements.txt; fi

# Create directories that SeleniumBase might need
RUN mkdir -p /app/downloaded_files \
    && mkdir -p /app/logs \
    && mkdir -p /app/assets \
    && mkdir -p /tmp/seleniumbase \
    && mkdir -p /dev/shm \
    && chmod -R 777 /app \
    && chmod -R 777 /tmp/seleniumbase

# Create a non-root user but keep running as root for now
RUN useradd -m -s /bin/bash seleniumuser

# Configure Chrome for Docker environment
RUN echo '#!/bin/bash\ngoogle-chrome --no-sandbox --disable-dev-shm-usage --disable-gpu --remote-debugging-port=9222 --disable-extensions --disable-plugins "$@"' > /usr/local/bin/google-chrome-stable \
    && chmod +x /usr/local/bin/google-chrome-stable

# Set environment variables for Chrome
ENV CHROME_BIN=/usr/bin/google-chrome-stable
ENV CHROME_PATH=/usr/bin/google-chrome-stable
ENV CHROMIUM_FLAGS="--no-sandbox --disable-dev-shm-usage --disable-gpu --disable-extensions --disable-plugins"

# Start Xvfb in background for display
RUN echo '#!/bin/bash\nXvfb :99 -screen 0 1024x768x24 > /dev/null 2>&1 &\nexec "$@"' > /usr/local/bin/entrypoint.sh \
    && chmod +x /usr/local/bin/entrypoint.sh

ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]

# Expose Flask port
EXPOSE 5000

# Default command
CMD ["python3", "main.py"]