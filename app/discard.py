from Config.config import *
from send_message import *
from booking import *
import ast
import datetime


@app.route('/api/v1/bookingroom/<code>/<oneid>', methods=['GET'])
@connect_sql()
def bookingroom(cursor, code, oneid):
    try:
        if not code and not oneid:
            return jsonify({"message": "Missing JSON in request"}), 400
        else:
            # code = request.json.get('code', None)
            # oneid = request.json.get('oneid', None)
            if not code or not oneid:
                return jsonify({"message": "Missing parameter"}), 400
            else:
                sql = """ SELECT ticketroom.rid, room.rname, ticketroom.row, 
                          time.time, ticketroom.oneid, ticketroom.code, ticketroom.name, 
                          ticketroom.description, ticketroom.ps, ticketroom.date 
                          FROM ticketroom
                          INNER JOIN time ON ticketroom.row = time.row
                          INNER JOIN room ON ticketroom.rid = room.rid
                          WHERE ticketroom.oneid = %s AND ticketroom.code = %s  AND room.category = 'room' 
                          GROUP BY date """
                cursor.execute(sql, (oneid, code))
                columns = [column[0] for column in cursor.description]
                resultBydate = toJson(cursor.fetchall(), columns)
                date_result = ""
                all_data = []
                times = []
                dateNow = datetime.date.today()
                for date in resultBydate:
                    if date['date'] >= dateNow:
                        sql2 = """ SELECT ticketroom.rid, room.rname, ticketroom.row, 
                            time.time, ticketroom.oneid, ticketroom.code, ticketroom.name, 
                            ticketroom.description, ticketroom.ps, ticketroom.date 
                            FROM ticketroom
                            INNER JOIN time ON ticketroom.row = time.row
                            INNER JOIN room ON ticketroom.rid = room.rid
                            WHERE ticketroom.oneid = %s AND ticketroom.code = %s  AND room.category = 'room' AND date(ticketroom.date) = %s """
                        cursor.execute(sql2, (oneid, code, date['date']))
                        columns = [column[0] for column in cursor.description]
                        result = toJson(cursor.fetchall(), columns)
                        date_result = {"date": result[0]['date']}
                        jsonResult = {"rid": result[0]["rid"], "rname": result[0]["rname"],
                                    "description": result[0]['description'], "ps": result[0]['ps']}
                        jsonResult.update(date_result)
                    # for time in result:
                    #     bookingtime = {"time": time['time'], "row": time['row']}
                    #     times.append(bookingtime)
                    #     jsonResult.update(times)
                        all_data.append(jsonResult)
                # jsonResult = {"rid": result[0]["rid"], "rname": result[0]["rname"], "description": result[0]['description'], "ps": result[0]['ps'], "date": result[0]['date'], "times": times}
                return jsonify({"message": all_data})
    except Exception as e:
        print('error ===', e)
        current_app.logger.info(e)
        return jsonify(str(e)), 500


@app.route('/api/v1/date_booking', methods=['POST'])
@connect_sql()
def date_booking(cursor):
    try:
        code = request.json.get('code', None)
        oneid = request.json.get('oneid', None)
        if not code and not oneid:
            return jsonify({"message": "Missing JSON in request"}), 400
        else:
            if not code or not oneid:
                return jsonify({"message": "Missing parameter"}), 400
            else:
                sql = """ SELECT ticketroom.oneid, ticketroom.code, ticketroom.date
                          FROM ticketroom
                          INNER JOIN time ON ticketroom.row = time.row
                          INNER JOIN room ON ticketroom.rid = room.rid
                          WHERE ticketroom.oneid = %s AND ticketroom.code = %s  AND room.category = 'room' 
                          GROUP BY date """
                cursor.execute(sql, (oneid, code))
                columns = [column[0] for column in cursor.description]
                resultBydate = toJson(cursor.fetchall(), columns)
                result_date = []
                dateNow = datetime.date.today()
                tmp_date = None
                for date in resultBydate:
                    if date['date'] >= dateNow:
                        tmp_date = date['date'].strftime("%Y-%m-%d")
                        result_date.append({"oneid": date['oneid'], "code":date['code'], "date":tmp_date})
                return jsonify({"message": result_date})
    except Exception as e:
        current_app.logger.info(e)
        return jsonify(str(e)), 500


