# Custom Script to check members in Discord and update their ratings against VATSIM Database and more.
from website.models import Role, roles_users, Users, db, Discord
from datetime import datetime
from dotenv import load_dotenv
from app import create_app

import requests
import time
import os


load_dotenv()
app = create_app()
app.app_context().push()


DISCORD_BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")
GUILD_ID = os.getenv("DISCORD_GUILD_ID")
CHANNEL_ID = os.getenv("DISCORD_LOG_CHANNEL_ID")

data = {"content": "Starting up role check."}
headers = {"Authorization": f"Bot {DISCORD_BOT_TOKEN}"}
requests.post(f"https://discord.com/api/v9/channels/{CHANNEL_ID}/messages", data=data, headers=headers)

time_start = datetime.utcnow()

payload = {"limit": 1000}
headers = {"Authorization": f"Bot {DISCORD_BOT_TOKEN}"}
r1 = requests.get(f"https://discord.com/api/v9/guilds/{GUILD_ID}/members", headers=headers, params=payload)
results = r1.json()
numbers = []
roles = []
allmems = []
ERROR = None


r2 = requests.get("https://hq.vatwa.net/api/vacc/PAK/resident")
r3 = requests.get("https://hq.vatwa.net/api/vacc/PAK/visitor")

if r2.status_code == 200 and r3.status_code == 200:
    for allmems1 in r2.json():
        allmems.append(allmems1['cid'])

    for allmems2 in r3.json():
        allmems.append(allmems2['cid'])

    residentslist = r2.json()
    visitorslist = r3.json()

else:
    print(f"Error in fetching residents {r2.status_code}")
    print(f"Error in fetching visitors {r3.status_code}")
    ERROR = f'{r2.status_code} Status returned by VATWA HQ'

for result in results:

    if result['nick'] != None:
        if result['nick'].startswith('|-') and result['nick'].endswith('-|'):
            new = result['nick'][2:-2]
            for word in new.split():
                if word.isdigit():
                    numbers.append(int(word))
                    data = {
                        "id": word,
                        "roles": result['roles'],
                        "discord_id": result['user']['id']
                    }
                    roles.append(data)

        else:
            for word in result['nick'].split():
                if word.isdigit():
                    numbers.append(int(word))
                    data = {
                        "id": word,
                        "roles": result['roles'],
                        "discord_id": result['user']['id']
                    }
                    roles.append(data)


OBS = '812598838732128266'
S1 = '812598837980954635'
S2 = '812598837754593280'
S3 = '812598837310390282'
C1 = '812598836580843541'
C3 = '812598836173471745'
I1 = '812598835804110888'
I3 = '812598835167494165'
SUP = '812598834994872340'
ADM = '812598834601525258'


GUEST = "812658278273253377"
RESIDENT = "810135707586134031"
APPROVED_RESIDENT = "810135707586134030"
VISITING_CONTROLLER = "894564558956535819"

rating_change = 0
suspensions = 0
revoke_suspensions = 0


