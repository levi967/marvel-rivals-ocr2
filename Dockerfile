FROM python:3.11-slim

# Install system packages like Tesseract
RUN apt-get update && \
    apt-get install -y tesseract-ocr libgl1-mesa-glx && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY . /app

RUN pip install --no-cache-dir -r requirements.txt

CMD ["gunicorn", "app:app"]
