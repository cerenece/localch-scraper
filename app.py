from flask import Flask, render_template, Response, request
import threading, json, time, csv
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "localch", "localch", "spiders"))
from localch_spider import LocalchSeleniumSpider


app = Flask(__name__)
results = []

def run_spider(keyword):
    global results
    results = []

    spider = LocalchSeleniumSpider(keyword=keyword)

    # start_requests generator’ını al
    start_requests = spider.start_requests()

    for request in start_requests:
        for item in spider.parse(request):
            results.append(item)
            # CSV kaydı
            with open(f"{keyword}_results.csv", "a", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=["Firma Adı","Adres","Telefon","Email","Website","URL"])
                writer.writerow({
                    "Firma Adı": item.get("Firma Adı", "Yok"),
                    "Adres": item.get("Adres", "Yok"),
                    "Telefon": ",".join(item.get("Telefon", [])),
                    "Email": ",".join(item.get("Email", [])),
                    "Website": ",".join(item.get("Website", [])),
                    "URL": item.get("URL", "Yok")
                })
                f.flush()


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        keyword = request.form["keyword"]
        thread = threading.Thread(target=run_spider, args=(keyword,))
        thread.start()
        return render_template("results.html", keyword=keyword)
    return render_template("index.html")


@app.route("/stream/<keyword>")
def stream(keyword):
    def event_stream():
        last_len = 0
        while True:
            if len(results) > last_len:
                for item in results[last_len:]:
                    yield f"data: {json.dumps(item)}\n\n"
                last_len = len(results)
            time.sleep(1)
    return Response(event_stream(), mimetype="text/event-stream")

app.route("/download/<keyword>")
def download_csv(keyword):
    filename = f"{keyword}_results.csv"
    filepath = os.path.join(os.getcwd(), filename)
    if os.path.exists(filepath):
        return send_file(filepath, as_attachment=True)
    else:
        return f"{filename} bulunamadı.", 404

if __name__ == "__main__":
    # Debug'ı kapatmak prod için daha sağlıklı
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=False)