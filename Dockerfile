FROM python:3.11-slim

RUN apt-get update && apt-get install -y sqlite3 && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY app /app/app

RUN pip install fastapi uvicorn

CMD ["uvicorn","app.main:app","--host","0.0.0.0","--port","8000"]
