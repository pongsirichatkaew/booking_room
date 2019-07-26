from Config.config import *
import ast
# import datetime
from datetime import date
from datetime import timedelta

@app.route('/checklogin', methods=['POST'])
@connect_sql()
def checklogin_one_id(cursor):
    try:
        data = request.json
        username = data['username']
        password = data['password']
        payload = {
            "grant_type": "password",
            "client_id": "37",
            "client_secret": "OiEdomw5Pr9T0dlipNWWlutB9rdsojH3ToE2MENb",
            "username": username,
            "password": password
        }

        response = requests.request(
            "POST", url="https://one.th/api/oauth/getpwd", json=payload, timeout=(60 * 1)).json()
        # print(response)
        if response['result'] == 'Fail':
            return jsonify({'status': 'Fail'})
        accessTokenOneID = response['token_type']+' '+response['access_token']
        informationUser = requests.get("https://one.th/api/account", headers={
                                       'Authorization': accessTokenOneID}, timeout=(60 * 1)).json()
        return jsonify(informationUser)
    except Exception as e:
        current_app.logger.info(e)
        return jsonify(str(e))

@app.route('/api/v1/send_message', methods=['GET'])
@connect_sql()
def send_message(cursor):
    try:
        today = date.today() + timedelta(days=1) 
        # today = date.today()
        nextDay = today.strftime("%Y-%m-%d")
        print(nextDay)
        bot_id = "B9f17b544628e5dfa8be224d00e759065"
        tokenBot = 'Bearer A62e8a53c57ec5330889b9f0f06e07e9cc5e82f556ae14b73acd9a53b758a5dddf8c22033ab5540788955425197bcac03'
        # sql = """
        # SELECT t.time,projector.pname,t.row,r.code,r.oneid,r.name,r.department,r.email,r.description,r.numberofpeople,r.ps,r.date FROM ticketprojector as r 
        # LEFT JOIN time as t ON r.row = t.row LEFT JOIN projector as projector ON r.pid = projector.pid WHERE Date(r.date) = %s GROUP BY r.name
        # """
        # cursor.execute(sql, nextDay)
        # columns = [column[0] for column in cursor.description]
        # result_printers = toJson(cursor.fetchall(), columns)
        result = []
        sql = """
        SELECT r.name,r.department,r.email,r.description,r.numberofpeople,r.ps,r.date FROM ticketroom as r WHERE Date(r.date) = %s GROUP BY r.name
        """
        cursor.execute(sql, nextDay)
        columns = [column[0] for column in cursor.description]
        result_rooms = toJson(cursor.fetchall(), columns)

        for result_room in result_rooms:
            sql = """
            SELECT room.rname,room.category,r.row,r.rid FROM ticketroom as r
             LEFT JOIN room as room ON r.rid = room.rid WHERE Date(r.date) = %s AND r.name = %s GROUP BY r.rid
            """
            cursor.execute(sql, (nextDay,result_room['name']))
            columns = [column[0] for column in cursor.description]
            rooms = toJson(cursor.fetchall(), columns)
            room = []
            for rname in rooms:
                sql = """
                SELECT t.time FROM ticketroom as r
                LEFT JOIN time as t ON r.row = t.row WHERE Date(r.date) = %s AND r.rid = %s ORDER BY r.row ASC LIMIT 1
                """
                cursor.execute(sql, (nextDay,rname['rid']))
                timesFirsts = cursor.fetchone()
                timesFirst = timesFirsts[0]
                txt1 = timesFirst
                x = txt1.split("-")
                timesFirst = x[0]

                sql = """
                SELECT t.time FROM ticketroom as r
                LEFT JOIN time as t ON r.row = t.row WHERE Date(r.date) = %s AND r.rid = %s ORDER BY r.row DESC LIMIT 1
                """
                cursor.execute(sql, (nextDay,rname['rid']))
                timesLasts = cursor.fetchone()
                timesLast = timesLasts[0]
                txt2 = timesLast
                y = txt2.split("-")
                if len(y) != 1:
                    timesLast = y[1]
                else:
                    timesLast = y[0]

                time = timesFirst + ' - ' + timesLast

                room.append({
                    'category': rname['category'],
                    'rname': rname['rname'],
                    'times': time
                })
            result_room['room'] = room


        # result_rooms = filter(lambda x: x.name == "Ms.Patinya  Buakaew", result_rooms)
        # rooms = []
        # output_dict = [x for x in result_rooms if x['name'] == 'Ms.Patinya  Buakaew']
        # for output_dicts in output_dict:
        #     data = {}
        #     a = next((x for x in rooms if x.get('rname') == output_dicts['rname']), None)
        #     if a is None:
        #         print('roomss')
        #         for room in rooms:
        #             times = []
        #             print('roomss')
        #             if output_dicts['rname'] != room.get('rname'):
        #                 for time in output_dict:
        #                     if time['rname'] == output_dicts['rname']:
        #                         times.append(time['time'])
        #                 data = {
        #                     'rname': output_dicts['rname'],
        #                     'times': times
        #                 }
        #                 break
        #         rooms.append(data)

        # print(output_dict)

        # sql = """
        # SELECT t.time,room.rname,t.row,r.code,r.oneid,r.name,r.department,r.email,r.description,r.numberofpeople,r.ps,r.date FROM ticketroom as r 
        # LEFT JOIN time as t ON r.row = t.row LEFT JOIN room as room ON r.rid = room.rid WHERE Date(r.date) = %s AND room.category LIKE 'vehicle'
        # """
        # cursor.execute(sql, nextDay)
        # columns = [column[0] for column in cursor.description]
        # result_vehicle = toJson(cursor.fetchall(), columns)

        # for result_room in result_rooms:
        #     send_msg = "พรุ่งนี้วันที่ {}  คุณ {} ได้ทำการจองห้อง {} ไว้".format(nextDay,result_room['name'], result_room['rname'])
            
        #     if result_room['email'] is not None:
        #         msg = Message('แจ้งเตือนการจองห้อง', sender = 'noreply.booking@inet.co.th', recipients = [result_room['email']])
        #         msg.body = send_msg
        #         mail.send(msg)

        #     if result_room['oneid'] is not None:
        #         payload = {
        #             "bot_id" : bot_id,
        #             "key_search" : result_room['oneid']
        #         }
        #         response = requests.request("POST", url="https://chat-manage.one.th:8997/api/v1/searchfriend",
        #         headers={'Authorization': tokenBot}, json=payload, timeout=(60 * 1)).json()
        #         if response['status'] != 'fail':
        #             payload_msg =  {
        #                     "to" : response['friend']['user_id'],
        #                     "bot_id" : bot_id,
        #                     "type" : "text",
        #                     "message" : send_msg
        #                 }
        #             response_msg = requests.request("POST", url="https://chat-public.one.th:8034/api/v1/push_message",
        #             headers={'Authorization': tokenBot}, json=payload_msg, timeout=(60 * 1)).json()

        return jsonify(result_rooms)
    except Exception as e:
        current_app.logger.info(e)
        return jsonify(str(e))