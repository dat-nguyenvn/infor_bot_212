#from trading212 import Client
import json # For pretty-printing dictionary output
import requests
import time
import datetime

bot_token = "8940816797:AAF7-LWk9eUTUBIZdT0xzgt2QTFtzLNHf0c"
base_url = f"https://api.telegram.org/bot{bot_token}"
chat_id = "7506258548"  # Your personal Telegram chat ID
YOUR212_API_KEY = '32226549ZXSJTeMFfOPVUkwLBfDcLNsSJPeVW'
api_vnsotck="8940816797:AAF7-LWk9eUTUBIZdT0xzgt2QTFtzLNHf0c"
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

from vnstock import Market, Reference, Fundamental
from vnstock import register_user
register_user() # Làm theo hướng dẫn trên terminal

from vnstock import Company


# Thay thế hàm send_vn() cũ bằng cú pháp này
def send_vn(chat_id, symbol="ACB"):
    company = Company(symbol=symbol, source="VCI")
    df = company.overview()

    # 1. In danh sách tất cả các tên cột ra console
    print("--- DANH SÁCH TẤT CẢ CÁC CỘT ---")
    print(df.columns.tolist())

    # 2. Lấy dòng dữ liệu đầu tiên
    row = df.iloc[0]

    # 3. Lấy thông tin symbol, current_price, market_cap
    sym = row.get("symbol", symbol)
    price = row.get("current_price", 0)
    market_cap = row.get("market_cap", 0)

    # Đổi vốn hóa sang đơn vị Tỷ VNĐ cho dễ đọc
    market_cap_billion = market_cap / 1_000_000_000

    # 4. Đóng gói tin nhắn
    msg = (
        f"📊 *THÔNG TIN CỔ PHIẾU {sym}*\n"
        f"💵 Giá hiện tại: *{price:,.0f} VNĐ*\n"
        f"🏦 Vốn hóa thị trường: *{market_cap_billion:,.2f} Tỷ VNĐ*"
    )

    send_text(chat_id, msg)

# Cấu trúc lưu trữ: user_states[chat_id] = {"step": ..., "data": {...}}
user_states = {}


# --- HÀM LẤY GIÁ & VỐN HÓA (TẦNG 1) ---
def send_vn_overview(chat_id, symbol="ACB"):
    company = Company(symbol=symbol, source="VCI")
    df = company.overview()

    row = df.iloc[0]
    sym = row.get("symbol", symbol)
    price = row.get("current_price", 0)
    market_cap = row.get("market_cap", 0)
    market_cap_billion = market_cap / 1_000_000_000

    msg = (
        f"📊 *THÔNG TIN CỔ PHIẾU {sym}*\n"
        f"💵 Giá hiện tại: *{price:,.0f} VNĐ*\n"
        f"🏦 Vốn hóa thị trường: *{market_cap_billion:,.2f} Tỷ VNĐ* \n"
        
    )
    send_text(chat_id, msg)


# --- HÀM LẤY CÔNG TY / CỔ ĐÔNG (TẦNG 2) ---
def send_vn_shareholders(chat_id, symbol="ACB"):
    company = Company(symbol=symbol, source="VCI")
    df = company.overview()
    print(df.columns.tolist())
    row = df.iloc[0]
    sector = row.get("sector", "N/A")
    issue_name = row.get("issue_name", symbol)

    msg = (
        f"📌 *Tên công ty:* {issue_name}\n"
        f"🏭 *Ngành nghề:* {sector}\n"
        f"📊 *Cổ tức:* {row.get('dividend_per_share_tsr', 'N/A')}\n"
        f"💰 *Tỷ lệ cổ đông nước ngoài:* {row.get('foreigner_percentage', 'N/A')}\n"
        f" company_profile : {row.get('company_profile', 'N/A')}\n"
    )
    send_text(chat_id, msg)


