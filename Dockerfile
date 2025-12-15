FROM python:3.10-slim-bookworm

WORKDIR /app

# UPDATE: 'build-essential' add kiya hai taaki gcc error na aaye
RUN apt-get update && apt-get install -y ffmpeg git build-essential && apt-get clean

COPY . .

RUN pip install --no-cache-dir --upgrade pip
RUN pip install av==12.0.0
RUN pip install -r requirements.txt

CMD ["python3", "main.py"]

