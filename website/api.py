from flask import Blueprint, jsonify, request
from .models import Controllerroster, News, SystemLog, Users, db, Events, Stats, Onlineatc
from datetime import datetime
from flask_login import current_user

import asyncio, requests, aiohttp, json, bs4

api = Blueprint("api", __name__)

async def get_api_data(cs, url):
    async with cs.get(url) as response:
        if response.status == 200:
            data = await response.json()
            return data
        else:
            return None


@api.route('/api/update/stats')
async def apiupdatestats():
    api_key = request.headers.get("Authorization")

    if api_key == "$WnY%#MN@U_UAxtg":
        resident_list = []
        visitor_list = []
        active_hours_vacc = ""
        active_countrollers = 0
        actions = []
        api_urls = ["https://hq.vatwa.net/api/vacc/PAK/resident", "https://hq.vatwa.net/api/vacc/PAK/visitor", "https://stats.vatwa.net/api/vacc/?PAK", "https://stats.vatwa.net/api/vacc/resident/?PAK", "https://stats.vatwa.net/api/vacc/visitor/?PAK"]

        counter = 0

        async with aiohttp.ClientSession() as cs:
            for url in api_urls:
                actions.append(asyncio.ensure_future(get_api_data(cs, url)))

            api_data = await asyncio.gather(*actions)

            for data in api_data:
                if data != None:

                    if counter == 0:
                        for residents in data:
                            resident_list.append(residents)
                        counter = counter + 1

                    elif counter == 1:
                        for visitors in data:
                            visitor_list.append(visitors)
                        counter = counter + 1
                    
                    elif counter == 2:
                        active_hours_vacc = data['total']
                        counter += 1

                    elif counter == 3:
                        active_countrollers = int(data[0][0]['active_controllers'])
                        counter += 1

                    elif counter == 4:
                        active_countrollers = active_countrollers + int(data[0][0]['active_controllers'])
                        counter += 1


            if api_data != None:

                found_json = Stats.query.filter_by(value=1).first()
                found_json.json_data = len(resident_list)

                found_json = Stats.query.filter_by(value=2).first()
                found_json.json_data = len(visitor_list)

                found_json = Stats.query.filter_by(value=3).first()
                found_json.json_data = active_hours_vacc.split(':')[0]

                found_json = Stats.query.filter_by(value=4).first()
                found_json.json_data = active_countrollers

                db.session.commit()

                responses = {
                    'details' : 'completed'
                }
                return jsonify(responses)
            
            elif data == None:
                responses = {
                    'details' : 'VATWA HQ returned None'
                }
                return jsonify(responses), 400
                

    elif not api_key:
        Missing_Key = {
        'details' : 'Authentication credentials were not provided.',
        }
        return jsonify(Missing_Key), 401
    
    else:
        Invalid_Key = {
        'details' : 'Authentication credentials were incorrect.',
        }
        return jsonify(Invalid_Key), 401

@api.route('/api/update/events')
def apiupdateevents():
    api_key = request.headers.get("Authorization")

    if api_key == "$WnY%#MN@U_UAxtg":

        r = requests.get("https://hq.vatwa.net/api/events/future")
        if r.status_code == 200:
            events = r.json()
            for data in events:
                if "PAK" in data['vacc']:
                    query = Events.query.filter_by(value=data['id']).first()
                    replace_start = data['start'].replace('T', ' ')
                    replace_end = data['end'].replace('T', ' ')

                    if query:
                        query.start_time = replace_start
                        query.end_time = replace_end
                        query.event_banner = data['banner_link']
                        db.session.commit()

                    else:
                        insert_event = Events(value=data['id'], start_time=replace_start, end_time=replace_end,
                                                event_banner=data['banner_link'], event_link=f"https://hq.vatwa.net/event/{data['id']}")
                        db.session.add(insert_event)
                        db.session.commit()

        # delete old events from DB
        times = Events.query.all()
        if times:
            time_now = datetime.utcnow()

            for time in times:
                stored = time.end_time[:-8]
                stored_time = datetime.strptime(stored, '%Y-%m-%d %H:%M:%S')
                diff = stored_time - time_now
                actual_diff = (diff.total_seconds() / 60)
                if actual_diff <= 0:
                    get_time = time.end_time
                    Events.query.filter_by(end_time=get_time).delete()
                    db.session.commit()
                    
        
        if r.status_code != 200:
            responses = {
                'details' : f'VATWA HQ returned {r.status_code} status code',
            }
            return jsonify(responses), 400
        
        else:
            responses = {
            'details' : 'completed'
        }
        return jsonify(responses)


    elif not api_key:
        Missing_Key = {
        'details' : 'Authentication credentials were not provided.',
        }
        return jsonify(Missing_Key), 401
    
    else:
        Invalid_Key = {
        'details' : 'Authentication credentials were incorrect.',
        }
        return jsonify(Invalid_Key), 401


