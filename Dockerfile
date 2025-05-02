FROM python:3.11-slim

# Çalışma dizini
WORKDIR /app

# Gereksinim dosyasını kopyala ve yükle
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Uygulama dosyalarını kopyala
COPY . .

# Varsayılan komut
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
