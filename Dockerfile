# Hafif bir Python imajı
FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

# Sistem bağımlılıkları: Chrome kurulumu için araçlar
RUN apt-get update && apt-get install -y \
    wget gnupg ca-certificates curl unzip \
    --no-install-recommends && rm -rf /var/lib/apt/lists/*

# Google Chrome stable repo anahtarını ekle ve Chrome'u kur
RUN mkdir -p /etc/apt/keyrings \
    && wget -qO- https://dl.google.com/linux/linux_signing_key.pub | gpg --dearmor > /etc/apt/keyrings/google.gpg \
    && echo "deb [arch=amd64 signed-by=/etc/apt/keyrings/google.gpg] http://dl.google.com/linux/chrome/deb/ stable main" \
    > /etc/apt/sources.list.d/google-chrome.list \
    && apt-get update \
    && apt-get install -y google-chrome-stable --no-install-recommends \
    && rm -rf /var/lib/apt/lists/*

# Çalışma dizini
WORKDIR /app

# Python bağımlılıkları
COPY requirements.txt ./
RUN pip install -r requirements.txt

# Projeyi kopyala
COPY . .

# Render portunu dışarı aç (bilgi amaçlı)
EXPOSE 5000

# Uygulamayı başlat
CMD ["python", "app.py"]
