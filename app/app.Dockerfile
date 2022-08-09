FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt ./
RUN pip install -r requirements.txt
# This line is for building the image standalone, dev environment uses local volume "/app"
# COPY . /app
CMD ["python", "helloPanda.py"]