for cid in numbers:
    r4 = requests.get(f"https://api.vatsim.net/api/ratings/{cid}/")
    try:
        save = r4.json()
    except Exception:
        time.sleep(1)
        r4 = requests.get(f"https://api.vatsim.net/api/ratings/{cid}/")
        try:
            save = r4.json()
        except Exception:
            print(r4.content)
            print(r4.status_code)
            print(f"Error at CID {cid}")
            ERROR = "LINE 116, VATSIM ERROR"
    finally:
        try:
            rating = save['rating']
        except:
            print(f"Error, CID {cid} rating was not found. Invalid response from VATSIM")
        else:
            for ids in roles:
                if str(cid) == ids['id']:
                    if rating == 1:
                        if OBS not in ids['roles']:
                            requests.put(
                                f"https://discord.com/api/guilds/{GUILD_ID}/members/{ids['discord_id']}/roles/{OBS}", headers=headers)
                            rating_change = rating_change + 1

                    elif rating == 2:
                        if S1 not in ids['roles']:
                            requests.put(
                                f"https://discord.com/api/guilds/{GUILD_ID}/members/{ids['discord_id']}/roles/{S1}", headers=headers)

                            if OBS in ids['roles']:
                                requests.delete(
                                    f"https://discord.com/api/guilds/{GUILD_ID}/members/{ids['discord_id']}/roles/{OBS}", headers=headers)
                            rating_change = rating_change + 1

                    elif rating == 3:
                        if S2 not in ids['roles']:
                            requests.put(
                                f"https://discord.com/api/guilds/{GUILD_ID}/members/{ids['discord_id']}/roles/{S2}", headers=headers)

                            if S1 in ids['roles']:
                                requests.delete(
                                    f"https://discord.com/api/guilds/{GUILD_ID}/members/{ids['discord_id']}/roles/{S1}", headers=headers)
                            rating_change = rating_change + 1

                    elif rating == 4:
                        if S3 not in ids['roles']:
                            requests.put(
                                f"https://discord.com/api/guilds/{GUILD_ID}/members/{ids['discord_id']}/roles/{S3}", headers=headers)

                            if S2 in ids['roles']:
                                requests.delete(
                                    f"https://discord.com/api/guilds/{GUILD_ID}/members/{ids['discord_id']}/roles/{S2}", headers=headers)
                            rating_change = rating_change + 1

                    elif rating == 5:
                        if C1 not in ids['roles']:
                            requests.put(
                                f"https://discord.com/api/guilds/{GUILD_ID}/members/{ids['discord_id']}/roles/{C1}", headers=headers)

                            if S3 in ids['roles']:
                                requests.delete(
                                    f"https://discord.com/api/guilds/{GUILD_ID}/members/{ids['discord_id']}/roles/{S3}", headers=headers)
                            rating_change = rating_change + 1

                    elif rating == 7:
                        if C3 not in ids['roles']:
                            requests.put(
                                f"https://discord.com/api/guilds/{GUILD_ID}/members/{ids['discord_id']}/roles/{C3}", headers=headers)

                            if C1 in ids['roles']:
                                requests.delete(
                                    f"https://discord.com/api/guilds/{GUILD_ID}/members/{ids['discord_id']}/roles/{C1}", headers=headers)
                            rating_change = rating_change + 1

                    elif rating == 8:
                        if I1 not in ids['roles']:
                            requests.put(
                                f"https://discord.com/api/guilds/{GUILD_ID}/members/{ids['discord_id']}/roles/{I1}", headers=headers)
                            if C1 in ids['roles']:
                                requests.delete(
                                    f"https://discord.com/api/guilds/{GUILD_ID}/members/{ids['discord_id']}/roles/{C1}", headers=headers)
                            elif C3 in ids['roles']:
                                requests.delete(
                                    f"https://discord.com/api/guilds/{GUILD_ID}/members/{ids['discord_id']}/roles/{C3}", headers=headers)

                            rating_change = rating_change + 1

                    elif rating == 10:
                        if I3 not in ids['roles']:
                            requests.put(
                                f"https://discord.com/api/guilds/{GUILD_ID}/members/{ids['discord_id']}/roles/{I3}", headers=headers)

                            if C1 in ids['roles']:
                                requests.delete(
                                    f"https://discord.com/api/guilds/{GUILD_ID}/members/{ids['discord_id']}/roles/{C1}", headers=headers)

                            elif C3 in ids['roles']:
                                requests.delete(
                                    f"https://discord.com/api/guilds/{GUILD_ID}/members/{ids['discord_id']}/roles/{C3}", headers=headers)

                            elif I1 in ids['roles']:
                                requests.delete(
                                    f"https://discord.com/api/guilds/{GUILD_ID}/members/{ids['discord_id']}/roles/{I1}", headers=headers)

                            rating_change = rating_change + 1

                    elif rating == 11:
                        if SUP not in ids['roles']:
                            requests.put(
                                f"https://discord.com/api/guilds/{GUILD_ID}/members/{ids['discord_id']}/roles/{SUP}", headers=headers)

                            rating_change = rating_change + 1

                    elif rating == 12:
                        if ADM not in ids['roles']:
                            requests.put(
                                f"https://discord.com/api/guilds/{GUILD_ID}/members/{ids['discord_id']}/roles/{ADM}", headers=headers)

                            rating_change = rating_change + 1

                    if rating == 0 or rating == -1:
                        requests.delete(
                            f"https://discord.com/api/guilds/{GUILD_ID}/members/{ids['discord_id']}", headers=headers)
                        suspensions = suspensions + 1
                        Role0 = Role.query.filter_by(id=3).first()
                        User = Users.query.filter_by(id=cid).first()
                        query = Discord.query.filter_by(id=cid).first()
                        if User:
                            try:
                                Role0.users.append(User)
                                if query:
                                    query.discord_server_data = "False"
                                db.session.commit()
                            except:
                                pass
                        else:
                            print(f"Found {cid} Suspended and unable to restrict them in database")

                    for resident in residentslist:
                        if int(resident['cid']) == cid:
                            if RESIDENT not in ids['roles']:
                                requests.put(
                                    f"https://discord.com/api/guilds/{GUILD_ID}/members/{ids['discord_id']}/roles/{RESIDENT}", headers=headers)

                            if GUEST in ids['roles']:
                                requests.delete(
                                    f"https://discord.com/api/guilds/{GUILD_ID}/members/{ids['discord_id']}/roles/{GUEST}", headers=headers)

                            if VISITING_CONTROLLER in ids['roles']:
                                requests.delete(
                                f"https://discord.com/api/guilds/{GUILD_ID}/members/{ids['discord_id']}/roles/{VISITING_CONTROLLER}", headers=headers)
                            
                            
                            if resident['approved_for'] != None:
                                if APPROVED_RESIDENT not in ids['roles']:
                                    requests.put(
                                        f"https://discord.com/api/guilds/{GUILD_ID}/members/{ids['discord_id']}/roles/{APPROVED_RESIDENT}", headers=headers)

                            elif resident['approved_for'] == None:
                                if APPROVED_RESIDENT in ids['roles']:
                                    requests.delete(
                                        f"https://discord.com/api/guilds/{GUILD_ID}/members/{ids['discord_id']}/roles/{APPROVED_RESIDENT}", headers=headers)

                    for visitor in visitorslist:
                        if int(visitor['cid']) == cid:
                            if RESIDENT in ids['roles']:
                                requests.delete(
                                    f"https://discord.com/api/guilds/{GUILD_ID}/members/{ids['discord_id']}/roles/{RESIDENT}", headers=headers)

                            if visitor['approved_for'] != None:
                                if VISITING_CONTROLLER not in ids['roles']:
                                    requests.put(
                                        f"https://discord.com/api/guilds/{GUILD_ID}/members/{ids['discord_id']}/roles/{VISITING_CONTROLLER}", headers=headers)
                                
                                if GUEST in ids['roles']:
                                    requests.delete(
                                        f"https://discord.com/api/guilds/{GUILD_ID}/members/{ids['discord_id']}/roles/{GUEST}", headers=headers)
                            
                            elif visitor['approved_for'] == None:
                                if VISITING_CONTROLLER in ids['roles']:
                                    requests.delete(
                                        f"https://discord.com/api/guilds/{GUILD_ID}/members/{ids['discord_id']}/roles/{VISITING_CONTROLLER}", headers=headers)
                                if GUEST not in ids['roles']:
                                    requests.put( 
                                        f"https://discord.com/api/guilds/{GUILD_ID}/members/{ids['discord_id']}/roles/{GUEST}", headers=headers)
                    
                    if str(cid) not in allmems:
                        if GUEST not in ids['roles']:
                            requests.put(
                                f"https://discord.com/api/guilds/{GUILD_ID}/members/{ids['discord_id']}/roles/{GUEST}", headers=headers)

                        if RESIDENT in ids['roles']:
                            requests.delete(
                                f"https://discord.com/api/guilds/{GUILD_ID}/members/{ids['discord_id']}/roles/{RESIDENT}", headers=headers)

                        if APPROVED_RESIDENT in ids['roles']:
                            requests.delete(
                                f"https://discord.com/api/guilds/{GUILD_ID}/members/{ids['discord_id']}/roles/{APPROVED_RESIDENT}", headers=headers)
                        
                        if VISITING_CONTROLLER in ids['roles']:
                            requests.delete(
                                f"https://discord.com/api/guilds/{GUILD_ID}/members/{ids['discord_id']}/roles/{VISITING_CONTROLLER}", headers=headers)



result = db.session.query(roles_users).filter(roles_users.c.user_id ==
                                              Users.id).filter(roles_users.c.role_id == Role.id).all()
for user in result:
    if user[1] == 3:
        r2 = requests.get(f"https://api.vatsim.net/api/ratings/{user[0]}/")
        data = r2.json()
        rating = data['rating']
        if rating != 0 or rating != -1:
            Role0 = Role.query.filter_by(id=3).first()
            User = Users.query.filter_by(id=user[0]).first()
            Role0.users.remove(User)
            db.session.commit()
            revoke_suspensions = revoke_suspensions + 1
            time.sleep(1)


time_end = datetime.utcnow()

diff = time_end - time_start
actual_diff = (diff.total_seconds())


data = {
    "content": f"Successfully updated member ratings. **{rating_change}** new rating updates. **{suspensions}** new suspensions were found and hence **{suspensions}** member(s) were kicked. **{revoke_suspensions}** suspensions revoked. Completed in **{actual_diff}** seconds. Error **{ERROR}**"}
headers = {"Authorization": f"Bot {DISCORD_BOT_TOKEN}"}
requests.post(f"https://discord.com/api/v9/channels/{CHANNEL_ID}/messages", data=data, headers=headers)
