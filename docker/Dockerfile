# docker/Dockerfile
# This Dockerfile is intentionally minimal and references src/api/main.py as entrypoint.
FROM python:3.10-slim

WORKDIR /app

# system deps for lightgbm/xgboost if needed
RUN apt-get update && apt-get install -y --no-install-recommends build-essential gcc g++ libgomp1 && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /app/requirements.txt
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r /app/requirements.txt

COPY . /app

EXPOSE 8000
CMD ["uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
