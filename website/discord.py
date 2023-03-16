from flask import Blueprint, redirect, url_for, request, session, flash, abort
from flask_login import current_user
from datetime import datetime
from dotenv import load_dotenv
from .models import Discord, Staff, Users, db, SystemLog
from .utils import post_discord_message
from .discordutils import discordlogin, getguilds, getuser, add_guild_member, discordserverjoinlogin, refreshtoken, discordspeciallogin, discordlogoutrequest

import os

discord = Blueprint("discord", __name__)
load_dotenv()

DISCORD_ENDPOINT = os.getenv("DISCORD_ENDPOINT")
DISCORD_ACCOUNT_LINK_URI = os.getenv("DISCORD_ACCOUNT_LINK_URI")
DISCORD_SERVER_JOIN_URI = os.getenv("DISCORD_SERVER_JOIN_URI")
DISCORD_GUILD_ID = os.getenv("DISCORD_GUILD_ID")
DISCORD_BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")
DISCORD_LOG_CHANNEL_ID = os.getenv("DISCORD_LOG_CHANNEL_ID")
DISCORD_SPECIAL_REDIRECT_URI = os.getenv("DISCORD_SPECIAL_REDIRECT_URI")
THREE = os.getenv("THREE")


@discord.route("/discord/link")
def oauth():
    if current_user.is_authenticated:
        query = Users.query.filter_by(id=current_user.id).first()
        if query.PrivacyPolicyAccepted == "True":
            if current_user.has_role(THREE):
                abort(403)
            else:
                return redirect(DISCORD_ACCOUNT_LINK_URI)
        else:
            return redirect(url_for("views.privacypolicy"))
    else:
        return redirect(url_for("auth.login"))


