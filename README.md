AI-Powered News to Podcast Automation

Overview

This project automates the process of extracting daily news from ShiftDelete.net, summarizing the content using pydantic-ai, converting the summaries into speech with Eleven Labs, and publishing the generated audio as a podcast on Spotify using Playwright.

Features

📰 Web Scraping: Fetches daily news articles from ShiftDelete.net

🧠 AI Summarization: Uses pydantic-ai to generate concise and clear summaries

🔊 Text-to-Speech (TTS): Converts summaries into natural-sounding speech via Eleven Labs

🎙 Automated Podcast Upload: Uploads the generated audio as a Spotify podcast using Playwright

⚡ Fully Automated Pipeline: Requires minimal human intervention once set up

Tech Stack

Python 🐍 (Core language)

pydantic-ai 🤖 (AI-powered text summarization)

BeautifulSoup & Requests 🌐 (Web scraping)

Eleven Labs API 🔉 (Text-to-Speech conversion)

Playwright 🎭 (Spotify podcast automation)

Installation

Prerequisites

Ensure you have Python 3.8+ installed and the following dependencies:

pip install beautifulsoup4 requests pydantic-ai playwright elevenlabs

Initialize Playwright:

playwright install

Usage

Run the script to fetch news, summarize, generate audio, and upload to Spotify:

python main.py

The process runs automatically, generating a podcast episode for the latest news.

Configuration

Eleven Labs API Key: Set your API key in config.py

Spotify Credentials: Store your login credentials securely for automated upload

Scraping Parameters: Modify the scraping logic in scraper.py if needed

Roadmap



Contributing

Pull requests are welcome! Feel free to submit issues and suggestions to improve the project.

License

This project is licensed under the MIT License.