@app.route('/api/v1/booking_discard', methods=['POST'])
@connect_sql()
def discard_booking(cursor):
    try:
        date = request.json.get('date', None)
        code = request.json.get('code', None)
        oneid = request.json.get('oneid', None)
        # print(date)
        # print(code)
        # print(oneid)
        if not code and not oneid:
            return jsonify({"message": "Missing JSON in request"}), 400
        else:
            if not code or not oneid :
                return jsonify({"message": "Missing parameter"}), 400
            elif not date:
                sql = """SELECT ticketroom.rid, room.rname, ticketroom.row, 
                          time.time, ticketroom.oneid, ticketroom.code, ticketroom.name, 
                          ticketroom.description, ticketroom.ps, ticketroom.date, ticketroom.name, ticketroom.email
                          FROM ticketroom
                          INNER JOIN time ON ticketroom.row = time.row
                          INNER JOIN room ON ticketroom.rid = room.rid
                          WHERE ticketroom.oneid = %s AND ticketroom.code = %s  AND room.category = 'room'
                          ORDER BY ticketroom.date,ticketroom.rid"""
                cursor.execute(sql, (oneid, code,))
                columns = [column[0] for column in cursor.description]
                result = toJson(cursor.fetchall(), columns)
                roomResult = []
                rooms = []
                times = []
                tmp_room_id = 0
                tmp_date = None
                dateNow = datetime.date.today()
                for room in result:
                    if room['rid'] == tmp_room_id and room['date'] == tmp_date and room['date'] >= dateNow:
                        times.append({"row": room['row'], "time":room['time']})
                    else:
                        if room['date'] >= dateNow:
                            times = []
                            times.append({"row": room['row'], "time":room['time']})
                            format_date = room['date'].strftime("%Y-%m-%d")
                            roomResult.append(
                                {"rid": room['rid'], "rname": room['rname'], "name": room['name'], "email": room['email'], "date": format_date, "times": times})
                            tmp_room_id = room['rid']
                            tmp_date = room['date']
                print('result', roomResult)
                return jsonify({"result": roomResult})
            else:
                sql = """SELECT ticketroom.rid, room.rname, ticketroom.row, 
                          time.time, ticketroom.oneid, ticketroom.code, ticketroom.name, 
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
                if room['rid'] == tmp_room_id and room['date'] >= dateNow:
                    times.append({"row": room['row'], "time":room['time']})
                else:
                    if room['date'] >= dateNow:
                        times = []
                        times.append({"row": room['row'], "time":room['time']})
                        format_date = room['date'].strftime("%Y-%m-%d")
                        roomResult.append(
                            {"rid": room['rid'], "rname": room['rname'], "name": room['name'], "email": room['email'], "date": format_date, "times": times})
                        tmp_room_id = room['rid']
            # print('result', roomResult)
            return jsonify({"result": roomResult})
    except Exception as e:
        print('error ===', e)
        current_app.logger.info(e)
        return jsonify(str(e)), 500

@app.route('/api/v1/booking_delete', methods=['POST'])
@connect_sql()
def booking_delete(cursor):
    try:
        if not request.is_json:
            return jsonify({"message":"Missing JSON Request"}), 400
        else:
            data = request.json
            date_time = data[0]['date']
            code = data[0]['code']
            rid = data[0]['rid']
            oneid = data[0]['oneid']
            name = data[0]['name']
            email = data[0]['email']
            # print(data)
            row = []
            for del_data in data:   
                row.append(del_data['row'])
                # print('row',row)
                sql = """ DELETE FROM ticketroom WHERE code = %s AND oneid = %s AND rid = %s AND row = %s AND date = %s """
                cursor.execute(sql, (del_data['code'], del_data['oneid'], del_data['rid'], del_data['row'], del_data['date']))
            sql = "SELECT COUNT(trid) AS trid_num FROM `ticketroom` WHERE `date` LIKE %s AND code = %s";
            cursor.execute(sql, (date_time, code))
            columns = [column[0] for column in cursor.description]
            result = toJson(cursor.fetchall(), columns)
            # print('row', row)
            # fullname = name.split('.')
            discard_room_email(row, date_time, name, rid, email)
            discard_to_oneid(row, date_time, name, rid, oneid)
            return jsonify({"message": "success", "data": { "result": result[0]['trid_num']}}), 200
    except Exception as e:
        print('error ===', e)
        current_app.logger.info(e)
        return jsonify(str(e)), 500

##################################VAN##################################################vehicle
@app.route('/api/v1/date_booking_vehicle', methods=['POST'])
@connect_sql()
def date_booking_vehicle(cursor):
    try:
        code = request.json.get('code', None)
        oneid = request.json.get('oneid', None)
        if not code and not oneid:
            return jsonify({"message": "Missing JSON in request"}), 400
        else:
            if not code or not oneid:
                return jsonify({"message": "Missing parameter"}), 400
            else:
                sql = """ SELECT ticketroom.oneid, ticketroom.code, ticketroom.date 
                          FROM ticketroom
                          INNER JOIN time ON ticketroom.row = time.row
                          INNER JOIN room ON ticketroom.rid = room.rid
                          WHERE ticketroom.oneid = %s AND ticketroom.code = %s  AND room.category = 'vehicle' 
                          GROUP BY date """
                cursor.execute(sql, (oneid, code))
                columns = [column[0] for column in cursor.description]
                resultBydate = toJson(cursor.fetchall(), columns)
                result_date = []
                tmp_date = None
                dateNow = datetime.date.today()
                for date in resultBydate:
                    if date['date'] >= dateNow:
                        tmp_date = date['date'].strftime("%Y-%m-%d")
                        result_date.append({"oneid": date['oneid'], "code":date['code'], "date":tmp_date})
                return jsonify({"message": result_date})
    except Exception as e:
        current_app.logger.info(e)
        return jsonify(str(e)), 500


@app.route('/api/v1/booking_discard_vehicle', methods=['POST'])
@connect_sql()
def discard_booking_vehicle(cursor):
    try:
        date = request.json.get('date', None)
        code = request.json.get('code', None)
        oneid = request.json.get('oneid', None)
        # print(date)
        # print(code)
        # print(oneid)
        if not code and not oneid:
            return jsonify({"message": "Missing JSON in request"}), 400
        else:
            if not code or not oneid :
                return jsonify({"message": "Missing parameter"}), 400
            elif not date:
                sql = """SELECT ticketroom.rid, room.rname, ticketroom.row, 
                          time.time, ticketroom.oneid, ticketroom.code, ticketroom.name, ticketroom.email,
                          ticketroom.description, ticketroom.ps, ticketroom.date
                          FROM ticketroom
                          INNER JOIN time ON ticketroom.row = time.row
                          INNER JOIN room ON ticketroom.rid = room.rid
                          WHERE ticketroom.oneid = %s AND ticketroom.code = %s  AND room.category = 'vehicle'
                          ORDER BY ticketroom.date,ticketroom.rid"""
                cursor.execute(sql, (oneid, code,))
                columns = [column[0] for column in cursor.description]
                result = toJson(cursor.fetchall(), columns)
                roomResult = []
                rooms = []
                times = []
                tmp_room_id = 0
                tmp_date = None
                dateNow = datetime.date.today()
                for room in result:
                    if room['rid'] == tmp_room_id and room['date'] == tmp_date and room['date'] >= dateNow:
                        times.append({"row": room['row'], "time":room['time']})
                    else:
                        if room['date'] >= dateNow:
                            times = []
                            times.append({"row": room['row'], "time":room['time']})
                            format_date = room['date'].strftime("%Y-%m-%d")
                            roomResult.append(
                                {"rid": room['rid'], "rname": room['rname'], "name": room['name'], "email": room['email'], "date": format_date, "times": times})
                            tmp_room_id = room['rid']
                            tmp_date = room['date']
                # print('result', roomResult)
                return jsonify({"result": roomResult})
            else:
                sql = """SELECT ticketroom.rid, room.rname, ticketroom.row, 
                          time.time, ticketroom.oneid, ticketroom.code, ticketroom.name, ticketroom.email,
                          ticketroom.description, ticketroom.ps, ticketroom.date
                          FROM ticketroom
                          INNER JOIN time ON ticketroom.row = time.row
                          INNER JOIN room ON ticketroom.rid = room.rid
                          WHERE ticketroom.oneid = %s AND ticketroom.code = %s  AND room.category = 'vehicle' AND date(date) = %s 
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
                if room['rid'] == tmp_room_id and room['date'] >= dateNow:
                    times.append({"row": room['row'], "time":room['time']})
                else:
                    if room['date'] >= dateNow:
                        times = []
                        times.append({"row": room['row'], "time":room['time']})
                        format_date = room['date'].strftime("%Y-%m-%d")
                        roomResult.append(
                            {"rid": room['rid'], "rname": room['rname'], "name": room['name'], "email": ['email'], "date": format_date, "times": times})
                        tmp_room_id = room['rid']
            # print('result', roomResult)
            return jsonify({"result": roomResult})
    except Exception as e:
        print('error ===', e)
        current_app.logger.info(e)
        return jsonify(str(e)), 500

