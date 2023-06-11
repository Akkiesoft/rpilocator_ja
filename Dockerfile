FROM python:3-slim-buster
RUN pip install flask pyppeteer
WORKDIR /usr/src/app
COPY app .
EXPOSE 31415
CMD [ "python3", "/usr/src/app/rpilocator_ja.py" ]
