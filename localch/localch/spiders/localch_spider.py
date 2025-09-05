import scrapy
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from pprint import pprint
import time

class LocalchSeleniumSpider(scrapy.Spider):
    name = "localch"

    def __init__(self, keyword=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not keyword:
            raise ValueError("Keyword parametresi gerekli!")
        self.keyword = keyword

    def start_requests(self):
        options = webdriver.ChromeOptions()
        options.add_argument("--start-maximized")
        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        self.wait = WebDriverWait(self.driver, 10)

        start_url = f"https://www.local.ch/de/s/{self.keyword}?what={self.keyword}"
        yield scrapy.Request(url=start_url, callback=self.parse)

    def parse(self, response):
        self.driver.get(response.url)
        time.sleep(2)

        # Çerez popup varsa kapat
        try:
            cookie_button = self.wait.until(
                EC.element_to_be_clickable((By.ID, "onetrust-accept-btn-handler"))
            )
            cookie_button.click()
            time.sleep(1)
        except:
            pass

        page_count = 1
        while True:
            print(f"\n--- Sayfa {page_count} ---")

            # Firma linklerini çek
            articles = self.driver.find_elements(By.CSS_SELECTOR, "div.kg a")
            detail_links = [a.get_attribute("href") for a in articles]

            for idx, link in enumerate(detail_links, start=1):
                # Yeni tab aç
                self.driver.execute_script("window.open(arguments[0]);", link)
                self.driver.switch_to.window(self.driver.window_handles[1])
                time.sleep(2)

                # Firma bilgilerini al
                try:
                    firma_adi = self.wait.until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, "h1[data-cy='header-title']"))
                    ).text.strip()
                except:
                    firma_adi = "Yok"

                try:
                    adres = self.driver.find_element(By.CSS_SELECTOR, "address").text.strip()
                except:
                    try:
                        adres_elem = self.driver.find_element(By.CSS_SELECTOR, "div[data-cy='detail-map-preview'] button")
                        adres = adres_elem.text.strip()
                    except:
                        adres = "Yok"

                # Telefonlar
                try:
                    telefon_elems = self.driver.find_elements(By.CSS_SELECTOR, "li.r2 a[href^='tel:']")
                    telefonlar = [t.get_attribute("href").replace("tel:", "").strip() for t in telefon_elems]
                except:
                    telefonlar = []

                # Email
                try:
                    email_elems = self.driver.find_elements(By.CSS_SELECTOR, "li.r2 a[href^='mailto:']")
                    emailler = [e.get_attribute("href").replace("mailto:", "").strip() for e in email_elems]
                except:
                    emailler = []

                # Website
                try:
                    website_elems = self.driver.find_elements(By.CSS_SELECTOR, "li.r2 a[href^='http']")
                    websiteler = [w.get_attribute("href").strip() for w in website_elems]
                except:
                    websiteler = []

                # Sonuç sözlüğü
                result = {
                    "Firma Adı": firma_adi,
                    "Adres": adres,
                    "Telefon": telefonlar,
                    "Email": emailler,
                    "Website": websiteler,
                    "URL": link
                }

                # Terminalde okunabilir şekilde yazdır
                print("\n------ Firma Bilgisi ------")
                pprint(result)
                print("----------------------------\n")

                # Veriyi Scrapy’ye ilet
                yield result

                # Tabı kapat ve ana sekmeye dön
                self.driver.close()
                self.driver.switch_to.window(self.driver.window_handles[0])
                time.sleep(1)

            # Sonraki sayfa
            try:
                next_button = self.driver.find_element(By.ID, "load-next-page")
                self.driver.execute_script("arguments[0].scrollIntoView(true);", next_button)
                self.driver.execute_script("arguments[0].click();", next_button)
                page_count += 1
                time.sleep(3)
            except:
                print("Son sayfaya ulaşıldı veya next buton bulunamadı.")
                break

        self.driver.quit()
