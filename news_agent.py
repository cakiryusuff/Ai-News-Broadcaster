import datetime
from pydantic import BaseModel, Field
from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIModel
from dotenv import load_dotenv
from playwright.sync_api import sync_playwright
import nest_asyncio
import os
from haber_scraper import HaberScraper
from text_to_speech import ElevenLabsClient

nest_asyncio.apply()
load_dotenv()

class ResearchResults(BaseModel):
    summary: str = Field(description="summary of the news")
    title: str = Field(description="title of the podcast")
    description: str = Field(description="description of the podcast")

class NewsFetcher:
    """Haberleri çeken sınıf"""
    def __init__(self):
        self.scraper = HaberScraper()
        self.openai_model = OpenAIModel("gpt-4o-mini")
        self.agent = Agent(
            self.openai_model,
            result_type= ResearchResults,
            system_prompt=(
                "You are an assistant that summarizes daily news in a clear and understandable way."
                "Given a list of news articles, provide a summary of the news."
                "This news gonna be used in a podcast and youtube videos. So make it clear and understandable."
                "Separate the news with a new line."
                "make a general title and description for podcast from summariezed news."
                "Title should be short and clear and contains the today's date."
                "to get today's date use get_date tool."
                "Do it in Turkish."
                "in summary numbers should be written in words. except for title and description. Just only in summary."
                "For example, 1,499 should be written as 'bin dört yüz doksan dokuz'."
                "To get todays news use get_news tool."
            ),
        )
        
        @self.agent.tool_plain
        def get_date() -> str: return datetime.datetime.now().strftime('%d.%m.%Y')
        
        @self.agent.tool_plain
        def get_news() -> list[str]: return self.scraper.get_all_news()

    def get_summary(self) -> ResearchResults:
        """Haber özetini alır."""
        result = self.agent.run_sync("Give me today's news")
        return result.data


class TextToSpeech:
    """Metni ses dosyasına dönüştüren sınıf"""
    def __init__(self):
        self.client = ElevenLabsClient()

    def convert_text(self, text: str, output_file="output.mp3"):
        """Verilen metni ses dosyasına çevirir."""
        self.client.convert_text_to_audio(text, output_file=output_file)


class PodcastUploader:
    """Spotify Podcast yükleyici sınıfı"""
    def __init__(self, email: str, password: str, audio_file: str, title, description):
        self.email = email
        self.password = password
        self.audio_file = audio_file
        self.title = title
        self.description = description

    def upload_podcast(self):
        """Spotify Podcasters platformuna podcast yükler."""
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False)
            page = browser.new_page()
            page.goto('https://podcasters.spotify.com/')
            page.wait_for_timeout(1000)

            # Giriş Yap
            page.click('text=Oturum aç')
            page.wait_for_timeout(1000)
            page.click('text=Spotify ile devam et')
            page.wait_for_timeout(1000)
            page.fill('#login-username', self.email)
            page.wait_for_timeout(1000)
            page.fill('#login-password', self.password)
            page.wait_for_timeout(1000)
            page.click('#login-button')
            page.wait_for_timeout(3000)

            page.goto('https://creators.spotify.com/pod/dashboard/episode/wizard')
            page.wait_for_timeout(3000)

            page.set_input_files('input[type="file"]', self.audio_file)
            page.wait_for_timeout(5000)

            page.fill('input[name="title"]', self.title)
            page.wait_for_timeout(2000)
            page.fill('div[contenteditable="true"]', self.description)
            page.wait_for_timeout(2000)

            page.click('button[type="submit"]')
            page.wait_for_timeout(10000)
            page.locator("label:has-text('Şimdi')").click()
            page.wait_for_timeout(2000)
            page.click("button[data-encore-id='buttonPrimary']")
            page.wait_for_timeout(10000)

            browser.close()


def run():
    """Tüm işlemleri sırasıyla çalıştıran fonksiyon"""
    email = os.getenv("SPOTIFY_EMAIL")
    password = os.getenv("SPOTIFY_PASSWORD")
    output_file = f"C:/news_creater/sounds/{int(datetime.datetime.timestamp(datetime.datetime.now()))}.mp3"

    news_fetcher = NewsFetcher()
    summary = news_fetcher.get_summary()
    print(summary)

    tts = TextToSpeech()
    tts.convert_text(summary.summary, output_file=output_file)

    uploader = PodcastUploader(email, password, output_file, summary.title, summary.description)
    uploader.upload_podcast()


if __name__ == "__main__":
    run()
