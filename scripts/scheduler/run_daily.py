import schedule
import time
import os

def job():
    print("\nRunning Daily AI Pipeline...\n")
    os.system("python scripts/run_pipeline.py")

# ✅ DAILY RUN (Production)
schedule.every().day.at("10:00").do(job)

# 🔥 TEST MODE (Every 1 minute)
schedule.every(1).minutes.do(job)

print("⏳ Scheduler started... Waiting for next run...")

while True:
    schedule.run_pending()
    time.sleep(60)