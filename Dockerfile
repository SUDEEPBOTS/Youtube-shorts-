FROM python:3.9-slim

WORKDIR /app

# Install dependencies first
COPY requirements.txt .
RUN pip install --no-cache-dir \
    pyrogram==2.0.106 \
    pytgcalls==3.1.0

# Copy your application code
COPY . .

CMD ["python", "main.py"]
