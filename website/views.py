from flask import Blueprint, redirect, url_for, render_template, request, flash, abort, send_file
from .models import Administrative, Controllerroster, Discord, News, Notams, Staff, Stats, Uploads, Users, SystemLog, db
from flask_login import current_user
from .emailutil import post_discord_message, send_email
from .utils import is_human, allowed_image_size, allowedextensions
from dotenv import load_dotenv
from datetime import datetime
from werkzeug.utils import secure_filename
from .discordutils import DISCORD_BOT_TOKEN, DISCORD_ENDPOINT, updatename

import os


views = Blueprint("views", __name__)
load_dotenv()

MEMBERSHIP_EMAIL = os.getenv("MEMBERSHIP_EMAIL")
ZERO = os.getenv("ZERO")
ONE = os.getenv("ONE")
THREE = os.getenv("THREE")
STAFF_EMAIL = os.getenv("STAFF_EMAIL")
DISCORD_LOG_CHANNEL_ID = os.getenv("DISCORD_LOG_CHANNEL_ID")
DISCORD_BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")
DISCORD_ENDPOINT = os.getenv("DISCORD_ENDPOINT")


@views.route("/privacy-policy", methods=['POST', 'GET'])
def privacypolicy():
    if current_user.is_authenticated:
        query = Users.query.filter_by(id=current_user.id).first()
        if query.PrivacyPolicyAccepted == "False":

            if query.Use_CID == "False" and query.Use_First_Name == "False":
                name = query.Full_Name
            elif query.Use_CID == "False" and query.Use_First_Name == "True":
                name = query.First_Name
            elif query.Use_CID == "True":
                name = current_user.id
            
            is_logged_in = "True"

            if current_user.has_role(ONE):
                check_admin = "True"
            elif current_user.has_role(ZERO):
                check_admin = "True"
            else:
                check_admin = "False"
    

            return render_template("/privacypolicy.html", is_logged_in=is_logged_in, name=name, check_admin=check_admin,
            policies=Administrative.query.all())
        else:
            return redirect(url_for("index"))
    else:
        return redirect(url_for("index"))


@views.route("/privacy-policy/deny", methods=['POST'])
def privacypolicydeny():
    if current_user.is_authenticated:
        query = Users.query.filter_by(id=current_user.id).first()
        if query.PrivacyPolicyAccepted == "False":
            Users.query.filter_by(id=current_user.id).delete()
            time_now = datetime.utcnow()
            system_log = SystemLog(action_by=current_user.id, action=f"Denied privacy policy. Data deleted.",
                                   timestamp=f"{time_now.strftime('%d-%m-%Y %H:%M:%S')} UTC")
            db.session.add(system_log)
            db.session.commit()
            return redirect(url_for("auth.logout"))

        else:
            return redirect(url_for("index"))
    else:
        return redirect(url_for("auth.login"))


@views.route("/privacy-policy/accept", methods=['POST', 'GET'])
def privacypolicyaccept():
    if current_user.is_authenticated:
        query = Users.query.filter_by(id=current_user.id).first()
        if query.PrivacyPolicyAccepted == "False":
            if request.method == "POST":
                emailopt = request.form.get("optinemail")
                if emailopt == "1":
                    query.OptedinEmails = "True"

                query.PrivacyPolicyAccepted = "True"
                time_now = datetime.utcnow()
                system_log = SystemLog(action_by=current_user.id, action=f"Accepted privacy policy and sent welcome email to them.",
                                    timestamp=f"{time_now.strftime('%d-%m-%Y %H:%M:%S')} UTC")
                db.session.add(system_log)
                db.session.commit()

                if query.Use_CID == "False" and query.Use_First_Name == "False":
                    name = query.Full_Name
                elif query.Use_CID == "False" and query.Use_First_Name == "True":
                    name = query.First_Name
                elif query.Use_CID == "True":
                    name = current_user.id

                flash(f"Welcome {name}!", category='success')
                return redirect(url_for("views.myprofile"))
            else:
                return redirect(url_for("index"))
        else:
            return redirect(url_for("index"))
    else:
        return redirect(url_for("index"))


