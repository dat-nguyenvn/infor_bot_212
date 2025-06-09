from trading212 import Client
import json # For pretty-printing dictionary output
import requests
import time

bot_token = "7922294374:AAFrRbKKP-c88H5GpztN9VR8GxjqYgECT5o"
base_url = f"https://api.telegram.org/bot{bot_token}"
chat_id = "7506258547"  # Your personal Telegram chat ID

def send_text(chat_id, text):
    url = f"{base_url}/sendMessage"
    data = {"chat_id": chat_id, "text": text}
    requests.post(url, data=data)

def send_photo(chat_id, photo_path, caption=""):
    url = f"{base_url}/sendPhoto"
    with open(photo_path, "rb") as photo:
        files = {"photo": photo}
        data = {"chat_id": chat_id, "caption": caption}
        requests.post(url, files=files, data=data)

def send_video(chat_id, video_path, caption=""):
    url = f"{base_url}/sendVideo"
    with open(video_path, "rb") as video:
        files = {"video": video}
        data = {"chat_id": chat_id, "caption": caption}
        requests.post(url, files=files, data=data)

def get_updates(offset=None):
    url = f"{base_url}/getUpdates"
    params = {"timeout": 100, "offset": offset}
    response = requests.get(url, params=params)
    return response.json()


# Your API key (make sure to replace with your actual key if different)
YOUR212_API_KEY = '32226549ZXSJTeMFfOPVUkwLBfDcLNsSJPeVW'


def main():
    last_update_id = None
    while True:

        updates = get_updates(last_update_id)
        for update in updates["result"]:
            last_update_id = update["update_id"] + 1
            message = update.get("message")
            if not message:
                continue
            text = message.get("text", "").lower()
            user_chat_id = message["chat"]["id"]

            if text == "image":
                send_photo(user_chat_id, "./personal_bot/image.jpg", "📷 Here is your image.")
            elif text == "video":
                send_video(user_chat_id, "./personal_bot/video.mp4", "🎥 Here is your video.")
            elif text == "text":
                send_text(user_chat_id, "📝 Here is a text reply.")               
            elif text == "212":
                client = Client(YOUR212_API_KEY)

                # --- 1. Get and print Account Cash Summary ---
                print("--- Account Cash Summary ---")
                account_summary = client.get_account_cash()
                # The 'account_summary' object has attributes like .total, .free, .invested, .currency
                print(f"Total Funds: {account_summary['total']} ")
                print(f"Free Funds: {account_summary['free']} ")
                print(f"Invested Funds: {account_summary['invested']} ")
                print("-" * 30 + "\n")
                send_text(user_chat_id, f"Total: {account_summary['total']} \nFree Funds: {account_summary['free']} \nInvested Funds: {account_summary['invested']}")
            else:
                send_text(user_chat_id, "Send 'image', 'video', or 'text'.")

        time.sleep(1)

if __name__ == "__main__":
    main()


