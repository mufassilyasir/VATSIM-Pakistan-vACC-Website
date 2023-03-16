from flask import Blueprint, render_template, abort, url_for, redirect, request, flash
from .models import Administrative, Discord, Notams, Role, Staff, SystemLog, Uploads, db, Users
from flask_login import current_user
from dotenv import load_dotenv
from werkzeug.utils import secure_filename
from datetime import datetime

import os

load_dotenv()

ZERO = os.getenv("ZERO")
ONE = os.getenv("ONE")


admin = Blueprint("admin", __name__)


@admin.route('/admin')
def adminpage():
    if current_user.is_authenticated:
        if current_user.has_role(ZERO) or current_user.has_role(ONE):
            
            query = Users.query.filter_by(id=current_user.id).first()
            
            if query.Use_CID == "False" and query.Use_First_Name == "False":
                name = query.Full_Name
            elif query.Use_CID == "False" and query.Use_First_Name == "True":
                name = query.First_Name
            elif query.Use_CID == "True":
                name = current_user.id

            return render_template("admin.html", is_logged_in="True", name=name, check_admin="True", 
            policies=Administrative.query.all(), users=len(Users.query.all()), 
            discord_accounts=len(Discord.query.all()), staffs=Staff.query.filter_by(appointed="True").all(), 
            staff_positions=Staff.query.filter_by(appointed="False").all(), id=current_user.id, 
            uploads=Uploads.query.order_by(Uploads.id.desc()).all(), notams=Notams.query.all(),
            time_now=datetime.utcnow().strftime("%d-%m-%Y, %H:%M"))

        else:
            abort(403)
    else:
        return redirect(url_for("auth.login"))


@admin.route('/admin/policy/add', methods=['POST'])
def policyadd():
    if current_user.is_authenticated:
        if current_user.has_role(ZERO) or Staff.query.filter_by(id=current_user.id).first().staff_callsign == "ACCPAK1":
            if request.method == "POST":
                if request.files:
                    policy = request.files['policy']
                    policy_name = request.form['policy_name']
                    if policy.filename == "":
                        flash("Cannot upload nothing", category='error')
                        return redirect(url_for("myadmin.adminpage"))

                    saving_path = f"/static/uploads/policies"
                    policy.save(os.path.join(
                        f"{os.path.dirname(os.path.abspath(__file__))}/{saving_path}", secure_filename(policy.filename)))
                    
                    new_policy = Administrative(policy_name = policy_name, policy_link = f"{saving_path}/{secure_filename(policy.filename)}")
                    db.session.add(new_policy)
                    system_log = SystemLog(action_by=current_user.id, action=f"Added Policy {policy_name}",
                    timestamp=f"{datetime.utcnow().strftime('%d-%m-%Y %H:%M:%S')} UTC")
                    db.session.add(system_log)
                    db.session.commit()
                    flash("Policy added successfully.", category='success')
                    return redirect(url_for("myadmin.adminpage"))
        else:
            flash("Only the vACC Director may remove policies.", category='error')
            return redirect(url_for("myadmin.adminpage"))

@admin.route('/admin/policy/remove', methods=['POST'])
def policyremove():
    if current_user.is_authenticated:
        if current_user.has_role(ZERO) or Staff.query.filter_by(id=current_user.id).first().staff_callsign == "ACCPAK1":
            if request.method == "POST":
                try:
                    policy = request.form['group']
                except KeyError:
                    policy = None

                if policy != None:

                    os.remove(f"{os.path.dirname(os.path.abspath(__file__))}{Administrative.query.filter_by(id=policy).first().policy_link}")
                    
                    system_log = SystemLog(action_by=current_user.id, action=f'Deleted Policy "{Administrative.query.filter_by(id=policy).first().policy_name}"',
                                        timestamp=f"{datetime.utcnow().strftime('%d-%m-%Y %H:%M:%S')} UTC")
                    db.session.add(system_log)

                    Administrative.query.filter_by(id=policy).delete()
                    db.session.commit()
                    
                    flash("Policy deleted successfully", category='success')
                    return redirect(url_for("myadmin.adminpage"))

                else:
                    flash("Error deleting a policy, make sure you're not deleting something you shouldn't", category='error')
                    return redirect(url_for("myadmin.adminpage"))
        else:
            flash("Only the vACC Director may remove policies.", category='error')
            return redirect(url_for("myadmin.adminpage"))


