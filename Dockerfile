FROM python:3.11-slim

RUN apt-get update && apt-get install -y \
    libmediainfo-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app/ ./app
COPY sample_data/ ./sample_data

CMD ["python", "app/main.py"]