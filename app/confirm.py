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
                  WHERE date = '{}' AND ticketroom.code = "OC2261074" GROUP BY ticketroom.name ORDER BY ticketroom.name DESC """.format(dateTomorow)
        # sql = """ SELECT * FROM ticketroom
        #           WHERE date = '{}' AND code = "OC2261074" """.format(dateTomorow)
        cursor.execute(sql)
        columns = [column[0] for column in cursor.description]
        result_tomorow = toJson(cursor.fetchall(), columns)
        return jsonify(result_tomorow)
        # if result_tomorow:
        #     for res in result_tomorow:
        #         url = "https://chat-booking.inet.co.th/confirm/{}/{}/{}".format(res['code'], res['oneid'], res['date'])
        #         # url = "https://chat-booking-test.inet.co.th/confirm/{}/{}".format(res['code'], res['oneid'])
        #         botid = 'Bbc41524dcbc3515ebc3cfd36a1b4ac81'
        #         authorization = 'Bearer A62e8a53c57ec5330889b9f0f06e07e9cc5e82f556ae14b73acd9a53b758a5dddf8c22033ab5540788955425197bcac03'
        #                         #####################FRIEND CHECK########################################
        #         playload_friend = {
        #             "bot_id": botid,
        #             "key_search": res['oneid']
        #         }
        #         friend_check = requests.request("POST", url="https://chat-manage.one.th:8997/api/v1/searchfriend",
        #                                         headers={'Authorization': authorization}, json=playload_friend, timeout=(60 * 1)).json()
        #         if friend_check['status'] != 'fail':
        #             playload_msg = {
        #                 "to": res['oneid'],
        #                 "bot_id": botid,
        #                 "type": "template",
        #                 "elements": [
        #                     {
        #                         "image": "https://c1.sfdcstatic.com/content/dam/blogs/ca/Blog%20Posts/shake-up-sales-meeting-og.jpg",
        #                         "title": "ยืนยันการใช้งานห้องประชุมและรถตู้",
        #                         "detail": "กรุณาคลิกที่ลิงค์เพื่อยืนยันการใช้งานห้องประชุมและรถตู้ในวันที่ {}".format(res['date']),
        #                         "choice": [
        #                             {
        #                                 "label": "คลิก!",
        #                                 "type": "webview",
        #                                 "url": url,
        #                                 "size": "full"
        #                             }
        #                         ]
        #                     }
        #                 ]
        #             }
        #             respone = requests.request("POST", url="https://chat-public.one.th:8034/api/v1/push_message",
        #                                        headers={'Authorization': authorization}, json=playload_msg, timeout=(60 * 1)).json()
        # else:
        #     return jsonify({"message": "Not found"})
        # return jsonify({"result": respone})
    except Exception as e:
        return jsonify({"status": "fail", "message": str(e)})


