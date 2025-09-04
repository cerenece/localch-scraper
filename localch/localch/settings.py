BOT_NAME = "localch"

SPIDER_MODULES = ["localch.spiders"]
NEWSPIDER_MODULE = "localch.spiders"

# User-Agent
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0 Safari/537.36"

# Robots.txt
ROBOTSTXT_OBEY = False

# Concurrency & Download Delay
CONCURRENT_REQUESTS = 2
CONCURRENT_REQUESTS_PER_DOMAIN = 1
DOWNLOAD_DELAY = 1

# AutoThrottle
AUTOTHROTTLE_ENABLED = True
AUTOTHROTTLE_START_DELAY = 1
AUTOTHROTTLE_MAX_DELAY = 5
AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0
AUTOTHROTTLE_DEBUG = False

# Output encoding
FEED_EXPORT_ENCODING = "utf-8"

# Excel çıktısı ayarı
FEEDS = {
    "sonuc.csv": {
        "format": "csv",
        "encoding": "utf-8",
        "store_empty": False,
        "fields": ["Firma Adı", "Adres", "Telefon", "Email", "Website", "URL"],
    },
}