@app.route('/api/v1/booking_delete_vehicle', methods=['POST'])
@connect_sql()
def booking_delete_vehicle(cursor):
    try:
        if not request.is_json:
            return jsonify({"message":"Missing JSON Request"}), 400
        else:
            data = request.json
            date_time = data[0]['date']
            code = data[0]['code']
            rid = data[0]['rid']
            oneid = data[0]['oneid']
            name = data[0]['name']
            email = data[0]['email']
            row = []
            for del_data in data:
                row.append(del_data['row'])
                sql = """ DELETE FROM ticketroom WHERE code = %s AND oneid = %s AND rid = %s AND row = %s AND date = %s """
                cursor.execute(sql, (del_data['code'], del_data['oneid'], del_data['rid'], del_data['row'], del_data['date']))
            sql = "SELECT COUNT(trid) AS trid_num FROM `ticketroom` WHERE `date` LIKE %s AND code = %s";
            cursor.execute(sql, (date_time, code))
            columns = [column[0] for column in cursor.description]
            result = toJson(cursor.fetchall(), columns)
            # print('row', row)
            # fullname = name.split('.')
            discard_room_email(row, date_time, name, rid, email)
            discard_to_oneid(row, date_time, name, rid, oneid)
            return jsonify({"message": "success", "data": { "result": result[0]['trid_num']}}), 200
    except Exception as e:
        print('error ===', e)
        current_app.logger.info(e)
        return jsonify(str(e)), 500

