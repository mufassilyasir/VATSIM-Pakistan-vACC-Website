from flask import Blueprint
from flask_security.core import RoleMixin
from flask_login import UserMixin
from . import db


models = Blueprint("models", __name__, static_folder="static", template_folder="templates")

class Role(db.Model, RoleMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    description = db.Column(db.String(100))

    def __str__(self):
        return self.name

roles_users = db.Table('roles_users',
                       db.Column('user_id', db.Integer, db.ForeignKey('users.id')),
                       db.Column('role_id', db.Integer, db.ForeignKey('role.id')))

class Users(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    First_Name = db.Column(db.String(500))
    Last_Name = db.Column(db.String(500))
    Full_Name = db.Column(db.String(500))
    Email = db.Column(db.String(450))
    RatingLong = db.Column(db.String(550))
    RatingShort = db.Column(db.String(500))
    PilotShort = db.Column(db.String(500))
    PilotLong = db.Column(db.String(500))
    DivisionID = db.Column(db.String(500), default="None")
    DivisionName = db.Column(db.String(500), default="None")
    RegionID = db.Column(db.String(500), default="None")
    RegionName = db.Column(db.String(500), default="None")
    SubdivisionID = db.Column(db.String(500), default="None")
    SubdivisionName = db.Column(db.String(500), default="None")
    Discord_Linked = db.Column(db.String(35), default="False")
    DiscordServerJoin = db.Column(db.String(35), default="False")
    StaffPosition = db.Column(db.String(500), default="None")
    PrivacyPolicyAccepted = db.Column(db.String(500), default="False")
    OptedinEmails = db.Column(db.String(500), default="False")
    Use_CID = db.Column(db.String(500))
    Use_First_Name = db.Column(db.String(500), default="False")
    user_own_upload = db.Column(db.String(500), default="False")
    user_own_upload_link = db.Column(db.String(450), default="None")
    roles = db.relationship('Role', secondary=roles_users, backref=db.backref('users', lazy='select'))

    def __init__(self, id, First_Name, Last_Name, Full_Name, Email, RatingLong, RatingShort, PilotShort, PilotLong, DivisionID, DivisionName, RegionID, RegionName, SubdivisionID, SubdivisionName, Use_CID):
        self.id = id
        self.First_Name = First_Name
        self.Last_Name = Last_Name
        self.Full_Name = Full_Name
        self.Email = Email
        self.RatingLong = RatingLong
        self.RatingShort = RatingShort
        self.PilotLong = PilotLong
        self.PilotShort = PilotShort
        self.DivisionID = DivisionID
        self.DivisionName = DivisionName
        self.RegionID = RegionID
        self.RegionName = RegionName
        self.SubdivisionID = SubdivisionID
        self.SubdivisionName = SubdivisionName
        self.Use_CID = Use_CID

    def get_id(self):
        return (self.id)

    def has_role(self, *args):
        return set(args).issubset({role.name for role in self.roles})

    def __repr__(self) -> str:
        return super().__repr__()

class Discord(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    is_discord_linked = db.Column(db.String(500))
    is_server_joined = db.Column(db.String(500))
    discord_user_id = db.Column(db.String(400))
    discord_profile_use = db.Column(db.String(500), default="False")
    discord_profile_link = db.Column(db.String(500), default="None")
    discord_username = db.Column(db.String(500))

class Events(db.Model):
    value = db.Column(db.Integer, primary_key=True)
    start_time = db.Column(db.String(500))
    end_time = db.Column(db.String(500))
    event_link = db.Column(db.String(500))
    event_banner = db.Column(db.String(500))
    last_updated = db.Column(db.String(500))

class Stats(db.Model):
    value = db.Column(db.Integer, primary_key=True)
    json_data = db.Column(db.String(500))
    time = db.Column(db.String(500))
    time_datetime = db.Column(db.JSON())

class SystemLog(db.Model):
    value = db.Column(db.Integer, primary_key=True)
    action_by = db.Column(db.String(500))
    action = db.Column(db.String(500))
    timestamp = db.Column(db.String(500))

class Staff(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    staff_position = db.Column(db.String)
    staff_name = db.Column(db.String)
    staff_bio = db.Column(db.String)
    staff_bio_itself = db.Column(db.String)
    staff_callsign = db.Column(db.String)
    appointed = db.Column(db.String)
    staff_image_url = db.Column(db.String)

class Onlineatc(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    cid = db.Column(db.Integer)
    controller_name = db.Column(db.String)
    facility_name = db.Column(db.String)
    callsign = db.Column(db.String)
    facility_db = db.Column(db.String)

class Administrative(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    policy_name = db.Column(db.String)
    policy_link = db.Column(db.String)

class Controllerroster(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.JSON())

class News(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    subject = db.Column(db.String)
    content = db.Column(db.String)
    banner_link = db.Column(db.String)
    created_by = db.Column(db.String)
    time = db.Column(db.String)

class Uploads(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    link = db.Column(db.String)
    uploaded_by = db.Column(db.String)
    name = db.Column(db.String)
    homepage = db.Column(db.String)


class Notams(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    notam = db.Column(db.String)
    icao = db.Column(db.String)
    start_date = db.Column(db.String)
    end_date = db.Column(db.String)
    notam_code = db.Column(db.String)
    airport_name = db.Column(db.String)
    image = db.Column(db.String)