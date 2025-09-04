import csv

class LocalchPipeline:
    def open_spider(self, spider):
        self.file = open(f"{spider.keyword}_results.csv", "w", newline="", encoding="utf-8")
        self.writer = csv.DictWriter(self.file, fieldnames=[
            "Firma Adı", "Adres", "Telefon", "Email", "Website", "URL"
        ])
        self.writer.writeheader()

    def close_spider(self, spider):
        self.file.close()

    def process_item(self, item, spider):
        self.writer.writerow({
            "Firma Adı": item.get("Firma Adı", "Yok"),
            "Adres": item.get("Adres", "Yok"),
            "Telefon": item.get("Telefon", "Yok"),
            "Email": item.get("Email", "Yok"),
            "Website": item.get("Website", "Yok"),
            "URL": item.get("URL", "Yok"),
        })
        self.file.flush()  # <<< her satırdan sonra flush ile anlık yazdır
        return item
