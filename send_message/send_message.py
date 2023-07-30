import requests
import os
from dotenv import load_dotenv

load_dotenv()

env = os.getenv("ENV")

def send_image(image_path: str, chat_id):

    payload = {'chat_id': str(chat_id)}
    file = open(image_path, 'rb')
    files = {'photo': file}

    if env in ["TEST", "LOCAL", "DEV"]:
        response = f"Sending {str(file)}"
        print(response)
        return str(file)
    else:
        response = requests.post(f"{os.environ.get('BOT_URL')}/sendPhoto", files=files, data=payload )
    
    file.close()
    return response

def send_message(message, chat_id):
    payload = {'chat_id': str(chat_id), 'text': message}
    if env in ["TEST", "LOCAL", "DEV"]:
        response = f"Sending '{message}'"
        print(response)
        return message
    else:
        response = requests.post(f"{os.environ.get('BOT_URL')}/sendMessage", data=payload )
    return response