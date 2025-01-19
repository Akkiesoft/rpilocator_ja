FROM python:3.12-slim-bookworm

RUN pip install flask pytest-playwright

# https://stackoverflow.com/questions/72006251/pyppeteer-and-docker-error-browser-closed-unexpectedly
RUN apt-get update && apt-get install -y \
    chromium \
    --no-install-recommends && \
    apt clean
# It won't run from the root user.
RUN groupadd chrome && useradd -g chrome -s /bin/bash -G audio,video chrome \
    && mkdir -p /home/chrome && chown -R chrome:chrome /home/chrome

WORKDIR /usr/src/app
COPY app .
EXPOSE 31415
CMD [ "python3", "/usr/src/app/rpilocator_ja.py" ]