@api.route('/api/update/online-controllers')
def updateonlinecontrollers():
    api_key = request.headers.get("Authorization")

    if api_key == "$WnY%#MN@U_UAxtg":
        
        r = requests.get("https://data.vatsim.net/v3/vatsim-data.json")
        if r.status_code == 200:
            try:
                data = r.json()
            except:
                responses = {
                'details' : 'VATSIM API returned blank page.',
                }
                return jsonify(responses), 400
            else:
                #store callsigns and other stuff in this list.
                big_list = []

                #loop through the controllers list in the VATSIM API
                for controllers in data['controllers']:
                    callsign = controllers['callsign']
                    big_list.append(callsign)

                    #check if ASIA_W_FSS is online
                    if "ASIA_W_FSS" in callsign:
                        if controllers['frequency'] != "199.998":
                    
                            query = Onlineatc.query.filter_by(callsign="ASIA_W_FSS").first()
                            if query:
                                query.controller_name = controllers['name']
                                query.cid = controllers['cid']
                                db.session.commit()
                            else:
                                print(f"Added ASIA_W_FSS way callsign {callsign}{controllers['name']}")
                                add_facility = Onlineatc(cid=controllers['cid'], controller_name=controllers['name'], facility_name="West Asia Control", callsign=callsign)
                                db.session.add(add_facility)
                                db.session.commit()


                    #check if any vACC Position is online
                    if callsign.startswith("OP"):
                        if controllers['frequency'] != "199.998":
                            if callsign.endswith("OBS") == False:
                                query = Onlineatc.query.all()
                                query1 = Onlineatc.query.filter_by(id=1).first()
                                pos = []
                                for q in query:
                                    pos.append(q.callsign)

                                con = json.loads(query1.facility_db)
                                query = Onlineatc.query.filter_by(cid=int(controllers['cid'])).first()
                                if query:
                                    find_callsign = Onlineatc.query.filter_by(callsign=callsign).first()
                                    find_callsign.callsign = callsign
                                    find_callsign.controller_name = controllers['name']
                                    find_callsign.cid = int(controllers['cid'])
                                    try:
                                        facility = con[callsign]
                                    except KeyError:
                                        a=callsign.split('_')
                                        facility_new = f"{a[0]}_{a[2]}"
                                        try:
                                            facility = con[facility_new]
                                        except KeyError:
                                            facility = callsign
                                    find_callsign.facility_name = facility
                                    db.session.commit()

                                else:
                                    try:
                                        facility = con[callsign]
                                    except KeyError:
                                        a=callsign.split('_')
                                        facility_new = f"{a[0]}_{a[2]}"
                                        try:
                                            facility = con[facility_new]
                                        except KeyError:
                                            facility = callsign

                                    print(f"Added normal way callsign {callsign}{controllers['name']}")
                                    add_facility = Onlineatc(cid=int(controllers['cid']), controller_name=controllers['name'], facility_name=facility, callsign=callsign)
                                    db.session.add(add_facility)
                                    db.session.commit()
                                    

                #delete position if not online
                query = Onlineatc.query.all()
                for q in query:
                    if q.callsign not in big_list:
                        if str(q.id) != "1":
                            Onlineatc.query.filter_by(callsign=q.callsign).delete()
                            db.session.commit()

                responses = {
                        'details' : 'completed'
                }
                return jsonify(responses)
        
        else:
            responses = {
                'details' : 'VATSIM API did not return 200 status code',
            }
            return jsonify(responses), 400


    elif not api_key:
        Missing_Key = {
        'details' : 'Authentication credentials were not provided.',
        }
        return jsonify(Missing_Key), 401
    
    else:
        Invalid_Key = {
        'details' : 'Authentication credentials were incorrect.',
        }
        return jsonify(Invalid_Key), 401

