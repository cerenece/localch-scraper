FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    wget unzip gnupg curl fonts-liberation \
    libnss3 libxss1 libasound2 libatk-bridge2.0-0 libgtk-3-0 \
    libx11-xcb1 libxcb1 libdbus-1-3 libxcomposite1 libxdamage \
    libxrandr2 libgbm1 libpangocairo-1.0-0 libpango-1.0-0 libatspi2.0-0 \
    ca-certificates chromium chromium-driver \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p /app/results

ENV CHROMIUM_PATH=/usr/bin/chromium
ENV CHROMEDRIVER_PATH=/usr/bin/chromedriver

EXPOSE 5000

CMD ["gunicorn", "-w", "2", "--threads", "4", "-b", "0.0.0.0:5000", "app:app"]
