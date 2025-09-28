from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import requests
import os
import time
from urllib.parse import urlparse
from tqdm import tqdm

class ImageFetcher:
    def __init__(self, headless=True):
        options = Options()
        if headless:
            options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        
        self.driver = webdriver.Chrome(options=options)
        self.wait = WebDriverWait(self.driver, 10)
    
    def search_bing(self, query, num_images=5):
        self.driver.get("https://www.bing.com/images")
        search_box = self.wait.until(EC.presence_of_element_located((By.NAME, "q")))
        search_box.send_keys(query + Keys.RETURN)
        time.sleep(3)
        
        # Scroll to load more images
        for _ in range(max(1, num_images // 20)):
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)
        
        images = self.driver.find_elements(By.CSS_SELECTOR, "img.mimg")
        urls = []
        for img in images:
            url = img.get_attribute("src")
            if url and url.startswith("http") and len(url) > 50:
                urls.append(url)
                if len(urls) >= num_images:
                    break
        return urls
    
    def download_image(self, url, filename):
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            with open(filename, 'wb') as f:
                f.write(response.content)
            return True
        except:
            return False
    
    def fetch_images(self, query, num_images=5, download_dir="images"):
        class_dir = os.path.join(download_dir, query.replace(' ', '_'))
        os.makedirs(class_dir, exist_ok=True)
        
        urls = self.search_bing(query, num_images)
        if not urls:
            print(f"No images found for {query}!")
            return
        
        successful = 0
        for i, url in enumerate(tqdm(urls, desc=f"Downloading {query}")):
            filename = os.path.join(class_dir, f"{i+1}.jpg")
            if self.download_image(url, filename):
                successful += 1
        
        print(f"{query}: Downloaded {successful}/{len(urls)} images")
    
    def fetch_multiple_classes(self, classes, num_images=5, download_dir="images"):
        for class_name in tqdm(classes, desc="Processing classes"):
            self.fetch_images(class_name, num_images, download_dir)
    
    def close(self):
        self.driver.quit()

if __name__ == "__main__":
    fetcher = ImageFetcher(headless=True)
    
    try:
        # fetcher.fetch_images("โรคใบขาวในอ้อย", num_images=100)
        diseases = ["โรคใบขาวในอ้อย", "โรคแส้ดำในอ้อย", "โรคเน่าคออ้อย","โรคใบจุดวงแหวนในอ้อย"]
        fetcher.fetch_multiple_classes(diseases, num_images=20)
    except KeyboardInterrupt:
        print("\nStopped by user")
    finally:
        fetcher.close()