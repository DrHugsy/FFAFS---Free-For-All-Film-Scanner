FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    libraw-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

# Render (y otros PaaS) asignan el puerto por la variable de entorno PORT.
# Si no existe (por ejemplo corriendo en tu propia VM), usa 8000 por defecto.
# 1 worker alcanza para el free tier de Render (RAM ajustada); si corrés esto
# en una máquina con más memoria, podés subir --workers a 2.
CMD gunicorn --bind 0.0.0.0:${PORT:-8000} --workers 1 --timeout 120 server_prod:app