@discord.route("/discord/link/callback")
def oauthcallback():
    if current_user.is_authenticated:
        user_query = Users.query.filter_by(id=current_user.id).first()
        if user_query.PrivacyPolicyAccepted == "True":
            if current_user.has_role(THREE) == False:
                code = request.args.get("code")
                error = request.args.get("error")
                if error == None:
                    if code != None:
                        result = discordlogin(code)

                        session.permanent = True
                        try:
                            session['refresh_token'] = result['refresh_token']
                        except:
                            return redirect(url_for("discord.speciallinkdiscord"))
                        else:

                            user = getuser(result['access_token'])
                            if Discord.query.filter(Discord.discord_user_id == user['id']).first():
                                flash("Oops, it appears this Discord account is linked with an another account.", category='error')
                                return redirect(url_for("views.myprofile"))

                            else:
                                guilds = getguilds(result['access_token'])

                                guilds_list = []
                                for g in guilds:
                                    guilds_list.append(g['id'])

                                if DISCORD_GUILD_ID not in guilds_list:
                                    discord_query = Discord.query.filter_by(id=current_user.id).first()
                                    if discord_query:

                                        discord_query.is_server_joined = "False"
                                        discord_query.is_discord_linked = "True"
                                        user_query.Discord_Linked = "True"
                                        user_query.DiscordServerJoin = "False"
                                        time_now = datetime.utcnow()
                                        system_log = SystemLog(
                                            action_by=current_user.id, action=f"Linked Discord account.", timestamp=f"{time_now.strftime('%d-%m-%Y %H:%M:%S')} UTC")
                                        db.session.add(system_log)
                                        db.session.commit()
                                        session['token'] = result['access_token']
                                        session.permanent = True
                                    else:
                                        
                                        try:
                                            if user['avatar'].startswith("a_"):
                                                profile_link = f"https://cdn.discordapp.com/avatars/{user['id']}/{user['avatar']}.gif"
                                            else:
                                                profile_link = f"https://cdn.discordapp.com/avatars/{user['id']}/{user['avatar']}.png"
                                        except:
                                            profile_link = f"/static/public/initials/{current_user.id}.png"

                                        discord_data_add = Discord(id=current_user.id, is_discord_linked="True",
                                                                  is_server_joined="False", discord_user_id=user['id'], 
                                                                  discord_username=f"{user['username']}#{user['discriminator']}", discord_profile_link=profile_link)
                                        db.session.add(discord_data_add)
                                        user_query.Discord_Linked = "True"
                                        user_query.DiscordServerJoin = "False"
                                        time_now = datetime.utcnow()
                                        system_log = SystemLog(
                                            action_by=current_user.id, action=f"Linked Discord account.", timestamp=f"{time_now.strftime('%d-%m-%Y %H:%M:%S')} UTC")
                                        db.session.add(system_log)
                                        db.session.commit()
                                        session['token'] = result['access_token']
                                        session.permanent = True

                                    flash("Discord account linked successfully.", category='success')
                                    return redirect(url_for("views.myprofile"))

                                elif DISCORD_GUILD_ID in guilds_list:
                                    discord_query = Discord.query.filter_by(id=current_user.id).first()
                                    if discord_query:

                                        discord_query.is_server_joined = "True"
                                        discord_query.is_discord_linked = "True"
                                        user_query.Discord_Linked = "True"
                                        user_query.DiscordServerJoin = "True"
                                        time_now = datetime.utcnow()
                                        system_log = SystemLog(
                                            action_by=current_user.id, action=f"Linked Discord account.", timestamp=f"{time_now.strftime('%d-%m-%Y %H:%M:%S')} UTC")
                                        db.session.add(system_log)
                                        db.session.commit()
                                        session['token'] = result['access_token']
                                        session.permanent = True

                                    else:
                                        try:
                                            if user['avatar'].startswith("a_"):
                                                profile_link = f"https://cdn.discordapp.com/avatars/{user['id']}/{user['avatar']}.gif"
                                            else:
                                                profile_link = f"https://cdn.discordapp.com/avatars/{user['id']}/{user['avatar']}.png"
                                        except:
                                            profile_link = f"/static/public/initials/{current_user.id}.png"

                                        discord_data_add = Discord(id=current_user.id, is_discord_linked="True",
                                                                  is_server_joined="True", discord_user_id=user['id'], 
                                                                  discord_username=f"{user['username']}#{user['discriminator']}", discord_profile_link=profile_link)
                                        db.session.add(discord_data_add)
                                        user_query.Discord_Linked = "True"
                                        user_query.DiscordServerJoin = "True"
                                        time_now = datetime.utcnow()
                                        system_log = SystemLog(
                                            action_by=current_user.id, action=f"Linked Discord account.", timestamp=f"{time_now.strftime('%d-%m-%Y %H:%M:%S')} UTC")
                                        db.session.add(system_log)
                                        db.session.commit()
                                        session.permanent = True
                                        session['token'] = result['access_token']
                                        print(session['token'])

                                    flash("Discord account linked successfully.", category='success')
                                    return redirect(url_for("views.myprofile"))
                    else:
                        return redirect(url_for("discord.oauth"))
                else:
                    flash(error, category='error')
                    return redirect(url_for("views.myprofile"))
            else:
                abort(403)

        else:
            return redirect(url_for("views.privacypolicy"))
    else:
        return redirect(url_for("auth.login"))

@discord.route("/discord/join")
def serverjoin():
    if current_user.is_authenticated:
        query = Users.query.filter_by(id=current_user.id).first()
        if query.PrivacyPolicyAccepted == "True":
            if current_user.has_role(THREE):
                abort(403)
            else:
                return redirect(DISCORD_SERVER_JOIN_URI)
        else:
            return redirect(url_for("views.privacypolicy"))
    else:
        return redirect(url_for("auth.login"))


