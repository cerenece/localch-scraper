from flask import Flask, render_template, Response, request, send_file
import threading, json, time, csv, os, sys, queue, traceback

# localch_spider.py'nin yolu
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "localch", "localch", "spiders"))
from localch_spider import LocalchSeleniumSpider

app = Flask(__name__)

# Keyword bazlı thread-safe queue'lar
queues_dict = {}

# CSV'lerin kaydedileceği klasör (container içinde /app/results)
RESULTS_DIR = "/app/results"
os.makedirs(RESULTS_DIR, exist_ok=True)


def run_spider(keyword):
    """
    Thread içinde çalışan spider fonksiyonu.
    """
    if keyword not in queues_dict:
        queues_dict[keyword] = queue.Queue()

    try:
        spider = LocalchSeleniumSpider(keyword=keyword)
        start_requests = spider.start_requests()

        for request_obj in start_requests:
            try:
                for item in spider.parse(request_obj):
                    queues_dict[keyword].put(item)

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
                        f.flush()

            except Exception as e:
                print(f"Parse sırasında hata: {e}")
                traceback.print_exc()

    except Exception as e:
        print(f"Spider başlatılamadı: {e}")
        traceback.print_exc()


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        keyword = request.form["keyword"].strip()
        if not keyword:
            return render_template("index.html", error="Keyword boş olamaz!")

        thread = threading.Thread(target=run_spider, args=(keyword,))
        thread.daemon = True
        thread.start()

        return render_template("results.html", keyword=keyword)
    return render_template("index.html")


@app.route("/stream/<keyword>")
def stream(keyword):
    """
    Server-Sent Events ile frontend’e anlık veri gönderimi.
    """
    def event_stream():
        if keyword not in queues_dict:
            queues_dict[keyword] = queue.Queue()

        while True:
            try:
                item = queues_dict[keyword].get_nowait()
                yield f"data: {json.dumps(item, ensure_ascii=False)}\n\n"
            except queue.Empty:
                time.sleep(0.5)  # Daha hızlı SSE tepkisi
            except Exception as e:
                print(f"SSE hatası: {e}")
                traceback.print_exc()
                break

    return Response(event_stream(), mimetype="text/event-stream")


@app.route("/download/<keyword>")
def download_csv(keyword):
    filename = f"{keyword}_results.csv"
    filepath = os.path.join(RESULTS_DIR, filename)

    if os.path.exists(filepath):
        return send_file(filepath, as_attachment=True)
    else:
        return f"{filename} bulunamadı.", 404


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False, threaded=True)
