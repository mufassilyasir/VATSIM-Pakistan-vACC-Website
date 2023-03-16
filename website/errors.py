from flask import Blueprint, render_template, request
from .models import Administrative, Users
from flask_login import current_user
from dotenv import load_dotenv
from .emailutil import post_discord_message, send_email

import os


errors = Blueprint("errors", __name__)
load_dotenv()
ZERO = os.getenv("ZERO")
ONE = os.getenv("ONE")


@errors.app_errorhandler(404)
def notfound(error):
    if current_user.is_authenticated:
        is_logged_in = "True"
        query = Users.query.filter_by(id=current_user.id).first()
        
        if query.Use_CID == "False" and query.Use_First_Name == "False":
            name = query.Full_Name
        elif query.Use_CID == "False" and query.Use_First_Name == "True":
            name = query.First_Name
        elif query.Use_CID == "True":
            name = current_user.id

        if current_user.has_role(ONE):
            check_admin = "True"
        elif current_user.has_role(ZERO):
            check_admin = "True"
        else:
            check_admin = "False"
    else:
        is_logged_in = "False"
        name="none"
        check_admin = "False"

    return render_template("/errors/404.html", name=name, is_logged_in=is_logged_in, policies=Administrative.query.all(),
    check_admin=check_admin), 404


@errors.app_errorhandler(403)
def forbidden(error):
    if current_user.is_authenticated:
        is_logged_in = "True"
        query = Users.query.filter_by(id=current_user.id).first()
        
        if query.Use_CID == "False" and query.Use_First_Name == "False":
            name = query.Full_Name
        elif query.Use_CID == "False" and query.Use_First_Name == "True":
            name = query.First_Name
        elif query.Use_CID == "True":
            name = current_user.id

        if current_user.has_role(ONE):
            check_admin = "True"
        elif current_user.has_role(ZERO):
            check_admin = "True"
        else:
            check_admin = "False"
    else:
        is_logged_in = "False"
        name="none"
        check_admin = "False"
    send_email('403 error Pakistan', 'no-reply@vatsimpakistan.com',
                ["mufassilyasir@gmail.com"], None,f"403 Error in Pakistan, {name} caused 403 error at {request.base_url}, IP {request.remote_addr}",None)
    return render_template("/errors/403.html", name=name, is_logged_in=is_logged_in, policies=Administrative.query.all(),
    check_admin=check_admin), 403
