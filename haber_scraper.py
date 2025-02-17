from bs4 import BeautifulSoup
import requests
from datetime import datetime
import pytz

class HaberScraper:
    def __init__(self, url="https://shiftdelete.net/"):
        self.url = url
        self.tz = pytz.timezone("Europe/Istanbul")
        self.now = datetime.now(self.tz)
        self.headers = {"User-Agent": "Mozilla/5.0"}

    def get_news_list(self):
        """Ana sayfadaki haberleri çeker ve 24 saat içinde olanları filtreler."""
        http_response = requests.get(self.url, headers=self.headers)
        soup = BeautifulSoup(http_response.text, "html.parser")
        arrayOfNews = soup.find_all("div", {"class": "td-module-meta-info"}, limit=None)
        
        news_links = []
        for i in arrayOfNews:
            try:
                time_tag = i.find("time")
                title_tag = i.find("h3")

                if time_tag is None or title_tag is None:
                    continue  # Eksikse atla

                given_time_str = time_tag.get("datetime")
                given_time = datetime.fromisoformat(given_time_str).astimezone(self.tz)

                time_difference = (self.now - given_time).total_seconds()

                if abs(time_difference) < 24 * 3600:
                    news_url = title_tag.find("a").get("href")
                    news_links.append([title_tag.get_text(), news_url])

            except Exception as e:
                print(f"Hata oluştu: {e}")

        return news_links

    def get_news_content(self, news_url):
        """Verilen haber linkinin içeriğini çeker ve döndürür."""
        try:
            news_response = requests.get(news_url[1], headers=self.headers)
            soup = BeautifulSoup(news_response.text, "html.parser")

            context = []
            context.append(news_url[0])  # Haber başlığını ekle
            article_body = soup.find_all("div", {"class": "tdb-block-inner td-fix-index"}, limit=None)

            for article in article_body:
                for paragraph in article.find_all("p"):
                    context.append(paragraph.get_text())

            return " ".join(context[:-4])
        except Exception as e:
            print(f"Haber içeriği alınırken hata oluştu: {e}")
            return None

    def get_all_news(self):
        """Tüm haberleri çeker ve içeriklerini döndürür."""
        news_links = self.get_news_list()
        all_news = []

        for link in news_links:
            content = self.get_news_content(link)
            if content:
                all_news.append(content)

        return all_news
    
scraper = HaberScraper()
news = scraper.get_all_news()
for new in news:
    print(new)
    print("\n")