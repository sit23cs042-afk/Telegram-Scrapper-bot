"""
Keep-alive script to ping the service and prevent spin-down
Run this as a cron job externally or use a service like UptimeRobot
"""
import requests
import time

SERVICE_URL = "https://telegram-discount-bot-g6ip.onrender.com/health"

def ping_service():
    try:
        response = requests.get(SERVICE_URL, timeout=10)
        if response.status_code == 200:
            print(f"✅ Service is alive: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        else:
            print(f"⚠️ Service returned {response.status_code}")
    except Exception as e:
        print(f"❌ Failed to ping service: {e}")

if __name__ == "__main__":
    while True:
        ping_service()
        # Ping every 10 minutes
        time.sleep(600)
