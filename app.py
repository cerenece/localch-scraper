from flask import Flask, render_template, Response, request, send_file
import threading, json, time, csv, os, sys

# localch_spider.py'nin yolu
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "localch", "localch", "spiders"))
from localch_spider import LocalchSeleniumSpider

app = Flask(__name__)
results = []

# CSV'lerin kaydedileceği klasör (container içinde /app/results)
RESULTS_DIR = "/app/results"
os.makedirs(RESULTS_DIR, exist_ok=True)

def run_spider(keyword):
    """
    Thread içinde çalışan spider fonksiyonu.
    """
    global results
    results = []

    spider = LocalchSeleniumSpider(keyword=keyword)

    # start_requests generator’ını al
    start_requests = spider.start_requests()

    for request in start_requests:
        for item in spider.parse(request):
            results.append(item)

            # CSV kaydı
            csv_file = os.path.join(RESULTS_DIR, f"{keyword}_results.csv")
            write_header = not os.path.exists(csv_file)

            with open(csv_file, "a", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(
                    f,
                    fieldnames=["Firma Adı", "Adres", "Telefon", "Email", "Website", "URL"]
                )
                if write_header:
                    writer.writeheader()

                writer.writerow({
                    "Firma Adı": item.get("Firma Adı", "Yok"),
                    "Adres": item.get("Adres", "Yok"),
                    "Telefon": ",".join(item.get("Telefon", [])),
                    "Email": ",".join(item.get("Email", [])),
                    "Website": ",".join(item.get("Website", [])),
                    "URL": item.get("URL", "Yok")
                })
                f.flush()  # anlık yazdırma

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        keyword = request.form["keyword"]

        # Spider'ı ayrı thread'te başlat
        thread = threading.Thread(target=run_spider, args=(keyword,))
        thread.daemon = True  # Container kapanırken thread kapanır
        thread.start()

        return render_template("results.html", keyword=keyword)
    return render_template("index.html")


@app.route("/stream/<keyword>")
def stream(keyword):
    """
    Frontend için server-sent events (SSE) stream.
    """
    def event_stream():
        last_len = 0
        while True:
            if len(results) > last_len:
                for item in results[last_len:]:
                    yield f"data: {json.dumps(item, ensure_ascii=False)}\n\n"
                last_len = len(results)
            time.sleep(1)
    return Response(event_stream(), mimetype="text/event-stream")


@app.route("/download/<keyword>")
def download_csv(keyword):
    """
    Kullanıcıya CSV dosyasını indirme imkanı sağlar.
    """
    filename = f"{keyword}_results.csv"
    filepath = os.path.join(RESULTS_DIR, filename)

    if os.path.exists(filepath):
        return send_file(filepath, as_attachment=True)
    else:
        return f"{filename} bulunamadı.", 404


if __name__ == "__main__":
    # Flask'ı production-ready çalıştırmak için gunicorn kullanıyoruz,
    # ama debug=False ile local test için de çalışır
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=False)
