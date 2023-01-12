FROM python:3.9-slim
WORKDIR /app
COPY /slack-listener/requirements.txt ./
RUN pip install -r requirements.txt
COPY /slack-listener/helloPanda3.py ./
# This line is for building the image standalone, dev environment uses local volume "/app"
# COPY . /app
CMD ["python", "helloPanda3.py"]