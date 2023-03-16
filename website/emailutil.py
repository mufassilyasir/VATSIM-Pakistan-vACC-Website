from website import mail
from threading import Thread
from flask_mail import Message
from flask import current_app
import requests


def send_async_email(app, msg):
    with app.app_context():
        mail.send(msg)


def send_email(subject, sender, recipients, bcc, text_body, html_body):
    app = current_app._get_current_object()
    msg = Message(subject, sender=sender, bcc=bcc, recipients=recipients)
    msg.body = text_body
    msg.html = html_body
    thr = Thread(target=send_async_email, args=[app, msg])
    thr.start()
    return thr


def post_async_message(app, DISCORD_ENDPOINT, DISCORD_CHANNEL_ID, data, headers):
    with app.app_context():
        requests.post(f"{DISCORD_ENDPOINT}/v9/channels/{DISCORD_CHANNEL_ID}/messages", data=data, headers=headers)


def post_discord_message(data, DISCORD_BOT_TOKEN, DISCORD_ENDPOINT, DISCORD_CHANNEL_ID):
    headers = {"Authorization": f"Bot {DISCORD_BOT_TOKEN}"}
    app = current_app._get_current_object()
    thr = Thread(target=post_async_message, args=[app, DISCORD_ENDPOINT, DISCORD_CHANNEL_ID, data, headers])
    thr.start()
    return thr
