FROM python:3.11-slim-bullseye

RUN pip install flask pytest-playwright

# https://stackoverflow.com/questions/72006251/pyppeteer-and-docker-error-browser-closed-unexpectedly
RUN apt-get update && apt-get install -y \
    apt-transport-https \
    ca-certificates \
    curl \
    gnupg \
    --no-install-recommends \
    && curl -sSL https://dl.google.com/linux/linux_signing_key.pub | apt-key add - \
    && echo "deb [arch=amd64] https://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google-chrome.list \
    && apt-get update && apt-get install -y \
    google-chrome-stable \
    --no-install-recommends && \
    apt clean
# It won't run from the root user.
RUN groupadd chrome && useradd -g chrome -s /bin/bash -G audio,video chrome \
    && mkdir -p /home/chrome && chown -R chrome:chrome /home/chrome

WORKDIR /usr/src/app
COPY app .
EXPOSE 31415
CMD [ "python3", "/usr/src/app/rpilocator_ja.py" ]
