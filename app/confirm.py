from Config.config import *
from send_message import *
from booking import *
import ast
import datetime


@app.route('/api/v1/confirmWebView', methods=['GET'])
@connect_sql()
def confirmWebView(cursor):
    try:
        dateTomorow = (datetime.date.today() +
                       timedelta(days=1)).strftime("%Y-%m-%d")
        # sql = """ SELECT ticketroom.rid, room.rname, ticketroom.row, time.time, ticketroom.oneid, ticketroom.code,
        #           ticketroom.name, ticketroom.email, ticketroom.date, room.category FROM ticketroom
        #           JOIN time ON ticketroom.row = time.row
        #           JOIN room ON ticketroom.rid = room.rid
        #           WHERE date = '{}' ORDER BY ticketroom.name DESC
        #           GROUP BY ticketroom.name """.format(dateTomorow)
        sql = """ SELECT ticketroom.oneid, ticketroom.code, 
                  ticketroom.name, ticketroom.email, ticketroom.date FROM ticketroom 
                  JOIN time ON ticketroom.row = time.row 
                  JOIN room ON ticketroom.rid = room.rid 
                  WHERE date = '{}' GROUP BY ticketroom.name ORDER BY ticketroom.name DESC """.format(dateTomorow)
        cursor.execute(sql)
        columns = [column[0] for column in cursor.description]
        result_tomorow = toJson(cursor.fetchall(), columns)
        if result_tomorow:
            for res in result_tomorow:
                botid = 'Bab49cebfb29557219b1eb3e75196a705'
                authorization = 'Bearer Ae369d6e9d3af510b9ac0276ab5e5ac9150230f559c6a4362aa1cd9b558fadecbfe73644946b5460d86781f6fc1eacc73'
                #####################FRIEND CHECK########################################
                playload_friend = {
                    "bot_id": botid,
                    "key_search": res['oneid']
                }
                friend_check = requests.request("POST", url="https://chat-manage.one.th:8997/api/v1/searchfriend",
                                                headers={'Authorization': authorization}, json=playload_friend, timeout=(60 * 1)).json()
                if friend_check['status'] != 'fail':
                    playload_msg = {
                        "to": res['oneid'],
                        "bot_id": botid,
                        "type": "template",
                        "elements": [
                            {
                                "image": "https://c1.sfdcstatic.com/content/dam/blogs/ca/Blog%20Posts/shake-up-sales-meeting-og.jpg",
                                "title": "ยืนยันการใช้งานห้องประชุมและรถตู้",
                                "detail": "กรุณาคลิกที่ลิ้งเพื้อยืนยันการใช้งานห้องประชุมและรถตู้ในวันที่ {}".format(res['date']),
                                "choice": [
                                    {
                                        "label": "คลิก!",
                                        "type": "webview",
                                        "url": "https://one.th/register",
                                        "size": "full"
                                    }
                                ]
                            }
                        ]
                    }
                    respone = requests.request("POST", url="https://chat-public.one.th:8034/api/v1/push_message",
                                               headers={'Authorization': authorization}, json=playload_msg, timeout=(60 * 1)).json()
        return jsonify({"result": respone})
    except Exception as e:
        return jsonify({"status": "fail", "message": str(e)})


@app.route('/api/v1/getroombooking', methods=['POST'])
@connect_sql()
def getroombooking(cursor):
    try:
        oneid = request.json.get('oneid', None)
        code = request.json.get('code', None)
        date = (datetime.date.today() +
                timedelta(days=1)).strftime("%Y-%m-%d")
        if not oneid or not code:
            return jsonify({"status": "fail", "message": "Missing Parameter"})
        else:
            sql = """SELECT ticketroom.rid, room.rname, ticketroom.row, ticketroom.description,
                          time.time, ticketroom.oneid, ticketroom.code, ticketroom.name, ticketroom.status,
                          ticketroom.description, ticketroom.ps, ticketroom.date, ticketroom.name, ticketroom.email
                          FROM ticketroom
                          INNER JOIN time ON ticketroom.row = time.row
                          INNER JOIN room ON ticketroom.rid = room.rid
                          WHERE ticketroom.oneid = %s AND ticketroom.code = %s  AND room.category = 'room' AND date(date) = %s 
                          ORDER BY ticketroom.rid"""
            cursor.execute(sql, (oneid, code, date,))
            columns = [column[0] for column in cursor.description]
            result = toJson(cursor.fetchall(), columns)
            roomResult = []
            rooms = []
            times = []
            tmp_room_id = 0
            dateNow = datetime.date.today()
            for room in result:
                if room['rid'] == tmp_room_id and room['date'] >= dateNow and room['status'] != "ยืนยัน":
                    times.append({"row": room['row'], "time": room['time']})
                else:
                    if room['date'] >= dateNow and room['status'] != "ยืนยัน":
                        times = []
                        times.append(
                            {"row": room['row'], "time": room['time']})
                        format_date = room['date'].strftime("%Y-%m-%d")
                        roomResult.append(
                            {"rid": room['rid'], "oneid": room['oneid'], "rname": room['rname'], "description": room['description'], "name": room['name'], "email": room['email'], "date": format_date, "times": times})
                        tmp_room_id = room['rid']
            # print('result', roomResult)
            return jsonify({"result": roomResult})
    except Exception as e:
        current_app.logger.info(e)
        return jsonify(str(e)), 500


@app.route('/api/v1/confirmbooking', methods=['POST'])
@connect_sql()
def confirmbooking(cursor):
    try:
        data = request.json
        if not data:
            return jsonify({"status": "fail", "message": "Missing Json"})
        else:
            timeStamp = datetime.datetime.now().strftime("%X")
            for x in data:
                if x['status'] != 'ยกเลิก':
                    sql_update_stauts = """ UPDATE ticketroom SET status = %s WHERE rid = %s AND row = %s AND date = %s AND oneid = %s """
                    cursor.execute(sql_update_stauts, ("ยืนยัน", x['rid'], x['row'], x['date'], x['oneid']))
                    sql = """ INSERT INTO log_appoved (rid, row, time_stamp, date, oneid, name, status) VALUES (%s, %s, %s, %s, %s, %s, %s) """
                    cursor.execute(
                        sql, (x['rid'], x['row'], timeStamp, x['date'], x['oneid'], x['name'], x['status']))
                else:
                    sql_del = """ DELETE FROM ticketroom WHERE rid = %s AND row = %s AND date = %s AND oneid = %s """
                    cursor.execute(
                        sql_del, (x['rid'], x['row'], x['date'], x['oneid']))
                    sql_discard = """ INSERT INTO log_appoved (rid, row, time_stamp, date, oneid, name, status) VALUES (%s, %s, %s, %s, %s, %s, %s) """
                    cursor.execute(
                        sql_discard, (x['rid'], x['row'], timeStamp, x['date'], x['oneid'], x['name'], x['status']))
            return jsonify({"message": "success"})
    except Exception as e:
        print(str(e))
        return jsonify(str(e))
