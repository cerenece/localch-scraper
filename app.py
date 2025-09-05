from flask import Flask, render_template, Response, request, send_file
import threading, json, time, csv, os, sys, queue

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

    spider = LocalchSeleniumSpider(keyword=keyword, results_queue=queues_dict[keyword])

    for request_obj in spider.start_requests():
        for _ in spider.parse(request_obj):
            # Spider içinde queue ve CSV işlemleri yapılıyor
            pass


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        keyword = request.form["keyword"]

        thread = threading.Thread(target=run_spider, args=(keyword,))
        thread.daemon = True
        thread.start()

        return render_template("results.html", keyword=keyword)
    return render_template("index.html")


@app.route("/stream/<keyword>")
def stream(keyword):
    """
    Frontend için server-sent events (SSE) stream.
    """
    def event_stream():
        if keyword not in queues_dict:
            queues_dict[keyword] = queue.Queue()

        while True:
            try:
                item = queues_dict[keyword].get_nowait()
                yield f"data: {json.dumps(item, ensure_ascii=False)}\n\n"
            except queue.Empty:
                time.sleep(1)

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
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=False)
