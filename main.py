import datetime
from pydantic import BaseModel, Field
from pydantic_ai import Agent, ModelRetry
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
    def __init__(self):
        self.scraper = HaberScraper()
        self.openai_model = OpenAIModel("gpt-4o-mini")
        self.agent = Agent(
            self.openai_model,
            result_type= ResearchResults,
            system_prompt=(
                "You are an AI assistant that summarizes daily news clearly and concisely in Turkish."
                "Given a list of news articles, generate a structured summary that is easy to understand."
                "These summaries will be used for a podcast and YouTube videos, so they should be engaging and well-structured."
                "Separate each news item with a new line for better readability."
                "Generate a general title and description for the podcast based on the summarized news."
                "The title should be short, clear, and include today's date (use the get_date tool to retrieve it, e.g. 'title - date')."
                "In the summary, numbers should be written in words (e.g., 1,499 → bin dört yüz doksan dokuz), except for the title and description."
                "To get today's news, use the get_news tool."
            ),
            retries=2
        )
        
        @self.agent.tool_plain
        def get_date() -> str: return datetime.datetime.now().strftime('%d.%m.%Y')
        
        @self.agent.tool_plain
        def get_news() -> list[str]: return self.scraper.get_all_news()
        
        @self.agent.result_validator
        def result_validator(data: ResearchResults):
            if datetime.datetime.now().strftime('%d.%m.%Y') not in data.title:
                raise ModelRetry("Title date is written in words. Write it in numbers. (e.g., 1.02.2022)")
            return data

    def get_summary(self) -> ResearchResults:
        result = self.agent.run_sync("Give me today's news")
        return result.data


class TextToSpeech:
    def __init__(self):
        self.client = ElevenLabsClient()

    def convert_text(self, text: str, output_file="output.mp3"):
        self.client.convert_text_to_audio(text, output_file=output_file)


class PodcastUploader:
    def __init__(self, email: str, password: str, audio_file: str, title, description):
        self.email = email
        self.password = password
        self.audio_file = audio_file
        self.title = title
        self.description = description

    def upload_podcast(self):
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
    email = os.getenv("SPOTIFY_EMAIL")
    password = os.getenv("SPOTIFY_PASSWORD")
    output_file = f"C:/news_creater/sounds/{datetime.datetime.timestamp(datetime.datetime.now())}.mp3"

    news_fetcher = NewsFetcher()
    summary = news_fetcher.get_summary()
    print("*"*10,"Summary getted","*"*10)

    tts = TextToSpeech()
    tts.convert_text(summary.summary, output_file=output_file)
    print("*"*10,"Text to speech done","*"*10)

    uploader = PodcastUploader(email, password, output_file, summary.title, summary.description)
    uploader.upload_podcast()
    print("*"*10,"Podcast uploaded","*"*10)


if __name__ == "__main__":
    run()