@views.route("/contact-us", strict_slashes=False, methods=['POST', 'GET'])
def contactus():
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

        id = current_user.id
        email = query.Email

    else:
        is_logged_in = "False"
        name = "none"
        check_admin = "False"
        id = "none"
        email=None

    if request.method == "POST":
        if current_user.is_authenticated:
            email = Users.query.filter_by(id=current_user.id).first().Email
            name = Users.query.filter_by(id=current_user.id).first().Full_Name
        else:
            email = request.form['email']
            name = request.form['name']
        subject = request.form['subject']
        message = request.form['message']
        captcha_response = request.form['g-recaptcha-response']

        if len(name) < 4:
            flash("Kindly ensure your name is greater than 4 letters. If this is a mistake, please let us know.", category='error')
            return redirect(url_for("views.contactus"))

        if len(email) < 4:
            flash("Kindly ensure your email is greater than 4 letters. If this is a mistake, please let us know.", category='error')
            return redirect(url_for("views.contactus"))

        if len(subject) < 4:
            flash("Kindly ensure your subject is greater than 4 letters. If this is a mistake, please let us know.", category='error')
            return redirect(url_for("views.contactus"))

        if len(message) < 4:
            flash("Kindly ensure your message is greater than 4 letters. If this is a mistake, please let us know.", category='error')
            return redirect(url_for("views.contactus"))

        recaptcha_response = is_human(captcha_response, request.remote_addr)

        if str(recaptcha_response['success']) == "True":
            #staff
            send_email('New Contact Form Message in VATSIM Pakistan vACC', 'no-reply@vatsimpakistan.com',
                [STAFF_EMAIL], None,None,render_template("/email/contact-form.html", name=name, email=email, subject=subject, message=message, ip=request.remote_addr))
            # user
            send_email('Thank you for contacting us - VATSIM Pakistan vACC', 'no-reply@vatsimpakistan.com',
            [email], None, None, f"<p>Thank you for contacting us, {name} we will be in touch shortly<p><br><br><p><strong>Regards, Pakistan vACC Staff</strong></p>")

            data = {"content": f"<@&810135707586134032> New contact us message received."}
            post_discord_message(data, DISCORD_BOT_TOKEN, DISCORD_ENDPOINT, DISCORD_LOG_CHANNEL_ID)

            flash("Thank you for contacting us, we will get back to you as soon as possible.", category='success')

        elif str(recaptcha_response['success']) == "False":
            flash("Oops, recaptcha validation error.", category='error')

        return redirect(url_for("views.contactus"))

    return render_template("contactus.html", is_logged_in=is_logged_in, name=name, check_admin=check_admin, id=id, email=email,
    policies=Administrative.query.all())


@views.route('/about-us')
def aboutus():
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
    
    staff = Staff.query.filter_by(appointed="True").order_by(Staff.staff_callsign.asc()).all()
    return render_template("aboutus.html", name=name, is_logged_in=is_logged_in, len_staff=len(staff), staffs=staff,
    check_admin=check_admin, policies=Administrative.query.all())