@api.route('/api/update/controller-roster')
async def apicontrollerroster():
    api_key = request.headers.get("Authorization")

    if api_key == "$WnY%#MN@U_UAxtg":
        resident_list = []
        visitor_list = []
        solo_list = []
        actions = []
        api_urls = ["https://hq.vatwa.net/api/vacc/PAK/resident", "https://hq.vatwa.net/api/vacc/PAK/visitor", "https://hq.vatwa.net/api/solo/vacc/PAK"]
        
        counter = 0

        with db.session.no_autoflush:
            async with aiohttp.ClientSession() as cs:
                for url in api_urls:
                    actions.append(asyncio.ensure_future(get_api_data(cs, url)))
                
                api_data = await asyncio.gather(*actions)
                
                for data in api_data:
                    if data != "error_in_response":

                        if counter == 0:
                            for residents in data:
                                resident_list.append(residents)
                            counter = counter + 1
                        elif counter == 1:
                            for visitors in data:
                                visitor_list.append(visitors)
                            counter = counter + 1
                        elif counter == 2:
                            for solopeeps in data:
                                solo_list.append(solopeeps)
                            counter = counter + 1   
        
                    
                if data != "error_in_response":
                    
                    found_json = Controllerroster.query.filter_by(id=1).first()
                    found_json.data = resident_list

                    found_json = Controllerroster.query.filter_by(id=2).first()
                    found_json.data = visitor_list


                    found_json = Controllerroster.query.filter_by(id=3).first()
                    found_json.data = solo_list

                    db.session.commit()

                    responses = {
                        'details' : 'completed'
                    }
                    return jsonify(responses)
                
                elif data == None:
                    responses = {
                        'details' : 'VATWA HQ returned None'
                    }
                    return jsonify(responses), 400
    
    elif not api_key:
        Missing_Key = {
        'details' : 'Authentication credentials were not provided.',
        }
        return jsonify(Missing_Key), 401
    
    else:
        Invalid_Key = {
        'details' : 'Authentication credentials were incorrect.',
        }
        return jsonify(Invalid_Key), 401


@api.route('/api/update/news')
def apinews():
    api_key = request.headers.get("Authorization")

    if api_key == "$WnY%#MN@U_UAxtg":
        r = requests.get("https://hq.vatwa.net/api/news/vacc/PAK")
        
        
        if r.status_code == 200:
            listing = []
            
            for data in r.json():
                listing.append(data['subject'])
                query2 = News.query.filter_by(subject=data['subject']).first()
                if query2:
                    pass
                else:
                    soup2 = bs4.BeautifulSoup(data['subject'], "html.parser")
                    soup = bs4.BeautifulSoup(data['content'], "html.parser")
                    if len(soup.find_all('img')) != 0:
                        for b in soup.find_all('img'):
                            if b['src']:
                                banner_link = b['src']
                                break
                    
                    else:
                        banner_link = "https://s3-us-west-2.amazonaws.com/s.cdpn.io/169963/photo-1429043794791-eb8f26f44081.jpeg"
                    add_news = News(subject=soup2.text, content=soup.text, banner_link=banner_link, created_by=data['created_by'], time=datetime.utcnow().strftime("%d %B, %Y"))
                    db.session.add(add_news)
                    db.session.commit()

            query = News.query.all()
            for q in query:
                if q.id != 1:
                    if q.subject not in listing:
                        News.query.filter_by(subject=q.subject).delete()
                        db.session.commit()

            response = {'details' : 'completed'}
            return jsonify(response)

        else:
            responses = {
                'details' : f'VATWA HQ returned {r.status_code}'
            }
            return jsonify(responses), 400

    elif not api_key:
        Missing_Key = {
        'details' : 'Authentication credentials were not provided.',
        }
        return jsonify(Missing_Key), 401
    
    else:
        Invalid_Key = {
        'details' : 'Authentication credentials were incorrect.',
        }
        return jsonify(Invalid_Key), 401


