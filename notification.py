import requests
import os
apiKey = os.environ.get('TELEGRAM_API_KEY')
chatId = os.environ.get('TELEGRAM_CHAT_ID')
if not apiKey or not chatId:
    print("Error: Missing Telegram API key or chat ID environment variables.")
    exit(1)

def send_notification(status, targetDate):
    #Decide message based off status
    if status == "Success":
        message = f"🎉Pilates class successfully booked for {targetDate}.🎉"
    else:
        if status == "Login Error":
            message = f"⚠️ Error logging in to booking site. ⚠️"
        elif status == "Navigation Error":
            message = f"⚠️ Error navigating to Pilates class. Either {targetDate} is not available for selection yet or Pilates is not available on {targetDate}. ⚠️"
        elif status == "Booking Error":
            message = f"⚠️ Error booking the Pilates class for {targetDate}. ⚠️"
        print(f"ERROR: {message}")

    # Replace with your actual webhook URL
    webhook_url = f"https://api.telegram.org/bot{apiKey}/sendMessage"
    payload = {
        "chat_id": chatId,
        "text": message
    }
    
    try:
        response = requests.post(webhook_url, json=payload)
        response.raise_for_status()
        print("Notification sent successfully.")
    except requests.exceptions.RequestException as e:
        print(f"Failed to send notification: {e}")