@admin.route('/admin/staff/appoint', methods=['POST'])
def staffappoint():
    if current_user.is_authenticated:
        if current_user.has_role(ZERO) or Staff.query.filter_by(id=current_user.id).first().staff_callsign == "ACCPAK1":
            if request.method == "POST":
                staff_vatsim_id = request.form['staff_vatsim_id']
                staff_position = request.form['staff_position']
                staff_callsign = request.form['callsign']

                query = Users.query.filter_by(id=staff_vatsim_id).first()
                if query:
                    query2 = Staff.query.filter_by(staff_callsign=staff_callsign).first()
                    query2.id = staff_vatsim_id
                    query2.staff_position = staff_position
                    query2.staff_name = query.Full_Name
                    query2.staff_bio = "False"
                    query2.staff_bio_itself = "This person chose not to add a biography."
                    query2.appointed = "True"
                    query.StaffPosition = staff_position

                    Role1 = Role.query.filter_by(id=1).first()
                    User = Users.query.filter_by(id=staff_vatsim_id).first()
                    if User:
                        try:
                            Role1.users.append(User)
                        except:
                            flash("Error, assigning permission, contact muf", category='error')
                            return redirect(url_for("myadmin.adminpage"))
                    else:
                        print(f"Found {staff_vatsim_id} Suspended and unable to restrict them in database")

                    discord_query = Discord.query.filter_by(id=staff_vatsim_id).first()

                    if query.user_own_upload == "True":
                        user_avatar_path = query.user_own_upload_link
                    elif discord_query:
                        if discord_query.discord_profile_use == "True":
                            user_avatar_path = discord_query.discord_profile_link
                        else:
                            user_avatar_path = f"/static/public/initials/{staff_vatsim_id}.png"
                    else:
                        user_avatar_path = f"/static/public/initials/{staff_vatsim_id}.png"

                    query2.staff_image_url = user_avatar_path

                    time_now = datetime.utcnow()
                    system_log = SystemLog(action_by=current_user.id, action=f"Appointed {staff_vatsim_id} as {staff_callsign}",
                                        timestamp=f"{time_now.strftime('%d-%m-%Y %H:%M:%S')} UTC")
                    db.session.add(system_log)
                    db.session.commit()
                    flash("Staff appointed successfully", category='success')
                    return redirect(url_for("myadmin.adminpage"))
                else:
                    flash("Member not found in our database. Hint: Tell them to login.", category='error')
                    return redirect(url_for("myadmin.adminpage"))

        else:
            flash("Only the vACC Director may appoint new vACC staff members.", category='error')
            return redirect(url_for("myadmin.adminpage"))

