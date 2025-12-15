# Python 3.9 use kar rahe hain (Ispe py-tgcalls error nahi deta)
FROM python:3.9-slim-buster

WORKDIR /app

# Basic tools
RUN apt-get update && apt-get install -y ffmpeg git build-essential && apt-get clean

COPY . .

RUN pip install --no-cache-dir --upgrade pip
RUN pip install av
RUN pip install -r requirements.txt

CMD ["python3", "main.py"]