@connect_sql()
def discard_room_email(cursor,row,date,name,rid,email):
    dateThai = nextDayThai(date)
    name_split = name.split('.')
    strTime = timeMerge(row)

    room = None
    ## Select Room Name ##
    sql_select_room = """ SELECT rname,category FROM room WHERE rid = %s """
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
    name_split[1] + " ได้ทำการยกเลิกการจอง" + \
    headerTitle + " ดังนี้ <br><br>"
    send_msg_email = ''
    timeSelec = 'เวลา: <br>'
    
    # timeSelec += '<ul style="padding-left: 15px;">'
    # for index in range(len(itemticket['mergedTime'])):
    #     timeSelec += '<li>' + \
    #     str(itemticket['mergedTime'][index]) + '</li>'
    # timeSelec += '</ul>'
    timeSelec += strTime
    send_msg_email += """ <ul style="list-style-type:none; padding: 0; margin: 0;"> """
    send_msg_email += """
    <li>{} {} </li>
    <li>{} </li>""".format(messageTitle, room[0]['rname'], timeSelec)
    # print(send_msg_email)

    send_msg_email += "</ul>"
    send_msg_email += "<br>"

    server = "mailtx.inet.co.th"
    # server = "smtp.gmail.com"
    send_from = 'noreply.booking@inet.co.th'
    send_to = email
    subject = 'แจ้งเตือนการจองยกเลิกห้องประชุมและรถตู้'

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

        # smtp = smtplib.SMTP(server,587)

        ####
        # smtp.ehlo()
        # smtp.starttls()
        # smtp.login('pongsirichatkaew@gmail.com', 'bank2538')
        ###

        smtp.sendmail(send_from, send_to, msg.as_string())
        smtp.close()
        response = 'success'
        # cursor.execute(
        #     sql, (send_to_email, send_to_oneid, send_type, response, dateTime))
    except Exception as e:
        current_app.logger.info(e)
        response = 'error'
        return str(e)
        # cursor.execute(
        #     sql, (send_to_email, send_to_oneid, send_type, response, dateTime))
    return response

@connect_sql()
def discard_to_oneid(cursor,row,date,name,rid,oneid):
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
        # print(room)

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
        send_msg_oneChat = """การจอง{} {} \nวัน: {} \nเวลา:\n\t{} \nได้ถูกยกเลิกเรียบร้อยแล้ว """.format(headerTitle, room[0]['rname'], dateThai, strTime)
        # print(send_msg_oneChat)

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