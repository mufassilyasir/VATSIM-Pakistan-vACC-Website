from flask_login import current_user
from .models import Discord, db
from dotenv import load_dotenv
import requests
import os


load_dotenv()

DISCORD_ENDPOINT = os.getenv("DISCORD_ENDPOINT")
DISCORD_ACCOUNT_LINK_URI = os.getenv("DISCORD_ACCOUNT_LINK_URI")
DISCORD_SERVER_JOIN_URI = os.getenv("DISCORD_SERVER_JOIN_URI")
DISCORD_GUILD_ID = os.getenv("DISCORD_GUILD_ID")
DISCORD_BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")
DISCORD_LOG_CHANNEL_ID = os.getenv("DISCORD_LOG_CHANNEL_ID")
DISCORD_SPECIAL_REDIRECT_URI = os.getenv("DISCORD_SPECIAL_REDIRECT_URI")
DISCORD_CLIENT_ID = os.getenv("DISCORD_CLIENT_ID")
DISCORD_CLIENT_SECRET = os.getenv("DISCORD_CLIENT_SECRET")
DISCORD_REDIRECT_URI = os.getenv("DISCORD_REDIRECT_URI")
DISCORD_REDIRECT_SERVER_JOIN_URI = os.getenv('DISCORD_REDIRECT_SERVER_JOIN_URI')
DISCORD_REDIRECT_SPECIAL_URI = os.getenv("DISCORD_REDIRECT_SPECIAL_URI")


THREE = os.getenv("THREE")

def discordlogin(code: str):
    data = {
        'client_id': DISCORD_CLIENT_ID,
        'client_secret': DISCORD_CLIENT_SECRET,
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': DISCORD_REDIRECT_URI,
        'scope': 'identify guilds'
    }
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    r = requests.post(f'{DISCORD_ENDPOINT}/oauth2/token', data=data, headers=headers)
    result = r.json()
    return result

def discordspeciallogin(code: str):
    data = {
        'client_id': DISCORD_CLIENT_ID,
        'client_secret': DISCORD_CLIENT_SECRET,
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': DISCORD_REDIRECT_SPECIAL_URI,
        'scope': 'identify'
    }
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    r = requests.post(f"{DISCORD_ENDPOINT}/oauth2/token", data=data, headers=headers)
    result = r.json()
    return result


def getuser(access_token: str):
    headers = {
        'Authorization': f"Bearer {access_token}"
    }
    r1 = requests.get(f"{DISCORD_ENDPOINT}/v9/users/@me", headers=headers)
    return r1.json()

def getguilds(access_token: str):
    headers = {
        'Authorization': f"Bearer {access_token}"
    }
    r1 = requests.get(f"{DISCORD_ENDPOINT}/v9/users/@me/guilds", headers=headers)
    return r1.json()

def add_guild_member(guild_id, user_id, access_token, name, id, check):

    data = {"access_token": access_token}
    headers = {"Authorization": f"Bot {DISCORD_BOT_TOKEN}"}

    requests.put(f"{DISCORD_ENDPOINT}/v9/guilds/{guild_id}/members/{user_id}", headers=headers, json=data)

    if check == 3:
        payload = {"Content-Type": 'application/json', "nick": f"|-{id}-|"}
        requests.patch(f"{DISCORD_ENDPOINT}/v9/guilds/{guild_id}/members/{user_id}", headers=headers, json=payload)

    else:
        payload = {"Content-Type": 'application/json', "nick": f"{name} - {id}"}
        requests.patch(f"{DISCORD_ENDPOINT}/v9/guilds/{guild_id}/members/{user_id}", headers=headers, json=payload)

    return

def updatename(user_id, name, cid, group):
    headers = {"Authorization": f"Bot {DISCORD_BOT_TOKEN}"}
    if group == "1":
        payload = {"Content-Type": 'application/json', "nick": f"|-{cid}-|"}
        requests.patch(f"{DISCORD_ENDPOINT}/v9/guilds/{DISCORD_GUILD_ID}/members/{user_id}",
                       headers=headers, json=payload)

    elif group == "2":
        payload = {"Content-Type": 'application/json', "nick": f"{name} - {cid}"}
        requests.patch(f"{DISCORD_ENDPOINT}/v9/guilds/{DISCORD_GUILD_ID}/members/{user_id}",
                       headers=headers, json=payload)

    elif group == "3":
        payload = {"Content-Type": 'application/json', "nick": f"{name} - {cid}"}
        requests.patch(f"{DISCORD_ENDPOINT}/v9/guilds/{DISCORD_GUILD_ID}/members/{user_id}",
                       headers=headers, json=payload)

    return

def discordserverjoinlogin(code: str):
    data = {
        'client_id': DISCORD_CLIENT_ID,
        'client_secret': DISCORD_CLIENT_SECRET,
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': DISCORD_REDIRECT_SERVER_JOIN_URI,
        'scope': 'identify guilds guilds.join'
    }
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    r = requests.post(f"{DISCORD_ENDPOINT}/oauth2/token", data=data, headers=headers)
    return r.json()


def refreshtoken(refresh_token: str):
    data = {
        'client_id': DISCORD_CLIENT_ID,
        'client_secret': DISCORD_CLIENT_SECRET,
        'grant_type': 'refresh_token',
        'refresh_token': refresh_token
    }
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    r = requests.post(f"{DISCORD_ENDPOINT}/v9/oauth2/token", headers=headers, data=data)
    return r.json()

def discordlogoutrequest():
    query = Discord.query.filter_by(id=current_user.id).first()

    headers = {"Authorization": f"Bot {DISCORD_BOT_TOKEN}"}
    requests.delete(f"{DISCORD_ENDPOINT}/v9/guilds/{DISCORD_GUILD_ID}/members/{query.discord_user_id}", headers=headers)