@views.route('/my/profile', methods=['GET', 'POST'])
def myprofile():
    if current_user.is_authenticated:
        if current_user.has_role(THREE) == False:
            query = Users.query.filter_by(id=current_user.id).first()
            if query.PrivacyPolicyAccepted == "True":
                is_logged_in = "True"
                staff_query = Staff.query.filter_by(id=current_user.id).first()

                if query.Use_CID == "False" and query.Use_First_Name == "False":
                    selected = "1"
                    name = query.Full_Name
                elif query.Use_CID == "False" and query.Use_First_Name == "True":
                    selected = "2"
                    name = query.First_Name
                elif query.Use_CID == "True":
                    selected = "3"
                    name = current_user.id

                if current_user.has_role(ONE):
                    check_admin = "True"
                    staff_role = "vACC Staff"
                elif current_user.has_role(ZERO):
                    staff_role = "Administrator"
                    check_admin = "True"
                else:
                    check_admin = "False"
                    staff_role = "None"

                staff_position = query.StaffPosition

                if query.Use_CID == "False" and query.Full_Name != "None" and query.First_Name != "None":
                    naming = query.Full_Name
                    name_first = query.First_Name
                    UseCID = "False"
                    

                elif query.Use_CID == "True" and query.Full_Name != "None" and query.First_Name != "None":
                    naming = query.Full_Name
                    name_first = query.First_Name
                    UseCID = "False"
                   

                elif query.Use_CID == "True" and query.Full_Name == "None" and query.First_Name == "None":
                    naming = "None"
                    name_first = "None"
                    UseCID = "True"

                discord_query = Discord.query.filter_by(id=current_user.id).first()

                if query.user_own_upload == "True":
                    user_avatar_path = query.user_own_upload_link
                elif discord_query:
                    if discord_query.discord_profile_use == "True":
                        user_avatar_path = discord_query.discord_profile_link
                    else:
                        user_avatar_path = f"/static/public/initials/{current_user.id}.png"
                else:
                    user_avatar_path = f"/static/public/initials/{current_user.id}.png"

                if discord_query:
                    is_linked = discord_query.is_discord_linked
                    is_member = discord_query.is_server_joined
                    discord_profile_use = discord_query.discord_profile_use
                    discord_profile_link = discord_query.discord_profile_link
                    discord_username_whole = str(discord_query.discord_username)
                    discord_username = discord_username_whole.split('#')[0]
                    discord_discriminator = discord_username_whole.split('#')[1]
                else:
                    is_linked = "False"
                    is_member = "False"
                    discord_profile_use = "False"
                    discord_profile_link = "None"
                    discord_username = "None"
                    discord_discriminator = "None"

                if request.method == "POST":

                    try:
                        group = request.form["group"]
                    except KeyError:
                        group = "0"

                    try:
                        bio = request.form['bio']
                    except KeyError:
                        bio = None
                    
                    try:
                        emailoptincheck = request.form['emailoptincheck']
                    except KeyError:
                        emailoptincheck = False

                    if group != "0":

                        if group == "1":
                            if query.Use_CID != "True":
                                query.Use_CID = "True"
                                query.Use_First_Name = "False"
                                time_now = datetime.utcnow()
                                system_log = SystemLog(action_by=current_user.id, action=f"Changed their name to use VATSIM CID only.",
                                                        timestamp=f"{time_now.strftime('%d-%m-%Y %H:%M:%S')} UTC")
                                db.session.add(system_log)
                                db.session.commit()
                                query1 = Discord.query.filter_by(id=current_user.id).first()
                                if query1:
                                    updatename(query1.discord_user_id, "None", current_user.id, group)

                                flash("Name Changed Successfully!", category='success')
                                return redirect(url_for("views.myprofile"))

                        elif group == "2":
                            if query.Use_CID == "False" and query.Use_First_Name == "False":
                               pass
                            else:
                                query.Use_CID = "False"
                                query.Use_First_Name = "False"
                                time_now = datetime.utcnow()
                                system_log = SystemLog(action_by=current_user.id, action=f"Changed their name to use VATSIM Full Name.",
                                                        timestamp=f"{time_now.strftime('%d-%m-%Y %H:%M:%S')} UTC")
                                db.session.add(system_log)
                                db.session.commit()
                                query1 = Discord.query.filter_by(id=current_user.id).first()
                                if query1:
                                    updatename(query1.discord_user_id, query.Full_Name, current_user.id, group)

                                flash("Name Changed Successfully!", category='success')
                                return redirect(url_for("views.myprofile"))

                        elif group == "3":
                            if query.Use_First_Name != "True":
                                query.Use_CID = "False"
                                query.Use_First_Name = "True"
                                time_now = datetime.utcnow()
                                system_log = SystemLog(action_by=current_user.id, action=f"Changed their name to use VATSIM First Name only.",
                                                        timestamp=f"{time_now.strftime('%d-%m-%Y %H:%M:%S')} UTC")
                                db.session.add(system_log)
                                db.session.commit()
                                query1 = Discord.query.filter_by(id=current_user.id).first()
                                if query1:
                                    updatename(query1.discord_user_id, query.First_Name, current_user.id, group)

                                flash("Name Changed Successfully!", category='success')
                                return redirect(url_for("views.myprofile"))

                    if bio != None:
                        if staff_query:
                            if bio != staff_query.staff_bio_itself:
                                staff_query.staff_bio_itself = bio
                                staff_query.staff_bio = "True"
                                db.session.commit()
                                flash("Staff biography updated successfully.", category='success')
                                return redirect(url_for("views.myprofile"))
                    
                    if emailoptincheck != False:
                        if query.OptedinEmails != "True":
                            query.OptedinEmails = "True"
                            db.session.commit()
                            flash("Successfully opted in marketing emails.", category='success')
                            return redirect(url_for("views.myprofile"))
                    else:
                        if query.OptedinEmails != "False":
                            query.OptedinEmails = "False"
                            db.session.commit()
                            flash("Successfully opted out of marketing emails.", category='success')
                            return redirect(url_for("views.myprofile"))

                if staff_query:
                    staffbio = staff_query.staff_bio
                    if staffbio != "False":
                        staff_bio_itself = staff_query.staff_bio_itself
                    else:
                        staff_bio_itself = "None"
                        staffbio="None"
                else:
                    staff_bio_itself="None"
                    staffbio="None"

                return render_template("myprofile.html", is_logged_in=is_logged_in, check_admin=check_admin, name=name, naming=naming, UseCID=UseCID, 
                name_first=name_first, staff_position=staff_position, staff_role=staff_role, 
                user_avatar_path=user_avatar_path, cid=current_user.id, email=query.Email, 
                atc1=query.RatingLong, atc2=query.RatingShort, policies=Administrative.query.all(),
                pilot1=query.PilotLong, pilot2=query.PilotShort, division=query.DivisionName, 
                subdivision=query.SubdivisionName, region=query.RegionName, 
                staffbio=staffbio, staff_bio_itself=staff_bio_itself, is_linked=is_linked, is_member=is_member, 
                discord_profile_use=discord_profile_use, discord_profile_link=discord_profile_link, 
                emailoptin=query.OptedinEmails,selected=selected, discord_username=discord_username, discord_discriminator=discord_discriminator)
            
            else:
                return redirect(url_for("views.privacypolicy"))
        else:
            abort(403)
    else:
        return redirect(url_for("auth.login"))


