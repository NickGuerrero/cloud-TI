FROM python:3.9-slim
WORKDIR /app
COPY /grouping-queue/requirements.txt ./
RUN pip install -r requirements.txt
COPY /grouping-queue/GroupQueue.py ./
# This line is for building the image standalone, dev environment uses local volume "/app"
# COPY . /app
CMD ["python", "GroupQueue.py"]