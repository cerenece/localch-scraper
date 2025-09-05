from flask import Flask, render_template, Response, request, send_file
import threading, json, time, csv, os, queue
from flask import Flask, render_template, Response, request
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "localch", "localch", "spiders"))
from localch_spider import LocalchSeleniumSpider


app = Flask(__name__)

# Thread-safe queue
queues_dict = {}

# CSV klasörü
RESULTS_DIR = "/app/results"
os.makedirs(RESULTS_DIR, exist_ok=True)

def run_spider(keyword):
    if keyword not in queues_dict:
        queues_dict[keyword] = queue.Queue()

    spider = LocalchSeleniumSpider(keyword=keyword)
    start_requests = spider.start_requests()

    for request_obj in start_requests:
        for item in spider.parse(request_obj):
            queues_dict[keyword].put(item)

            csv_file = os.path.join(RESULTS_DIR, f"{keyword}_results.csv")
            write_header = not os.path.exists(csv_file)

            with open(csv_file, "a", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(
                    f,
                    fieldnames=["Firma Adı","Adres","Telefon","Email","Website","URL"]
                )
                if write_header:
                    writer.writeheader()
                writer.writerow({
                    "Firma Adı": item.get("Firma Adı","Yok"),
                    "Adres": item.get("Adres","Yok"),
                    "Telefon": ",".join(item.get("Telefon",[])),
                    "Email": ",".join(item.get("Email",[])),
                    "Website": ",".join(item.get("Website",[])),
                    "URL": item.get("URL","Yok")
                })
                f.flush()

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
    filepath = os.path.join(RESULTS_DIR, f"{keyword}_results.csv")
    if os.path.exists(filepath):
        return send_file(filepath, as_attachment=True)
    return f"{keyword}_results.csv bulunamadı", 404

if __name__ == "__main__":
    import os
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT",5000)), debug=False)
