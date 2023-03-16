from dotenv import load_dotenv
from flask import current_app
from threading import Thread

import os, requests

load_dotenv()
RECAPTCHA_SECRET_KEY = os.getenv("RECAPTCHA_SECRET_KEY")

def is_human(captcha_response, User_IP):
    data = {'response': captcha_response, 'secret': RECAPTCHA_SECRET_KEY, 'remoteip':User_IP}
    r = requests.post("https://www.google.com/recaptcha/api/siteverify", data=data)
    return r.json()


def avatar_download(first_name, last_name, cid):
    if first_name == "None":
        r = requests.get(f"https://ui-avatars.com/api/?background=5c9f24&color=fff&size=256&name={cid}&bold=true")
    elif first_name != "None":
        r = requests.get(f"https://ui-avatars.com/api/?background=5c9f24&color=fff&size=256&name={first_name}+{last_name}&bold=true")

    if r.status_code == 200:

        save_image = "website/static/public/initials" + "/" + str(cid) + ".png"
        with open(save_image, 'wb') as file:
            file.write(r.content)
        file.close()

    return


FILE_UPLOAD_EXTENSIONS = ["PNG", "JPG", "JPEG", "GIF"]


def allowedextensions(imagename):
    if not "." in imagename:
        return False

    extension = imagename.rsplit(".", 1)[1]

    if extension.upper() in FILE_UPLOAD_EXTENSIONS:
        return True
    else:
        return False


def allowed_image_size(imagesize):

    if int(imagesize) <= 2.0 * 1024 * 1024:
        return True
    else:
        return False

def post_async_message(app, DISCORD_ENDPOINT, DISCORD_CHANNEL_ID, data, headers):
    with app.app_context():
        requests.post(f"{DISCORD_ENDPOINT}/v9/channels/{DISCORD_CHANNEL_ID}/messages", data=data, headers=headers)


def post_discord_message(data, DISCORD_BOT_TOKEN, DISCORD_ENDPOINT, DISCORD_LOG_CHANNEL_ID):
    headers = {"Authorization": f"Bot {DISCORD_BOT_TOKEN}"}
    app = current_app._get_current_object()
    thr = Thread(target=post_async_message, args=[app, DISCORD_ENDPOINT, DISCORD_LOG_CHANNEL_ID, data, headers])
    thr.start()
    return thr
