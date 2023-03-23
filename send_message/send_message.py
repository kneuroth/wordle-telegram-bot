import requests
import os

def send_image(image_path: str):

    payload = {'chat_id': os.environ.get('CHAT_ID')}
    file = open(image_path, 'rb')
    files = {'photo': file}
    response = requests.post(f"{os.environ.get('BOT_URL')}/sendPhoto", files=files, data=payload )
    
    file.close()
    return response

def send_message(message):
    payload = {'chat_id': os.environ.get('CHAT_ID'), 'text': message}
    return requests.post(f"{os.environ.get('BOT_URL')}/sendMessage", data=payload )