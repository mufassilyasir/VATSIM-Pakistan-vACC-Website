from flask import render_template, abort, request, redirect
from website import create_app
from flask_login import current_user
from dotenv import load_dotenv
from flask_admin.contrib.sqla import ModelView
from flask_admin import Admin, AdminIndexView
from urllib.parse import urlparse, urlunparse
#from waitress import serve

import os

from website.models import Administrative, Events, Onlineatc, Stats, db, Role, Users, SystemLog, News, Uploads
from flask_security import Security, SQLAlchemyUserDatastore
app = create_app()


user_datastore = SQLAlchemyUserDatastore(db, Users, Role)
security = Security(app, user_datastore)


load_dotenv()
ZERO = os.getenv("ZERO")
ONE = os.getenv("ONE")
ID1 = os.getenv("ID1")
ID2 = os.getenv("ID2")

class MyAdminIndexView(AdminIndexView):
    def is_accessible(self):
        if current_user.is_authenticated:
            if current_user.has_role(ZERO) or current_user.has_role(ONE):
                return current_user.is_authenticated

    def inaccessible_callback(self, name, **kwargs):
        return abort(403)


class SystemLogController(ModelView):
    can_view_details = True
    column_filters = [
        'action_by',
        "action",
        "timestamp"
    ]
    column_default_sort = ('value', True)

    def is_accessible(self):
        if current_user.is_authenticated:
            if current_user.id == int(ID1):
                self.can_create = True
                self.can_edit = True
                self.can_delete = True
                return current_user.is_authenticated

            elif current_user.id == int(ID2):
                self.can_create = False
                self.can_edit = False
                self.can_delete = False
                return current_user.is_authenticated

    def inaccessible_callback(self, name, **kwargs):
        return abort(403)

class UserController(ModelView):
    can_view_details = True
    column_list = ['id', 'First_Name', 'Last_Name', 'Full_Name', 'Email', "RatingLong", "RatingShort", "PilotShort", "PilotLong", "DivisionID", "DivisionName",
                   "RegionID", "RegionName", "SubdivisionID", "SubdivisionName", "Discord_Linked", "DiscordServerJoin",  "PrivacyPolicyAccepted", "OptedinEmails"]

    def is_accessible(self):
        if current_user.is_authenticated:
            if current_user.id == int(ID1):
                self.can_create = True
                self.can_edit = True
                self.can_delete = True
                return current_user.is_authenticated
            
            if current_user.id == int(ID2):
                self.can_create = False
                self.can_edit = False
                self.can_delete = False
                return current_user.is_authenticated

    def inaccessible_callback(self, name, **kwargs):
        return abort(403)


flaskadmin = Admin(app, template_mode='bootstrap4', name="Administrative Panel",
index_view=MyAdminIndexView(url='/adminpagedontuse/'), url='/adminpagedontuse/')
flaskadmin.add_view(SystemLogController(SystemLog, db.session, name='System Log', url="/admin/system-log/"))
flaskadmin.add_view(UserController(Users, db.session, name='Users', url="/admin/users/"))


@app.before_request
def redirect_nonwww():
    urlparts = urlparse(request.url)
    if urlparts.netloc == 'www.vatsimpakistan.com':
        urlparts_list = list(urlparts)
        urlparts_list[1] = 'vatsimpakistan.com'
        return redirect(urlunparse(urlparts_list), code=301)


@app.route("/")
def index():
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

    return render_template("index.html",is_logged_in=is_logged_in, name=name, len_events=len(Events.query.all()), events_query=Events.query.all(),
    len_controllers=len(Onlineatc.query.all()), controllers=Onlineatc.query.all(), 
    residents=Stats.query.filter_by(value=1).first().json_data, 
    visitors=Stats.query.filter_by(value=2).first().json_data, 
    active_controllers=Stats.query.filter_by(value=4).first().json_data, 
    vacc_hours=Stats.query.filter_by(value=3).first().json_data, check_admin=check_admin, 
    uploads=Uploads.query.filter_by(homepage="True").order_by(Uploads.id.desc()).limit(6).all(), 
    policies=Administrative.query.all(), news=News.query.order_by(News.id.desc()).limit(2).all())

if __name__ == "__main__":
    #serve(app, host='0.0.0.0', threads=8)
    app.run(debug=True)