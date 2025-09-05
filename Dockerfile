# Temel imaj
FROM python:3.11-slim

# Çalışma dizini
WORKDIR /app

# Gereksinimleri kopyala ve yükle
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Uygulamayı kopyala
COPY . .

# Portu aç
EXPOSE 8080

# Uygulamayı çalıştır
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:app"]

