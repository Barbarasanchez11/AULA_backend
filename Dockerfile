FROM python:3.11-slim

WORKDIR /code

# Instalar dependencias del sistema necesarias para psycopg2 si fuera necesario (versión binary no suele requerirlo, pero es bueno tenerlo en cuenta)
# RUN apt-get update && apt-get install -y libpq-dev gcc

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
