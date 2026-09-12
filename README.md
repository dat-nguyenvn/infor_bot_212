# Personal Bot

A personal automation bot built with Python. The project provides multiple utilities for interacting with Telegram, scanning web content, and generating AI-powered summaries using an LLM.

## Features

The project currently provides three main functions:

- **Telegram Bot** — Run the Telegram bot service.
- **Website Scanner** — Crawl and collect content from configured websites.
- **LLM Content Summarization** — Process collected content and generate summaries using an LLM.

---

## Project Structure

```text
personal_bot/
│
├── .venv/                  # Python virtual environment
├── requirements.txt        # Python dependencies
│
├── source.py              # Telegram bot
├── scan_web.py            # Website crawler / content scanner
├── agent_ai.py            # LLM-based content summarization
│
└── README.md              # Project documentation

## Installation & Setup
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install --upgrade pip
pip3 install -r requirements.txt
python3 -m playwright install chromium



## Fucntion telegram
python3 source.py

## Function scan website
python3 scan_web.py

## Function summary con