@views.route("/upload/avatar", methods=["POST"], strict_slashes=False)
def avataruploader():
    if current_user.is_authenticated:
        if current_user.PrivacyPolicyAccepted == "True":
            if current_user.has_role(THREE) == False:
                if request.method == "POST":
                    if request.files:
                        image = request.files['image']

                        if image == None:
                            flash("To upload an avatar you should give the file a name.", category='error')
                            return "1"

                        elif image.filename == "":
                            flash("To upload an avatar you should give the file a name.", category='error')

                        elif not allowed_image_size(request.cookies.get("size")):
                            flash("Kindly ensure, the file size is 2MB or less.", category='error')
                            return redirect(url_for("views.myprofile"))

                        elif not allowedextensions(image.filename):
                            flash("Avatar file extensions must be 'PNG', 'JPG', 'JPEG', 'GIF' extensions only.", category='error')

                        else:
                            path = f"{os.path.dirname(os.path.abspath(__file__))}/static/public/uploads/{current_user.id}"
                            if os.path.exists(path) == False:
                                os.chdir(f"{os.path.dirname(os.path.abspath(__file__))}/static/public/uploads")
                                os.makedirs(str(f"{current_user.id}"))

                            for files in os.listdir(path):
                                if files:
                                    os.remove(
                                        f"{os.path.dirname(os.path.abspath(__file__))}/static/public/uploads/{current_user.id}/{files}")

                            saving_path = f"/static/public/uploads/{current_user.id}"
                            image.save(os.path.join(
                                f"{os.path.dirname(os.path.abspath(__file__))}/{saving_path}", secure_filename(image.filename)))
                            query = Users.query.filter_by(id=current_user.id).first()
                            query1 = Discord.query.filter_by(id=current_user.id).first()
                            time_now = datetime.utcnow()
                            add_to_system_log = SystemLog(
                                action_by= current_user.id, action = "Uploaded custom avatar", timestamp = f"{time_now.strftime('%d-%m-%Y %H:%M:%S')} UTC")
                            db.session.add(add_to_system_log)
                            if query1:
                                query1.discord_profile_use = "False"
                            query.user_own_upload = "True"
                            query.user_own_upload_link = os.path.join(saving_path, secure_filename(image.filename))

                            if Staff.query.filter_by(id=current_user.id).first():
                                Staff.query.filter_by(id=current_user.id).first().staff_image_url = os.path.join(saving_path, secure_filename(image.filename))

                            db.session.commit()
                            flash("Avatar changed!", category='success')

                        return redirect(url_for("views.myprofile"))
            else:
                abort(403)
        else:
            return redirect(url_for("views.privacypolicy"))
    else:
        return redirect(url_for("auth.login"))

@views.route('/airspace')
def airspace():
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

    return render_template("airspace.html", is_logged_in=is_logged_in, check_admin=check_admin,
    name=name, policies=Administrative.query.all())

@views.route('/airfields-info')
def airfieldsinfo():
    if current_user.is_authenticated:
        if current_user.PrivacyPolicyAccepted == "True":
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

            return render_template("airfields.html", is_logged_in=is_logged_in, check_admin=check_admin, name=name,
            policies=Administrative.query.all())

        else:
            return redirect(url_for("views.privacypolicy"))
    else:
        return redirect(url_for("auth.login"))