# --- HÀM XỬ LÝ LUỒNG NHIỀU BƯỚC ---
def handle_vn_flow(user_chat_id, raw_text, text):
    state = user_states.get(user_chat_id)

    # BƯỚC 1: Mới gõ 'vn' -> Hỏi nhập mã CK
    if not state:
        user_states[user_chat_id] = {"step": "WAITING_SYMBOL", "data": {}}
        send_text(
            user_chat_id,
            "🔤 **Bước 1/2:** Vui lòng nhập mã chứng khoán (VD: FPT, ACB):",
        )

    # BƯỚC 2: Nhận mã CK -> Hỏi tiếp lựa chọn tầng 2
    elif state["step"] == "WAITING_SYMBOL":
        symbol = raw_text.upper()
        user_states[user_chat_id] = {
            "step": "WAITING_ACTION",
            "data": {"symbol": symbol},
        }

        msg = (
            f"📌 Đã chọn mã *{symbol}*.\n"
            f"**Bước 2/2:** Bạn muốn xem thông tin gì?\n"
            f"1️⃣ Gõ `1` - Xem Giá & Vốn hóa\n"
            f"2️⃣ Gõ `2` - Xem Thông tin công ty"
        )
        send_text(user_chat_id, msg)

    # BƯỚC 3: Xử lý lựa chọn và gửi kết quả
    elif state["step"] == "WAITING_ACTION":
        symbol = state["data"]["symbol"]

        if text == "1":
            send_vn_overview(user_chat_id, symbol)
            del user_states[user_chat_id]  # Hoàn tất luồng -> Xóa state
        elif text == "2":
            send_vn_shareholders(user_chat_id, symbol)
            del user_states[user_chat_id]  # Hoàn tất luồng -> Xóa state
        else:
            send_text(
                user_chat_id,
                "⚠️ Lựa chọn không hợp lệ. Vui lòng nhập `1` hoặc `2`.",
            )


def main():
    last_update_id = None
    DATE = datetime.datetime.now()

    while True:
        updates = get_updates(last_update_id)
        for update in updates.get("result", []):
            last_update_id = update["update_id"] + 1
            message = update.get("message")
            if not message:
                continue

            # --- LẤY DỮ LIỆU MESSAGE TRƯỚC KHI DÙNG TRONG IF/ELIF ---
            raw_text = message.get("text", "").strip()
            text = raw_text.lower()
            user_chat_id = message["chat"]["id"]

            # Xử lý theo luồng state hoặc khi gõ 'vn'
            if user_chat_id in user_states or text == "stock":
                handle_vn_flow(user_chat_id, raw_text, text)
            elif text == "image":
                send_photo(user_chat_id, "image.jpg", "📷 Here is your image.")
            elif text == "video":
                send_video(user_chat_id, "video.mp4", "🎥 Here is your video.")
            elif text == "text":
                send_text(user_chat_id, "📝 Here is a text reply.")
            else:
                send_text(
                    user_chat_id, "Send 'image', 'video', 'text' or 'stock'."
                )

        time.sleep(1)


if __name__ == "__main__":
    main()

# ['symbol', 'organ_code', 'current_price', 
# 'market_cap', 'issue_share', 'issue_share', 
# 'issue_share', 'issue_share', 'tag', 'rating',
#  'rating_as_of', 'organ_name', 'organ_short_name', 
#  'com_type_code', 'com_group_code', 'sector', 
#  'average_match_value1_month', 'average_match_volume1_month', 
#  'highest_price1_year', 'lowest_price1_year', 'foreigner_percentage', 
#  'maximum_foreign_percentage', 'state_percentage', 'analyst', 'upside_to_target_percent',
#   'dividend_per_share_tsr', 'projected_tsr_percentage', 'target_price', 'company_profile', 
#   'in_cu', 'icb_code_lv2', 'icb_code_lv4', 'free_float', 'free_float_percentage', 
#   'listing_date', 'first_price', 'first_volume', 'prev_insight', 'fund_info', 'is_bank', 
#   'listing', 'bank']