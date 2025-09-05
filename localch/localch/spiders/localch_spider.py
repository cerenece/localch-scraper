import scrapy
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time, json, os

class LocalchSeleniumSpider(scrapy.Spider):
    name = "localch"

    def __init__(self, keyword=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not keyword:
            raise ValueError("Keyword parametresi gerekli!")
        self.keyword = keyword

    def start_requests(self):
        options = Options()
        options.binary_location = os.environ.get("CHROMIUM_PATH", "/usr/bin/chromium")
    
        # Railway optimizasyonları
        options.add_argument("--headless=new")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument("--disable-software-rasterizer")
        options.add_argument("--disable-extensions")
        options.add_argument("--disable-background-networking")
        options.add_argument("--disable-sync")
        options.add_argument("--disable-translate")
        options.add_argument("--disable-features=VizDisplayCompositor")
        options.add_argument("--window-size=1920,1080")
        options.add_argument("--single-process")       # 🔑 RAM azaltıyor
        options.add_argument("--disable-dev-tools")    # 🔑 DevTools kapalı
        options.add_argument("--no-zygote")            # 🔑 Zygote process kapalı
        options.add_argument("--disable-features=SitePerProcess") # 🔑 Tab crash azaltır

    self.driver = webdriver.Chrome(
        service=Service(os.environ.get("CHROMEDRIVER_PATH", "/usr/bin/chromedriver")),
        options=options
    )
    self.wait = WebDriverWait(self.driver, 10)

    start_url = f"https://www.local.ch/de/s/{self.keyword}?what={self.keyword}"
    yield scrapy.Request(url=start_url, callback=self.parse)

    def parse(self, response):
        self.driver.get(response.url)
        time.sleep(2)
        # Çerez popup
        try:
            cookie_button = self.wait.until(
                EC.element_to_be_clickable((By.ID,"onetrust-accept-btn-handler"))
            )
            cookie_button.click()
            time.sleep(1)
        except: pass

        page_count = 1
        while True:
            articles = self.driver.find_elements(By.CSS_SELECTOR,"div.kg a")
            detail_links = [a.get_attribute("href") for a in articles]

            for link in detail_links:
                self.driver.execute_script("window.open(arguments[0]);", link)
                self.driver.switch_to.window(self.driver.window_handles[1])
                time.sleep(2)

                # Firma bilgileri
                try: firma_adi = self.wait.until(
                    EC.presence_of_element_located((By.CSS_SELECTOR,"h1[data-cy='header-title']"))
                ).text.strip()
                except: firma_adi="Yok"

                try: adres=self.driver.find_element(By.CSS_SELECTOR,"address").text.strip()
                except: adres="Yok"

                try:
                    telefon_elems=self.driver.find_elements(By.CSS_SELECTOR,"li.r2 a[href^='tel:']")
                    telefonlar=[t.get_attribute("href").replace("tel:","").strip() for t in telefon_elems]
                except: telefonlar=[]

                try:
                    email_elems=self.driver.find_elements(By.CSS_SELECTOR,"li.r2 a[href^='mailto:']")
                    emailler=[e.get_attribute("href").replace("mailto:","").strip() for e in email_elems]
                except: emailler=[]

                try:
                    website_elems=self.driver.find_elements(By.CSS_SELECTOR,"li.r2 a[href^='http']")
                    websiteler=[w.get_attribute("href").strip() for w in website_elems]
                except: websiteler=[]

                result = {
                    "Firma Adı":firma_adi,
                    "Adres":adres,
                    "Telefon":telefonlar,
                    "Email":emailler,
                    "Website":websiteler,
                    "URL":link
                }

                print(json.dumps(result, ensure_ascii=False))
                yield result

                self.driver.close()
                self.driver.switch_to.window(self.driver.window_handles[0])
                time.sleep(1)

            # Sonraki sayfa
            try:
                next_button=self.driver.find_element(By.ID,"load-next-page")
                self.driver.execute_script("arguments[0].scrollIntoView(true);", next_button)
                self.driver.execute_script("arguments[0].click();", next_button)
                page_count+=1
                time.sleep(3)
            except: break

        self.driver.quit()