@admin.route('/admin/staff/remove', methods=['POST'])
def staffremove():
    if current_user.is_authenticated:
        if current_user.has_role(ZERO) or Staff.query.filter_by(id=current_user.id).first().staff_callsign == "ACCPAK1":
            if request.method == "POST":
                staff_id = request.form['group']

                query = Staff.query.filter_by(id=staff_id).first()
                if query:
                    if int(staff_id) != int(current_user.id):
                        if query.staff_callsign == "ACCPAK1":
                            query.id = "1"
                        elif query.staff_callsign == "ACCPAK2":
                            query.id = "2"
                        elif query.staff_callsign == "ACCPAK3":
                            query.id = "3"
                        elif query.staff_callsign == "ACCPAK4":
                            query.id = "4"
                        
                        query.staff_position = "False"
                        query.staff_name = "None"
                        query.staff_bio = "False"
                        query.staff_bio_itself = "None"
                        query.appointed = "False"
                        Users.query.filter_by(id=staff_id).first().StaffPosition = "None"

                        Role0 = Role.query.filter_by(id=1).first()
                        User = Users.query.filter_by(id=staff_id).first()
                        try:
                            Role0.users.remove(User)
                        except:
                            flash("ERROR COULD NOT REMOVE STAFF PERMISSIONS PLEASE CONTACT MUF!! This is important.", category='error')
                            return redirect(url_for("myadmin.adminpage"))

                        system_log = SystemLog(action_by=current_user.id, action=f"Removed {staff_id} as Staff",
                                            timestamp=f"{datetime.utcnow().strftime('%d-%m-%Y %H:%M:%S')} UTC")
                        db.session.add(system_log)
                        db.session.commit()
                        flash("Staff removed", category='success')
                        return redirect(url_for("myadmin.adminpage"))
                    
                    else:
                        flash("Cannot remove yourself as staff.", category='error')
                        return redirect(url_for("myadmin.adminpage"))
                else:
                    flash("Staff not found", category='error')
                    return redirect(url_for("myadmin.adminpage"))
        else:
            flash("Only the vACC Director may remove vACC staff members.", category='error')
            return redirect(url_for("myadmin.adminpage"))


@admin.route("/admin/upload/media", methods=['POST'])
def uploadmedia():
    if current_user.is_authenticated:
        if current_user.has_role(ZERO) or current_user.has_role(ONE):
            if request.method == "POST":
                if request.files:
                    media = request.files['media']
                    media_name = request.form['name']
                    homepage = request.form.get('homepage')

                    if media.filename == "":
                        flash("Cannot upload nothing", category='error')
                        return redirect(url_for("myadmin.adminpage"))
                    if len(media_name) < 3:
                        flash("Please state where this media will be used.", category='error')
                        return redirect(url_for("myadmin.adminpage"))

                    if homepage != None:
                        homepage_val = "True"
                    elif homepage == None:
                        homepage_val = "False"

                    saving_path = f"/static/uploads"
                    media.save(os.path.join(
                        f"{os.path.dirname(os.path.abspath(__file__))}/{saving_path}", secure_filename(media.filename)))
                    
                    new_upload = Uploads(name = media_name, link = f"{saving_path}/{secure_filename(media.filename)}", uploaded_by = current_user.id,
                    homepage = homepage_val)
                    db.session.add(new_upload)
                    system_log = SystemLog(action_by=current_user.id, action=f'Uploaded media with use as {media_name}',
                    timestamp=f"{datetime.utcnow().strftime('%d-%m-%Y %H:%M:%S')} UTC")
                    db.session.add(system_log)
                    db.session.commit()
                    flash("Media uploaded successfully.", category='success')
                    return redirect(url_for("myadmin.adminpage"))

@admin.route('/admin/delete/media/<id>')
def deletemedia(id):
    if current_user.is_authenticated:
        if current_user.has_role(ONE) or current_user.has_role(ZERO):
            query = Uploads.query.filter_by(id=id).first()
            if query:
                try:
                    os.remove(f"{os.path.dirname(os.path.abspath(__file__))}{Uploads.query.filter_by(id=id).first().link}")
                except:
                    pass
                Uploads.query.filter_by(id=id).delete()
                system_log = SystemLog(action_by=current_user.id, action=f'Deleted media that was uploaded by {query.uploaded_by} with use as {query.name}',
                timestamp=f"{datetime.utcnow().strftime('%d-%m-%Y %H:%M:%S')} UTC")
                db.session.add(system_log)
                db.session.commit()
                flash("Media deleted successfully", category='success')
                return redirect(url_for("myadmin.adminpage"))
            else:
                flash("Media could not be found", category='error')
                return redirect(url_for("myadmin.adminpage"))

