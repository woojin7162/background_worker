import os
import time
from datetime import datetime, timedelta
from pymongo import MongoClient
import requests
import urllib.parse

MONGODB_URI = os.environ.get("MONGODB_URI")
DISCORD_WEBHOOK_URL = os.environ.get("DISCORD_WEBHOOK_URL")

client = MongoClient(MONGODB_URI)
db = client["Cluster0"]  # 실제 DB 이름으로 변경
collection = db["scheduled_messages"]


def send_notilab_push(body):
    to_nickname = "Shift_Alarm"  # notilab 앱 닉네임
    title = "교대근무 알리미"
    sckey = "89150194-88f3-4b84-ac93-6f9b4fa91ce9"
    url = (
        "https://noti.kyulabs.app/send?"
        f"to={urllib.parse.quote(to_nickname)}"
        f"&title={urllib.parse.quote(title)}"
        f"&body={urllib.parse.quote(body)}"
        f"&secretKey={urllib.parse.quote(sckey)}"
    )
    try:
        resp = requests.get(url, timeout=5)
        print("notilab 응답:", resp.status_code, resp.text)
    except Exception as e:
        print("notilab 푸시 전송 오류:", e)

def process_scheduled_messages():
    now = datetime.utcnow() + timedelta(hours=9)
    messages = list(collection.find({"run_time": {"$lte": now}}))
    for msg in messages:
        send_notilab_push(msg["content"])
        collection.delete_one({"_id": msg["_id"]})  

if __name__ == "__main__":
    print("[워커] 스케줄러 워커 시작")
    already_deleted_today = False
    while True:
        process_scheduled_messages()
        time.sleep(10)