@app.route('/api/v1/getroombooking', methods=['POST'])
@connect_sql()
def getroombooking(cursor):
    try:
        date = request.json.get('date', None)
        oneid = request.json.get('oneid', None)
        code = request.json.get('code', None)
        date_now = datetime.date.today().strftime("%Y-%m-%d")
        # date = (datetime.date.today() +
        #         timedelta(days=1)).strftime("%Y-%m-%d")
        if not oneid or not code or not date:
            return jsonify({"status": "fail", "message": "Missing Parameter"}), 400
        else:
            if date <= date_now:
                return jsonify({"status": "fail", "message": {"text":"Date: {} time out.".format(date), "date": date}}), 200
            else:
                sql = """SELECT ticketroom.rid, room.rname, ticketroom.row, ticketroom.description,
                            time.time, ticketroom.oneid, ticketroom.code, ticketroom.name, ticketroom.status,
                            ticketroom.description, ticketroom.ps, ticketroom.date, ticketroom.name, ticketroom.email
                            FROM ticketroom
                            INNER JOIN time ON ticketroom.row = time.row
                            INNER JOIN room ON ticketroom.rid = room.rid
                            WHERE ticketroom.oneid = %s AND ticketroom.code = %s  AND date(date) = %s
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
                return jsonify({"status": "success", "result": roomResult}), 200
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
            date_time = data[0]['date']
            # code = data[0]['code']
            rid = data[0]['rid']
            oneid = data[0]['oneid']
            name = data[0]['name']
            email = data[0]['email']
            status = data[0]['status']
            row = []
            for x in data:
                if x['status'] != 'ยกเลิก':
                    row.append(x['row'])
                    sql_update_stauts = """ UPDATE ticketroom SET status = %s WHERE rid = %s AND row = %s AND date = %s AND oneid = %s """
                    cursor.execute(sql_update_stauts, ("ยืนยัน", x['rid'], x['row'], x['date'], x['oneid']))
                    sql = """ INSERT INTO log_appoved (rid, row, time_stamp, date, oneid, name, status) VALUES (%s, %s, %s, %s, %s, %s, %s) """
                    cursor.execute(
                        sql, (x['rid'], x['row'], timeStamp, x['date'], x['oneid'], x['name'], x['status']))
                else:
                    row.append(x['row'])
                    sql_del = """ DELETE FROM ticketroom WHERE rid = %s AND row = %s AND date = %s AND oneid = %s """
                    cursor.execute(
                        sql_del, (x['rid'], x['row'], x['date'], x['oneid']))
                    sql_discard = """ INSERT INTO log_appoved (rid, row, time_stamp, date, oneid, name, status) VALUES (%s, %s, %s, %s, %s, %s, %s) """
                    cursor.execute(
                        sql_discard, (x['rid'], x['row'], timeStamp, x['date'], x['oneid'], x['name'], x['status']))
            confirm_room_email(row, date_time, name, rid, email, status)
            confirm_to_oneid(row,date_time,name,rid,oneid,status)
            return jsonify({"message": "success"})
    except Exception as e:
        print(str(e))
        return jsonify(str(e))

@app.route('/checkbot')
def cdheckbot():
    botid = 'Bab49cebfb29557219b1eb3e75196a705'
    authorization = 'Bearer Ae369d6e9d3af510b9ac0276ab5e5ac9150230f559c6a4362aa1cd9b558fadecbfe73644946b5460d86781f6fc1eacc73'
    respone = requests.request("POST", url="https://chat-manage.one.th:8997/api/v1/getlistroom",
                                               headers={'Authorization': authorization}, json={"bot_id": botid}, timeout=(60 * 1)).json()
    return jsonify({"result": respone})

@connect_sql()
def confirm_room_email(cursor,row,date,name,rid,email,status):
    dateThai = nextDayThai(date)
    name_split = name.split('.')
    strTime = timeMerge(row)

    room = None
    ## Select Room Name ##
    sql_select_room = """ SELECT rname, category FROM room WHERE rid = %s """
    cursor.execute(sql_select_room, (rid))
    columns = [column[0] for column in cursor.description]
    room = toJson(cursor.fetchall(), columns)
    headerTitle = ''
    messageTitle = ''
    if(room[0]['category'] == 'room'):
        headerTitle = 'ห้องประชุม'
        messageTitle = 'ห้อง:'
    else:
        headerTitle = 'รถตู้'
        messageTitle = ''

    send_msg_title = "วันที่ " + dateThai + " คุณ " + \
    name_split[1] + " ได้" + status + "การจอง" + \
    headerTitle + " ดังนี้ <br><br>"
    send_msg_email = ''
    timeSelec = 'เวลา: <br>'
    timeSelec += strTime
    send_msg_email += """ <ul style="list-style-type:none; padding: 0; margin: 0;"> """
    send_msg_email += """
    <li>{} {} </li>
    <li>{} </li>""".format(messageTitle, room[0]['rname'], timeSelec)
    send_msg_email += "</ul>"
    send_msg_email += "<br>"
    server = "mailtx.inet.co.th"
    # server = "smtp.gmail.com"
    send_from = 'noreply.booking@inet.co.th'
    send_to = email
    subject = 'แจ้งเตือน{}การใช้ห้องประชุมและรถตู้'.format(status)

    text = send_msg_title + send_msg_email

    msg = MIMEMultipart()
    msg['From'] = send_from
    msg['To'] = send_to
    msg['Date'] = formatdate(localtime=True)
    msg['Subject'] = subject
    msg.attach(MIMEText(text, "html", "utf-8"))
    send_type = 'email'
    dateTime = datetime.datetime.now()
    response = ''
    try:
        smtp = smtplib.SMTP(server)
        smtp.sendmail(send_from, send_to, msg.as_string())
        smtp.close()
        response = 'success'
    except Exception as e:
        print(str(e))
        current_app.logger.info(e)
        response = 'error'
        return str(e)
    return response

@connect_sql()
def confirm_to_oneid(cursor,row,date,name,rid,oneid,status):
    try:
        dateThai = nextDayThai(date)
        # bot_id = "B9f17b544628e5dfa8be224d00e759065"
        bot_id = "Bbc41524dcbc3515ebc3cfd36a1b4ac81"
        tokenBot = 'Bearer A62e8a53c57ec5330889b9f0f06e07e9cc5e82f556ae14b73acd9a53b758a5dddf8c22033ab5540788955425197bcac03'
        send_type = ''
        send_to_email = ''
        send_to_oneid = ''
        user_id = ''

        headerTitle = ''
        messageTitle = ''

        room = None
        ## Select Room Name #
        sql_select_room = """ SELECT rname, category FROM `room` WHERE rid = %s """
        cursor.execute(sql_select_room, (rid))
        columns = [column[0] for column in cursor.description]
        room = toJson(cursor.fetchall(), columns)

        if(room[0]['category'] == 'room'):
            headerTitle = 'ห้องประชุม'
            messageTitle = 'ห้อง:'
        else:
            headerTitle = 'รถตู้'
            messageTitle = ''

        strTime = timeMerge(row)

        name_split = name.split('.')
        # send_msg_oneChat_title = """คุณ {} ได้ยกเลิกการจอง{} ในวันที่ {}\n""".format(name_split[1], headerTitle, dateThai)

        # send_msg_oneChat = """\n{}{} \n เวลา:\n{} """.format(messageTitle, room[0]['rname'], strTime)
        send_msg_oneChat = """การจอง{} {} \nวัน: {} \nเวลา:\n{} \nได้ถูก{}เรียบร้อยแล้ว """.format(headerTitle, room[0]['rname'], dateThai, strTime, status)
        payload = {
                "bot_id": bot_id,
                "key_search": oneid
            }

        # GET user_id
        response = requests.request("POST", url="https://chat-manage.one.th:8997/api/v1/searchfriend",
                                                    headers={'Authorization': tokenBot}, json=payload, timeout=(60 * 1)).json()
        if response['status'] != 'fail':
            user_id = response['friend']['user_id']

        # Send One chat
        payload_msg =  {
                            "to" : user_id,
                            "bot_id" : bot_id,
                            "type" : "text",
                            "message" : send_msg_oneChat
                            # "message" : send_msg_oneChat_title + send_msg_oneChat
                        }
        send_type = 'one_id'
        dateTime = datetime.datetime.now()
        response_msg = requests.request("POST", url="https://chat-public.one.th:8034/api/v1/push_message",
        headers={'Authorization': tokenBot}, json=payload_msg, timeout=(60 * 1)).json()
        return response_msg
    except Exception as e:
        print('error ===', e)
        current_app.logger.info(e)
        return jsonify(str(e))
