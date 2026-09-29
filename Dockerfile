FROM python:3.12-slim

WORKDIR /app

# Installation des dépendances système
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copie et installation des dépendances Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copie de l'application et de la configuration Streamlit
COPY . .

ENV PORT=8080
EXPOSE 8080

CMD ["sh", "-c", "streamlit run main.py --server.port=${PORT} --server.address=0.0.0.0"]
