FROM python:3.11-slim
ENV APP_ENV=production PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY automind_api ./automind_api
RUN useradd --uid 10001 --create-home appuser
USER appuser
CMD ["sh","-c","uvicorn automind_api.main:app --host 0.0.0.0 --port ${PORT:-8080} --workers 1"]
