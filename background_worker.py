import os
import time
from datetime import datetime, timedelta
from pymongo import MongoClient
import requests
from discord import Webhook


MONGODB_URI = os.environ.get("MONGODB_URI")
DISCORD_WEBHOOK_URL = os.environ.get("DISCORD_WEBHOOK_URL")

client = MongoClient(MONGODB_URI)
db = client["Cluster0"]  # 실제 DB 이름으로 변경
collection = db["scheduled_messages"]

def send_discord_message(content, db_id):
    url = DISCORD_WEBHOOK_URL
    if "?wait=true" not in url:
        url += "?wait=true"
    payload = {
        "content": content,
        "username": "교대근무 알리미"
    }

    try:
        resp = requests.post(url, json=payload, timeout=5)
        print("웹훅 응답:", resp.status_code, resp.text)
        # 메시지 ID 저장 관련 코드 삭제됨
    except Exception as e:
        print("웹훅 전송 오류:", e)


def process_scheduled_messages():
    now = datetime.utcnow() + timedelta(hours=9)
    messages = list(collection.find({"run_time": {"$lte": now}}))
    for msg in messages:
        send_discord_message(msg["content"], msg["_id"])
        collection.delete_one({"_id": msg["_id"]})  

if __name__ == "__main__":
    print("[워커] 스케줄러 워커 시작")
    already_deleted_today = False
    while True:
        process_scheduled_messages()
        time.sleep(10)