@views.route('/controllers/<what_is>')
def controllers(what_is):
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

    if what_is == "roster":
        is_solo = "False"
        is_roster = "True"
        top_controllers = "False"
    elif what_is == "solo-validations":
        is_solo = "True"
        is_roster = "False"
        top_controllers = "False"
    elif what_is == "top":
        is_solo = "False"
        is_roster = "False"
        top_controllers = "True"
    else:
        abort(404)
    
    return render_template("controllers.html", residents=Controllerroster.query.filter_by(id=1).first().data, is_roster=is_roster, 
    is_solo=is_solo, visitors=Controllerroster.query.filter_by(id=2).first().data, is_logged_in=is_logged_in, 
    policies=Administrative.query.all(), solos=Controllerroster.query.filter_by(id=3).first().data, 
    name=name, check_admin=check_admin,top_controllers = top_controllers, 
    center_controllers=Stats.query.filter_by(value=5).first().time_datetime, 
    approach_controllers=Stats.query.filter_by(value=6).first().time_datetime,
    tower_controllers=Stats.query.filter_by(value=7).first().time_datetime,
    ground_controllers=Stats.query.filter_by(value=8).first().time_datetime, 
    month=Stats.query.filter_by(value=5).first().time)

@views.route('/controllers/resources/vatis/<icao>')
def downloadvatis(icao):
    if current_user.is_authenticated:
        if current_user.PrivacyPolicyAccepted == "True":
            found = False
            if found == False:
                query = Controllerroster.query.filter_by(id=1).first()
                for q in query.data:
                    if current_user.id == int(q['cid']):
                        if q['approved_for'] != None:
                            found = True
                        else:
                            flash("You do not have the required approvals to download this file.", category='error')
                            return redirect(url_for("views.myprofile"))
            
            if found == False:
                query = Controllerroster.query.filter_by(id=2).first()
                for q in query.data:
                    if current_user.id == int(q['cid']):
                        if q['approved_for'] != None:
                            found = True
                        else:
                            flash("You do not have the required approvals to download this file.", category='error')
                            return redirect(url_for("views.myprofile"))

            if found == True:
                if icao == "opla":
                    path = f"{os.path.dirname(os.path.abspath(__file__))}/static/uploads/vATIS/vATIS_Facility_-_Allama_Iqbal_Intl_OPLA.gz"
                    return send_file(path, as_attachment=True)
                elif icao == "opkc":
                    path = f"{os.path.dirname(os.path.abspath(__file__))}/static/uploads/vATIS/vATIS_Facility_-_Jinnah_Intl_OPKC.gz"
                    return send_file(path, as_attachment=True)
                elif icao == "opis":
                    path = f"{os.path.dirname(os.path.abspath(__file__))}/static/uploads/vATIS/vATIS_Facility_-_Islamabad_International_OPIS.gz"
                    return send_file(path, as_attachment=True)
                else:
                    flash("Why search for an airport that is not mentioned?", category='error')
                    return redirect(url_for("views.myprofile"))
            else:
                flash("You are not an approved visitor or a resident controller in the vACC.", category='error')
                return redirect(url_for("views.myprofile"))
        else:
            return redirect(url_for("views.privacypolicy"))
    else:
        return redirect(url_for("auth.login"))

@views.route("/news/<id>")
def news(id):
    if id == "all":
        show_all = "True"
        news = News.query.order_by(News.id.desc()).all()
    else:
        try:
            int(id)
        except:
            return abort(404)
        else:
            if int(id) != 1:
                show_all = "False"
                news_check = News.query.filter_by(id=int(id)).first()
                if news_check:
                    news = News.query.filter_by(id=int(id)).first()
                else:
                    abort(404)
            else:
                abort(404)
                
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

    

    return render_template("news.html", name=name, check_admin=check_admin, is_logged_in=is_logged_in,
    policies=Administrative.query.all(), news=news, show_all=show_all)

@views.route('/media/all')
def mediaall():
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

    return render_template("media.html", name=name, check_admin=check_admin, is_logged_in=is_logged_in,
    policies=Administrative.query.all(), uploads=Uploads.query.filter_by(homepage="True").order_by(Uploads.id.desc()).all())


@views.route('/notams/<view>')
def notams(view):
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

    if view == "all":
        notam = Notams.query.all()
        notam1 = []
        notams = []
        for n in notam:
            if n.icao not in notam1:
                notam1.append(n.icao)
                notams.append(n)
        view_is = "all"
        image="None"
        airport_name = "None"
    else:
        query = Notams.query.filter_by(icao=view).first()
        if query:
            notams = Notams.query.filter_by(icao=view).all()
            view_is = "limited"
            image = Notams.query.filter_by(icao=view).first().image
            airport_name = Notams.query.filter_by(icao=view).first().airport_name
        else:
            abort(404)    

    return render_template("notams.html", name=name, check_admin=check_admin, is_logged_in=is_logged_in,
    policies=Administrative.query.all(), notams=notams, view_is=view_is, 
    image=image, airport_name=airport_name, notam_len=len(Notams.query.all()))