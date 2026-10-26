FROM python:3.10-slim

# Instalar SWI-Prolog y dependencias del sistema
RUN apt-get update && apt-get install -y \
    swi-prolog \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Instalar Flask
RUN pip install --no-cache-dir flask

COPY app.py .
COPY proyecto.pl .

EXPOSE 5000

CMD ["python", "app.py"]