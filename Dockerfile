# 'buster' expire ho gaya, isliye 'bullseye' use kar rahe hain
FROM python:3.9-slim-bullseye

WORKDIR /app

# Basic tools install kar rahe hain
RUN apt-get update && apt-get install -y ffmpeg git build-essential && apt-get clean

COPY . .

RUN pip install --no-cache-dir --upgrade pip
RUN pip install av
RUN pip install -r requirements.txt

CMD ["python3", "main.py"]