@discord.route("/discord/join/callback")
def serverjoincallback():
    if current_user.is_authenticated:
        name_query = Users.query.filter_by(id=current_user.id).first()
        if name_query.PrivacyPolicyAccepted == "True":
            if current_user.has_role(THREE) == False:
                code = request.args.get("code")

                result = discordserverjoinlogin(code)

                try:
                    session['access_token_guilds'] = result['access_token']
                except:
                    flash("Discord error, kindly try to join server again.", category='error')
                    return redirect(url_for("views.myprofile"))
                session.permanent = True

                if "access_token_guilds" in session:
                    user = getuser(result['access_token'])
                    guilds = getguilds(result['access_token'])

                    guilds_list = []
                    for g in guilds:
                        guilds_list.append(g['id'])

                    if DISCORD_GUILD_ID not in guilds_list:
                        query = Discord.query.filter_by(id=current_user.id).first()
                        if query:
                            if name_query.Use_CID == "False" and name_query.Use_First_Name == "False":
                                name = name_query.Full_Name
                                check = 1

                            elif name_query.Use_CID == "False" and name_query.Use_First_Name == "True":
                                name = name_query.First_Name
                                check = 2

                            elif name_query.Use_CID == "True":
                                name = None
                                check = 3

                            add_guild_member(DISCORD_GUILD_ID, user['id'], session['access_token_guilds'], name, current_user.id, check)
                            query.is_server_joined = "True"
                            name_query.DiscordServerJoin = "True"
                            time_now = datetime.utcnow()
                            system_log = SystemLog(action_by=current_user.id, action=f"Joined vACC's Discord server.",
                                                   timestamp=f"{time_now.strftime('%d-%m-%Y %H:%M:%S')} UTC")
                            db.session.add(system_log)
                            db.session.commit()

                            flash("Joined vACC's Discord server successfully, enjoy your time!", category='success')
                            return redirect(url_for("views.myprofile"))

                        else:
                            return redirect(url_for("discord.oauth"))

                    elif DISCORD_GUILD_ID in guilds_list:
                        flash("You are already a member of vACC's Discord server.")
                        return redirect(url_for("views.myprofile"))

                else:
                    return redirect(url_for("discord.serverjoin"))

            else:
                abort(403)
        else:
            return redirect(url_for("views.privacypolicy"))
    else:
        return redirect(url_for("auth.login"))


@discord.route("/discord/use-profile-picture")
def discordprofilepicset():
    if current_user.is_authenticated:
        query = Users.query.filter_by(id=current_user.id).first()
        if query.PrivacyPolicyAccepted == "True":
            if current_user.has_role(THREE) == False:
                if "token" in session:
                    if "refresh_token" in session:

                        try:
                            some_variable = refreshtoken(session['refresh_token'])
                        except:
                            session['pakistan-vacc-referrer'] = request.base_url
                            return redirect(url_for("discord.speciallinkdiscord"))

                        access_token = some_variable['access_token']
                        session.permanent = True
                        session['token'] = access_token
                        session['refresh_token'] = some_variable['refresh_token']

                        store = getuser(access_token)

                        try:
                            if store['avatar'].startswith("a_"):
                                profile_link = f"https://cdn.discordapp.com/avatars/{store['id']}/{store['avatar']}.gif"
                            else:
                                profile_link = f"https://cdn.discordapp.com/avatars/{store['id']}/{store['avatar']}.png"
                        except:
                            profile_link = f"/static/public/initials/{current_user.id}.png"
                        
                        if profile_link == "None":
                            flash("You do not have a discord profile picture set.", category='error')
                            return redirect(url_for("views.myprofile"))
                        query1 = Discord.query.filter_by(id=current_user.id).first()
                        query1.discord_profile_link = profile_link
                        query1.discord_profile_use = "True"
                        query.user_own_upload = "False"
                        if Staff.query.filter_by(id=current_user.id).first():
                            Staff.query.filter_by(id=current_user.id).first().staff_image_url = profile_link
                        time_now = datetime.utcnow()
                        system_log = SystemLog(action_by=current_user.id, action=f"Changed their profile picture to Discord profile picture.",
                                               timestamp=f"{time_now.strftime('%d-%m-%Y %H:%M:%S')} UTC")
                        db.session.add(system_log)
                        db.session.commit()
                        flash("Discord avatar used as profile image.", category='success')
                        return redirect(url_for("views.myprofile"))

                    else:
                        session['pakistan-vacc-referrer'] = request.base_url
                        return redirect(url_for("discord.speciallinkdiscord"))

                else:
                    session['pakistan-vacc-referrer'] = request.base_url
                    return redirect(url_for("discord.speciallinkdiscord"))

            else:
                abort(403)

        else:
            return redirect(url_for("views.privacypolicy"))

    else:
        return redirect(url_for("auth.login"))


