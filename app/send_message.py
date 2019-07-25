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
        nextDay = today.strftime("%Y-%m-%d")
        print(nextDay)
        sql = """
        SELECT t.time,projector.pname,t.row,r.code,r.oneid,r.name,r.department,r.email,r.description,r.numberofpeople,r.ps,r.date FROM ticketprojector as r 
        LEFT JOIN time as t ON r.row = t.row LEFT JOIN projector as projector ON r.pid = projector.pid WHERE Date(r.date) = %s GROUP BY r.name
        """
        cursor.execute(sql, nextDay)
        columns = [column[0] for column in cursor.description]
        result_printers = toJson(cursor.fetchall(), columns)

        sql = """
        SELECT t.time,room.rname,t.row,r.code,r.oneid,r.name,r.department,r.email,r.description,r.numberofpeople,r.ps,r.date FROM ticketroom as r 
        LEFT JOIN time as t ON r.row = t.row LEFT JOIN room as room ON r.rid = room.rid WHERE Date(r.date) = %s GROUP BY r.name
        """
        cursor.execute(sql, nextDay)
        columns = [column[0] for column in cursor.description]
        result_rooms = toJson(cursor.fetchall(), columns)

        for result_room in result_rooms:
            send_msg = "พรุ่งนี้วันที่ {}  คุณ {} ได้ทำการจองห้อง {} ไว้".format(nextDay,result_room['name'], result_room['rname'])
            if result_room['email'] is not None:
                msg = Message('แจ้งเตือนการจองห้อง', sender = 'noreply.booking@inet.co.th', recipients = [result_room['email']])
                msg.body = send_msg
                mail.send(msg)
            if result_room['oneid'] is not None:
                bot_id = "B9f17b544628e5dfa8be224d00e759065"
                payload = {
                    "bot_id" : bot_id,
                    "key_search" : result_room['oneid']
                }
                accessTokenOneID = 'Bearer A62e8a53c57ec5330889b9f0f06e07e9cc5e82f556ae14b73acd9a53b758a5dddf8c22033ab5540788955425197bcac03'
                response = requests.request("POST", url="https://chat-manage.one.th:8997/api/v1/searchfriend",
                headers={'Authorization': accessTokenOneID}, json=payload, timeout=(60 * 1)).json()
                if response['status'] != 'fail':
                    payload_msg =  {
                            "to" : response['friend']['user_id'],
                            "bot_id" : bot_id,
                            "type" : "text",
                            "message" : send_msg
                        }
                    response_msg = requests.request("POST", url="https://chat-public.one.th:8034/api/v1/push_message",
                    headers={'Authorization': accessTokenOneID}, json=payload_msg, timeout=(60 * 1)).json()
                # print('OK One ID')
        return jsonify(result_rooms)
    except Exception as e:
        current_app.logger.info(e)
        return jsonify(str(e))