@admin.route('/admin/notam/add', methods=['POST'])
def notamadd():
    if current_user.is_authenticated:
        if current_user.has_role(ONE) or current_user.has_role(ZERO):
            if request.method == "POST":
                notam = request.form['notam']
                group = request.form.get('group')
                notamcode = request.form['notamcode']
                notamstart = request.form['notamstart']
                permenanent_notam = request.form.get('permanent_notam')

                if permenanent_notam == "1":
                    notamend = "Permanent"
                else:
                    notamend = request.form['notamend']

                if group == None:
                    flash("Please select an airfield to update NOTAM for.", category='error')
                    return redirect(url_for("myadmin.adminpage"))
                if len(notam) < 10:
                    flash("Are you sure you added something in the NOTAM?", category='error')
                    return redirect(url_for("myadmin.adminpage"))
                if len(notamcode) < 5:
                    flash("Are you sure you added something in the NOTAM Code?", category='error')
                    return redirect(url_for("myadmin.adminpage"))
                if len(notamstart) < 6:
                    flash("Are you sure you added something in the NOTAM Start Date?", category='error')
                    return redirect(url_for("myadmin.adminpage"))
                if len(notamend) < 6:
                    flash("Are you sure you added something in the NOTAM End Date?", category='error')
                    return redirect(url_for("myadmin.adminpage"))

                if group == "OPLA":
                    airport_name = "Allama Iqbal International Airport, Lahore"
                    image = "/static/img/websiteuploads/AllamaIqbalAirport.png"
                elif group == "OPKC":
                    airport_name = "Jinnah International Airport, Karachi"
                    image = "/static/img/websiteuploads/jinnahterminal.png"
                elif group == "OPIS":
                    airport_name = "Islamabad International Airport, Islamabad"
                    image = "/static/img/websiteuploads/islmamabadterminal.png"
                elif group == "OPPS":
                    airport_name = "Bacha Khan International Airport, Peshawar"
                    image = "/static/img/websiteuploads/bachakhan.png"
                elif group == "OPQT":
                    airport_name = "Quetta International Airport, Quetta"
                    image = "/static/img/websiteuploads/quettaterminal.png"
                elif group == "OPFA":
                    airport_name = "Faisalabad International Airport, Faisalabad"
                    image = "/static/img/websiteuploads/faisalabadterminal.png"
                elif group == "OPMT":
                    airport_name = "Multan International Airport, Multan"
                    image = "/static/img/websiteuploads/multanterminal.png"
                elif group == "OPST":
                    airport_name = "Sialkot International Airport, Sialkot"
                    image = "/static/img/websiteuploads/Sialkot.jpg"
                elif group == "OPSD":
                    airport_name = "Skardu Airport, Skardu"
                    image = "/static/img/websiteuploads/Skardu.jpg"
                elif group == "OPKR":
                    airport_name = "Karachi Control FIR"
                    image = ""
                elif group == "OPLR":
                    airport_name = "Lahore Control FIR"
                    image = ""
                else:
                    image = ""
                    airport_name = ""


                system_log = SystemLog(action_by=current_user.id, action=f'Added {group} NOTAM',
                timestamp=f"{datetime.utcnow().strftime('%d-%m-%Y %H:%M:%S')} UTC")
                add_notam = Notams(notam=notam, icao=group, start_date=notamstart, end_date=notamend, 
                notam_code=notamcode, airport_name=airport_name, image=image)
                db.session.add(system_log)
                db.session.add(add_notam)
                db.session.commit()
                flash(f"{group} NOTAM added successfully.", category='success')
                return redirect(url_for("myadmin.adminpage"))

        else:
            abort(403)
    else:
        return redirect(url_for("auth.login"))

@admin.route('/admin/notam/delete', methods=['POST'])
def notamdelete():
    if current_user.is_authenticated:
        if current_user.has_role(ZERO) or current_user.has_role(ONE):
            if request.method == "POST":
                notamid = request.form.get('group')

                if notamid != None:
                    if Notams.query.filter_by(id=notamid).first():
                        Notams.query.filter_by(id=notamid).delete()
                        db.session.commit()
                        flash("NOTAM deleted successfully", category='success')
                    return redirect(url_for("myadmin.adminpage"))
                else:
                    flash("What do you wanna see, error?", category='error')
                    return redirect(url_for("myadmin.adminpage"))
        else:
            abort(403)