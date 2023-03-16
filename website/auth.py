from flask import Blueprint, redirect, url_for, request, session, flash
from flask_login.utils import logout_user
from .models import Users, db
from flask_login import login_manager, login_user, LoginManager, current_user
from urllib.parse import urlparse
from dotenv import load_dotenv
from .utils import avatar_download

import os
import requests
import urllib.parse as urlparse


auth = Blueprint("auth", __name__)
load_dotenv()



login_manager = LoginManager()
login_manager.login_view = "login"
login_manager.init_app(auth)


# @login_manager.user_loader
# def load_user(user_id):
#     return Users.query.get(int(user_id))



VATSIM_ENDPOINT = os.getenv("VATSIM_ENDPOINT")
VATSIM_CLIENT_ID = os.getenv("VATSIM_CLIENT_ID")
VATSIM_CLIENT_SECRET = os.getenv("VATSIM_CLIENT_SECRET")
VATSIM_REDIRECT_URI = os.getenv("VATSIM_REDIRECT_URI")


@auth.route('/auth/login')
def login():
    if current_user.is_authenticated == False:
        url = f"{VATSIM_ENDPOINT}/oauth/authorize"
        params = {
            "client_id": VATSIM_CLIENT_ID,
            "redirect_uri": VATSIM_REDIRECT_URI,
            "response_type": "code",
            "scope": "full_name vatsim_details email",
            "required_scopes": "vatsim_details email"
        }

        url_parse = urlparse.urlparse(url)
        query = url_parse.query
        url_dict = dict(urlparse.parse_qsl(query))
        url_dict.update(params)
        url_new_query = urlparse.urlencode(url_dict)
        url_parse = url_parse._replace(query=url_new_query)
        new_url = urlparse.urlunparse(url_parse)
        return redirect(new_url)
    else:
        return redirect(url_for("index"))


@auth.route('/auth/login/callback')
def authorize():
    code = request.args.get("code")

    data = {
        'grant_type': 'authorization_code',
        'client_id': VATSIM_CLIENT_ID,
        'client_secret': VATSIM_CLIENT_SECRET,
        'redirect_uri': VATSIM_REDIRECT_URI,
        'code':  code

    }
    r = requests.post(f"{VATSIM_ENDPOINT}/oauth/token", data=data)
    try:
        token = r.json()['access_token']
    except KeyError:
        flash("Error, missing token from VATSIM. Make sure you didn't access the link directly.")
        return redirect(url_for("index"))
    headers = {
        'Authorization': f"Bearer {token}",
        'Accept': 'application/json'
    }

    r1 = requests.get(f"{VATSIM_ENDPOINT}/api/user", headers=headers)
    result = r1.json()
    if 'error' in result:
        flash(result)
        return redirect(url_for("index"))
    
    try:
        name_first = result['data']['personal']['name_first']
    except:
        UseCID = "True"
        name_first = "None"
    else:
        UseCID = "False"
    finally:
        try:
            name_last = result['data']['personal']['name_last']
        except KeyError:
            name_last = "None"
        finally:
            try:
                name_full = result['data']['personal']['name_full']
            except KeyError:
                name_full = "None"
            finally:
                try:
                    rating_long = result['data']['vatsim']['rating']['long']
                except KeyError:
                    flash("Rating not found. Please try again.")
                    return redirect(url_for("index"))
                else:

                    try:
                        email = result['data']['personal']['email']
                    except KeyError:
                        flash("Email not found. Please try again.")
                        return redirect(url_for("index"))
                    else:

                        rating_short = result['data']['vatsim']['rating']['short']
                        pilot_short = result['data']['vatsim']['pilotrating']['short']
                        pilot_long = result['data']['vatsim']['pilotrating']['long']
                        division_id = result['data']['vatsim']['division']['id']
                        division_name = result['data']['vatsim']['division']['name']
                        region_id = result['data']['vatsim']['region']['id']
                        region_name = result['data']['vatsim']['region']['name']
                        subdivision_id = result['data']['vatsim']['subdivision']['id']
                        subdivision_name = result['data']['vatsim']['subdivision']['name']
                        cid = result['data']['cid']

                        found_CID = Users.query.filter_by(id=cid).first()
                        if found_CID:
                            found_CID.First_Name = name_first
                            found_CID.Last_Name = name_last
                            found_CID.Full_Name = name_full
                            found_CID.Email = email
                            found_CID.RatingLong = rating_long
                            found_CID.RatingShort = rating_short
                            found_CID.PilotShort = pilot_short
                            found_CID.PilotLong = pilot_long
                            found_CID.DivisionID = division_id
                            found_CID.DivisionName = division_name
                            found_CID.RegionID = region_id
                            found_CID.RegionName = region_name
                            found_CID.SubdivisionID = subdivision_id
                            found_CID.SubdivisionName = subdivision_name
                            if UseCID:
                                found_CID.Use_CID = UseCID
                            db.session.commit()
                            print("Mufassil, member CID was found and their records were updated in our database.")
                            login_user(found_CID, remember=True)
                            
                            if found_CID.PrivacyPolicyAccepted == "True":
                                if found_CID.Use_CID == "False" and found_CID.Use_First_Name == "False":
                                    name = found_CID.Full_Name
                                elif found_CID.Use_CID == "False" and found_CID.Use_First_Name == "True":
                                    name = found_CID.First_Name
                                elif found_CID.Use_CID == "True":
                                    name = current_user.id

                                flash(f"Welcome back {name}!", category='success')
                                return redirect(url_for("views.myprofile"))
                            else:
                                if UseCID == "True":
                                    avatar_download(first_name="None", last_name="None", cid=cid)
                                else:
                                    avatar_download(first_name=name_first, last_name=name_last, cid=cid)
                                return redirect(url_for("views.privacypolicy"))


                        else:
                            if UseCID == "True":
                                User_add = Users(id=cid, First_Name="None", Last_Name="None", Full_Name="None", Email=email, RatingLong=rating_long, RatingShort=rating_short, PilotShort=pilot_short, PilotLong=pilot_long,
                                                 DivisionID=division_id, DivisionName=division_name, RegionID=region_id, RegionName=region_name, SubdivisionID=subdivision_id, SubdivisionName=subdivision_name, Use_CID=UseCID)
                                avatar_download(first_name="None", last_name="None", cid=cid)
                            else:
                                User_add = Users(id=cid, First_Name=name_first, Last_Name=name_last, Full_Name=name_full, Email=email, RatingLong=rating_long, RatingShort=rating_short, PilotShort=pilot_short, PilotLong=pilot_long,
                                                 DivisionID=division_id, DivisionName=division_name, RegionID=region_id, RegionName=region_name, SubdivisionID=subdivision_id, SubdivisionName=subdivision_name, Use_CID="False")
                                avatar_download(first_name=name_first, last_name=name_last, cid=cid)

                            db.session.add(User_add)
                            db.session.commit()
                            user = Users.query.filter_by(id=cid).first()
                            print("Mufassil, member CID was NOT found, and their records were updated in our database.")
                            login_user(user, remember=True)
                            return redirect(url_for("views.privacypolicy"))

@auth.route('/auth/logout')
def logout():
    if current_user.is_authenticated:
        logout_user()
        return redirect(url_for("index"))
    else:
        return redirect(url_for("index"))