@api.route('/api/update/controllers-top')
def apicontrollerstop():
    api_key = request.headers.get("Authorization")

    if api_key == "$WnY%#MN@U_UAxtg":
        r = requests.get("https://stats.vatwa.net/api/vacc/top5/?PAK")
        if r.status_code == 200:
            Center = []
            App = []
            Twr = []
            Gnd = []

            try:
                r.json()[1]['CTR'][0]['CTR']
            except KeyError:
                count = 1
                for data in r.json()[1]['CTR']:
                    query = Users.query.filter_by(id=int(data['id'])).first()
                    if query:
                        data['name'] = query.Full_Name
                        data['pos'] = count
                        count += 1
                    else:
                        new_user = Users(id=data['id'], First_Name=['name_first'], Last_Name=['name_last'], Full_Name=f"{r1.json()['name_first']} {r1.json()['name_last']}",
                        Email="None", RatingLong="None", RatingShort="None", PilotLong="None", PilotShort="None", DivisionID="None",
                        DivisionName="None", RegionID="NOne", RegionName="None", SubdivisionID="None", SubdivisionName="None", Use_CID="None")
                        db.session.add(new_user)
                        data['name'] = f"{r1.json()['name_first']} {r1.json()['name_last']}"
                        data['pos'] = count
                        count += 1
                    Center.append(data)
            else:
                pass
            
            try:
                r.json()[2]['APP'][0]['APP']
            except KeyError:
                count = 1
                for data in r.json()[2]['APP']:
                    query = Users.query.filter_by(id=int(data['id'])).first()
                    if query:
                        data['name'] = query.Full_Name
                        data['pos'] = count
                        count += 1
                    else:
                        new_user = Users(id=data['id'], First_Name=['name_first'},l_Name=['name_last'], Full_Name=f"{r1.json()['name_first']} {r1.json()['name_last']}",
                        Email="None", RatingLong="None", RatingShort="None", PilotLong="None", PilotShort="None", DivisionID="None",
                        DivisionName="None", RegionID="NOne", RegionName="None", SubdivisionID="None", SubdivisionName="None", Use_CID="None")
                        db.session.add(new_user)
                        data['name'] = f"{r1.json()['name_first']} {r1.json()['name_last']}"
                        data['pos'] = count
                        count += 1
                    App.append(data)
            else:
                pass

            try:
                r.json()[3]['TWR'][0]['TWR']

            except KeyError:
                count = 1
                for data in r.json()[3]['TWR']:
                    query = Users.query.filter_by(id=int(data['id'])).first()
                    if query:
                        data['name'] = query.Full_Name
                        data['pos'] = count
                        count += 1
                    else:
                        new_user = Users(id=data['id'], First_Name=['name_first'], Last_Name=['name_last'], Full_Name=f"{r1.json()['name_first']} {r1.json()['name_last']}",
                        Email="None", RatingLong="None", RatingShort="None", PilotLong="None", PilotShort="None", DivisionID="None",
                        DivisionName="None", RegionID="NOne", RegionName="None", SubdivisionID="None", SubdivisionName="None", Use_CID="None")
                        db.session.add(new_user)
                        data['name'] = f"{r1.json()['name_first']} {r1.json()['name_last']}"
                        data['pos'] = count
                        count += 1
                    Twr.append(data)
            else:
                pass

            try:
                r.json()[4]['GND'][0]['GND']
            except KeyError:
                count = 1 
                for data in r.json()[4]['GND']:
                    query = Users.query.filter_by(id=int(data['id'])).first()
                    if query:
                        data['name'] = query.Full_Name
                        data['pos'] = count
                        count += 1
                    else:
                        new_user = Users(id=data['id'], First_Name=['name_first'], Last_Name=['name_last'], Full_Name=f"{r1.json()['name_first']} {r1.json()['name_last']}",
                        Email="None", RatingLong="None", RatingShort="None", PilotLong="None", PilotShort="None", DivisionID="None",
                        DivisionName="None", RegionID="None", RegionName="None", SubdivisionID="None", SubdivisionName="None", Use_CID="None")
                        db.session.add(new_user)
                        data['name'] = f"{r1.json()['name_first']} {r1.json()['name_last']}"
                        data['pos'] = count
                        count += 1
                    Gnd.append(data)
            else:
                pass
            
            months = {"1" : "January", "2" : "February", "3" : "March", "4" : "April", "5" : "May", "6" : "June", 
            "7" : "July", "8" : "August", "9" : "September", "10" : "October", "11" : "November", "12" : "December"}
            Stats.query.filter_by(value=5).first().time_datetime = Center
            Stats.query.filter_by(value=5).first().time = months[r.json()[0][0]['month_year'].split('-')[0]]
            Stats.query.filter_by(value=6).first().time_datetime = App
            Stats.query.filter_by(value=7).first().time_datetime = Twr
            Stats.query.filter_by(value=8).first().time_datetime = Gnd
            db.session.commit()
            response = {'details' : 'completed'}
            return jsonify(response)

        else:
            responses = {
                'details' : f'VATWA HQ returned {r.status_code}'
            }
            return jsonify(responses), 400

    elif not api_key:
        Missing_Key = {
        'details' : 'Authentication credentials were not provided.',
        }
        return jsonify(Missing_Key), 401
    
    else:
        Invalid_Key = {
        'details' : 'Authentication credentials were incorrect.',
        }
        return jsonify(Invalid_Key), 401
