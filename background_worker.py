import os
import time
from datetime import datetime, timedelta
from pymongo import MongoClient
import requests

MONGODB_URI = os.environ.get("MONGODB_URI")
DISCORD_WEBHOOK_URL = os.environ.get("DISCORD_WEBHOOK_URL")

client = MongoClient(MONGODB_URI)
db = client["Cluster0"]  # 실제 DB 이름으로 변경
collection = db["scheduled_messages"]

def send_discord_message(content):
    print(f"[워커] send_discord_message 실행됨: {content}")
    if not DISCORD_WEBHOOK_URL:
        print("웹훅 URL이 설정되지 않았습니다.")
        return
    payload = {
        "content": content,
        "username": "교대근무 알리미"
    }
    try:
        resp = requests.post(DISCORD_WEBHOOK_URL, json=payload, timeout=5)
        print("웹훅 응답:", resp.status_code, resp.text)
    except Exception as e:
        print("웹훅 전송 오류:", e)

def process_scheduled_messages():
    now = datetime.utcnow() + timedelta(hours=9)
    # 예약 시간이 지난 메시지 모두 조회
    messages = list(collection.find({"run_time": {"$lte": now}}))
    for msg in messages:
        send_discord_message(msg["content"])
        # 전송 후 삭제
        collection.delete_one({"_id": msg["_id"]})

if __name__ == "__main__":
    print("[워커] 스케줄러 워커 시작")
    while True:
        process_scheduled_messages()
        time.sleep(10)
