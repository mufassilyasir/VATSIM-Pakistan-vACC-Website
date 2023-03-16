from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
from datetime import timedelta


import os 


mail = Mail()
db = SQLAlchemy()

def create_app():
    from website.errors import errors
    from website.models import models
    from website.auth import auth
    from website.views import views
    from website.discord import discord
    from website.api import api
    from website.admin import admin

    app = Flask(__name__)
    app.url_map.strict_slashes = False
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECURITY_SEND_REGISTER_EMAIL'] = False
    app.config['DEBUG'] = True
    app.config['TESTING'] = True
    app.config['TRAP_HTTP_EXCEPTIONS'] = True
    app.config['MAIL_SERVER'] = 'mail.vatsimpakistan.com'
    app.config['MAIL_PORT'] = 465
    app.config['MAIL_USE_TLS'] = False
    app.config['MAIL_USE_SSL'] = True
    app.config['MAIL_USERNAME'] = 'no-reply@vatsimpakistan.com'
    app.config['MAIL_PASSWORD'] = 'mypass'
    app.config['MAIL_DEFAULT_SENDER'] = 'no-reply@vatsimpakistan.com'
    app.config['MAIL_MAX_EMAILS'] = 1
    app.config['MAIL_ASCII_ATTACHMENTS'] = False
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = 'false'
    app.secret_key = b"mykey"
    app.permanent_session_lifetime = timedelta(days=1234)



    mail.init_app(app)
    db.init_app(app)

    app.register_blueprint(auth)
    app.register_blueprint(errors)
    app.register_blueprint(admin, name="myadmin")
    app.register_blueprint(models)
    app.register_blueprint(views)
    app.register_blueprint(discord)
    app.register_blueprint(api)
    return app

