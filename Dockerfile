# Base python image
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# The following native requirements (Xvfb/X11) are helpful to prevent pyautogui 
# from failing on import inside headless Linux, although this bot heavily relies on 
# Windows MS-Word. 
RUN apt-get update && apt-get install -y \
    python3-xlib \
    xvfb \
    scrot \
    python3-tk \
    python3-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy python dependencies
COPY requirements.txt .

# Install python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY . .

# Set display for pyautogui inside simple linux env
ENV DISPLAY=:0

CMD ["python", "human_typer.py"]
