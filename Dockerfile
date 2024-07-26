FROM python:3.8-slim

WORKDIR /app

COPY . /app

RUN pip install --no-cache-dir fastapi uvicorn redis

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