@discord.route("/discord/remove-profile-picture")
def discordprofilepicrem():
    if current_user.is_authenticated:
        query = Users.query.filter_by(id=current_user.id).first()
        if query.PrivacyPolicyAccepted == "True":
            if current_user.has_role(THREE) == False:

                query = Discord.query.filter_by(id=current_user.id).first()
                query.discord_profile_use = "False"
                if Staff.query.filter_by(id=current_user.id).first():
                    Staff.query.filter_by(id=current_user.id).first().staff_image_url = f"/static/public/initials/{current_user.id}.png"
                time_now = datetime.utcnow()
                system_log = SystemLog(action_by=current_user.id, action=f"Removed Discord profile picture as avatar.",
                                        timestamp=f"{time_now.strftime('%d-%m-%Y %H:%M:%S')} UTC")
                db.session.add(system_log)
                db.session.commit()
                flash("Discord Avatar removed as profile image.", category='success')
                return redirect(url_for("views.myprofile"))

            else:
                abort(403)

        else:
            return redirect(url_for("views.privacypolicy"))

    else:
        return redirect(url_for("auth.login"))

@discord.route("/discord/another/link")
def speciallinkdiscord():
    if current_user.is_authenticated:
        query = Users.query.filter_by(id=current_user.id).first()
        if query.PrivacyPolicyAccepted == "True":
            if current_user.has_role(THREE):
                abort(403)
            else:
                return redirect(DISCORD_SPECIAL_REDIRECT_URI)

        else:
            return redirect(url_for("views.privacypolicy"))

    else:
        return redirect(url_for("auth.login"))


@discord.route("/discord/another/link/callback")
def speciallinkdiscordcallback():
    if current_user.is_authenticated:
        query = Users.query.filter_by(id=current_user.id).first()
        if query.PrivacyPolicyAccepted == "True":
            if current_user.has_role(THREE) == False:
                code = request.args.get("code")

                result = discordspeciallogin(code)

                session['refresh_token'] = result['refresh_token']
                session['token'] = result['access_token']
                if session['pakistan-vacc-referrer']:
                    return redirect(session['pakistan-vacc-referrer'])
                else:
                    return redirect(url_for("views.myprofile"))

            else:
                abort(403)
        else:
            return redirect(url_for("views.privacypolicy"))

    else:
        return redirect(url_for("auth.login"))

@discord.route("/profile-picture/reset", methods=["POST"], strict_slashes=False)
def avatarreset():
    if current_user.is_authenticated:
        if current_user.has_role(THREE) == False:
            if request.method == "POST":
                value = request.form["resetavatar"]
                if value == "resetpls":
                    query = Users.query.filter_by(id=current_user.id).first()
                    query1 = Discord.query.filter_by(id=current_user.id).first()
                    if query1:
                        query1.discord_profile_use = "False"
                    query.user_own_upload = "False"
                    db.session.commit()
                    flash("Profile picture set to default.", category='success')
                    return redirect(url_for("views.myprofile"))
        else:
            abort(403)
    else:
        return redirect(url_for("auth.login"))
    
@discord.route("/discord/unlink/account")
def discordlogout():
    if current_user.is_authenticated:
        query = Users.query.filter_by(id=current_user.id).first()
        if query.PrivacyPolicyAccepted == "True":
            if current_user.has_role(THREE) == False:
                query = Discord.query.filter_by(id=current_user.id).first()
                if query:
                    if query.is_server_joined == "True":

                        discordlogoutrequest()

                        data = {
                            "content": f"<@{query.discord_user_id}> Unlinked Discord account and was removed from vACC's Discord server."}
                        post_discord_message(data, DISCORD_BOT_TOKEN, DISCORD_ENDPOINT, DISCORD_LOG_CHANNEL_ID)

                if query.is_server_joined == "True":
                    try:
                        session.pop("access_token_guilds")
                    except KeyError:
                        print("User did not join from our service")
                try:
                    session.pop("refresh_token")
                except KeyError:
                    pass
                try:
                    session.pop("token")
                except KeyError:
                    pass

                Discord.query.filter_by(id=current_user.id).delete()
                time_now = datetime.utcnow()
                system_log = SystemLog(action_by=current_user.id, action=f"Unlinked Discord account.",
                                       timestamp=f"{time_now.strftime('%d-%m-%Y %H:%M:%S')} UTC")
                db.session.add(system_log)
                db.session.commit()

                flash("Successfully unlinked Discord account.", category='success')
                return redirect(url_for("views.myprofile"))

            else:
                abort(403)
        else:
            return redirect(url_for("views.privacypolicy"))

    else:
        return redirect(url_for("auth.login"))