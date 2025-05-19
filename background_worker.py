import os
import time
from datetime import datetime, timedelta
from sqlalchemy import create_engine, text
import requests

DATABASE_URL = os.environ.get("DATABASE_URL")
DISCORD_WEBHOOK_URL = os.environ.get("DISCORD_WEBHOOK_URL")

engine = create_engine(DATABASE_URL)

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
    now = datetime.utcnow() + timedelta(hours=9)  # Flask와 동일하게 한국시간 기준
    with engine.begin() as conn:
        # 예약 시간이 지난 메시지 조회
        result = conn.execute(
            text("SELECT id, content FROM scheduled_messages WHERE run_time <= :now"),
            {"now": now}
        )
        rows = result.fetchall()
        for row in rows:
            send_discord_message(row["content"])
            # 전송 후 삭제
            conn.execute(
                text("DELETE FROM scheduled_messages WHERE id = :id"),
                {"id": row["id"]}
            )

if __name__ == "__main__":
    print("[워커] 스케줄러 워커 시작")
    while True:
        process_scheduled_messages()
        time.sleep(10)  # 10초마다 체크