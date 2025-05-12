FROM ubuntu:22.04

# Set environment variables
ENV DEBIAN_FRONTEND=noninteractive
ENV DISPLAY=:0

# Install required packages
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    xvfb \
    x11vnc \
    fluxbox \
    libqt5webkit5-dev \
    libqt5webengine5 \
    libqt5webenginewidgets5 \
    libxkbcommon-x11-0 \
    libxcb-icccm4 \
    libxcb-image0 \
    libxcb-keysyms1 \
    libxcb-randr0 \
    libxcb-render-util0 \
    libxcb-xinerama0 \
    libxcb-xkb1 \
    libxkbcommon-x11-0 \
    cups \
    cups-client \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Create app directory
WORKDIR /app

# Copy application files
COPY kiosk_browser.py /app/
COPY requirements.txt /app/

# Install Python dependencies
RUN pip3 install -r requirements.txt

# Create startup script
COPY start_kiosk.sh /app/
RUN chmod +x /app/start_kiosk.sh /app/kiosk_browser.py

# Create entrypoint script
RUN echo '#!/bin/bash\n\
Xvfb :0 -screen 0 1280x800x24 &\n\
sleep 1\n\
x11vnc -display :0 -forever -passwd password &\n\
fluxbox &\n\
sleep 2\n\
python3 /app/kiosk_browser.py\n\
' > /app/entrypoint.sh && chmod +x /app/entrypoint.sh

# Expose VNC port
EXPOSE 5900

# Set entrypoint
ENTRYPOINT ["/app/entrypoint.sh"]
