from Config.config import *
from send_message import *
import ast
import datetime


# -----------------------login---------------------------------#
@app.route('/api/v1/login', methods=['POST'])
@connect_sql()
def login(cursor):
    try:
        if not request.is_json:
            return jsonify({"message": "Missing JSON in request"}), 400
        else:
            staff_id = request.json.get('staff_id', None)
            oneid = request.json.get('oneid', None)
            if not staff_id or not oneid:
                return jsonify({"message": "Missing parameter"}), 400
            else:
                response = requests.get(
                    'https://chat-develop.one.th:8007/checkStaff/'+staff_id+'/'+oneid)
                if response:
                    raw = response.text
                    raw = json.loads(raw)
                    # print(raw)
                    return jsonify({"message": raw})
                else:
                    return jsonify({"message": "error"}), 401
    except Exception as e:
        current_app.logger.info(e)
        return jsonify(str(e))

# ------------------------ All Ticket Room -------------------#
@app.route('/api/v1/rooms', methods=['GET'])
@connect_sql()
def get_all_rooms(cursor):
    try:
        sql = """SELECT rid,rname as name,rnumber FROM room where rstatus = 'show' and category = 'room'"""
        cursor.execute(sql,)
        columns = [column[0] for column in cursor.description]
        result = toJson(cursor.fetchall(), columns)
        return jsonify({"message": result})
    except Exception as e:
        print('error ===', e)
        current_app.logger.info(e)
        return jsonify(str(e)), 500


@app.route('/api/v1/vehicles', methods=['GET'])
@connect_sql()
def get_all_vehicles(cursor):
    try:
        sql = """SELECT rid,rname as name,rnumber FROM room where rstatus = 'show' and category = 'vehicle' """
        cursor.execute(sql,)
        columns = [column[0] for column in cursor.description]
        result = toJson(cursor.fetchall(), columns)
        return jsonify({"message": result})
    except Exception as e:
        print('error ===', e)
        current_app.logger.info(e)
        return jsonify(str(e)), 500


@app.route('/api/v1/projectors', methods=['GET'])
@connect_sql()
def get_all_projectors(cursor):
    try:
        sql = """ SELECT pid,pname as name FROM projector WHERE pstatus = 'show'  """
        cursor.execute(sql,)
        columns = [column[0] for column in cursor.description]
        result = toJson(cursor.fetchall(), columns)
        return jsonify({"message": result})
    except Exception as e:
        print('error ===', e)
        current_app.logger.info(e)
        return jsonify(str(e)), 500


# ------------------------ Room with time ---------------------#
@app.route('/api/v1/ticket_room', methods=['POST'])
@connect_sql()
def get_ticket_room(cursor):
    try:
        if not request.is_json:
            return jsonify({"message": "Missing JSON in request"}), 400
        else:
            date = request.json.get('date', None)
            room_id = request.json.get('rid', None)
            if not date:
                return jsonify({"message": "Missing parameter"}), 400
            elif not room_id and date:
                # print('date_all_room', date)
                sql = """SELECT t.time, room.rname, r.name , r.department , r.description , r.numberofpeople , r.ps ,r.date
                        FROM ticketroom as r
                        LEFT JOIN time as t
                        ON r.row = t.row
                        LEFT JOIN room as room
                        ON r.rid = room.rid
                        WHERE Date(r.date) = %s """
                cursor.execute(sql, (date,))
                columns = [column[0] for column in cursor.description]
                result = toJson(cursor.fetchall(), columns)
                return jsonify({"message": result})
            elif room_id and date:
                # print('date_some_room', date)
                # print('date_some_room', type(room_id))
                sql = """SELECT t.time, room.rname, r.name , r.department , r.description , r.numberofpeople , r.ps ,r.date
                        FROM ticketroom as r
                        LEFT JOIN time as t
                        ON r.row = t.row
                        LEFT JOIN room as room
                        ON r.rid = room.rid
                        WHERE Date(r.date) = %s AND r.rid = %s"""
                cursor.execute(sql, (date, room_id,))
                columns = [column[0] for column in cursor.description]
                result = toJson(cursor.fetchall(), columns)
                return jsonify({"message": result})
    except Exception as e:
        current_app.logger.info(e)
        return jsonify({"message": str(e)}), 500

# ------------------------ Room with time ---------------------#
@app.route('/api/v1/available_room', methods=['POST'])
@connect_sql()
def get_available_ticket_room(cursor):
    try:
        if not request.is_json:
            # print('if not json')
            return jsonify({"message": "Missing JSON in request"}), 400
        else:
            date = request.json.get('date', None)
            room_id = request.json.get('rid', None)
            if not room_id and date:
                room_sql = """SELECT rid,rname FROM room  WHERE category = 'room' AND rstatus='show' """
                cursor.execute(room_sql, )
                columns = [column[0] for column in cursor.description]
                allroom = toJson(cursor.fetchall(), columns)
                arr_room = []
                # print(allroom)
                for room in allroom:
                    sql = """SELECT t.time,room.rname,t.row
                            FROM ticketroom as r
                            LEFT JOIN time as t
                            ON r.row = t.row
                            LEFT JOIN room as room
                            ON r.rid = room.rid
                            WHERE Date(r.date) = %s AND r.rid = %s"""
                    cursor.execute(sql, (date, room["rid"],))
                    columns = [column[0] for column in cursor.description]
                    room_result = toJson(cursor.fetchall(), columns)

                    sql_select_room = """SELECT rnumber from room WHERE rid = %s"""
                    cursor.execute(sql_select_room, (room["rid"],))
                    columns = [column[0] for column in cursor.description]
                    room_number = toJson(cursor.fetchall(), columns)
                    # print(room_number)

                    jsonResult = {"name": room["rname"], "rid": room["rid"],
                                  "rnumber": room_number[0]['rnumber']}

                    sql_all_time = """SELECT time,row FROM `time`"""
                    cursor.execute(sql_all_time)
                    columns = [column[0] for column in cursor.description]
                    alltime = toJson(cursor.fetchall(), columns)

                    ## list Dict ##
                    arr_alltime = []
                    arr_selecttime = []
                    arr_time = []
                    for time in alltime:
                        arr_alltime.append(time['time'])
                    # print('alltime', arr_alltime)
                    for time in room_result:
                        arr_selecttime.append(time['time'])
                    # print('selectedtime', arr_selecttime)

                    my_time = set(arr_alltime) - set(arr_selecttime)
                    # print('listmytime', list(my_time))
                    list_time = []
                    for t in list(my_time):
                        for time in alltime:
                            if(t == time['time']):
                                list_time.append(
                                    {"row": time['row'], "time": time['time']})

                    list_time.sort(key=extract_time, reverse=False)
                    jsonResult.update({"times": list_time})
                    # print('jsonResult1', jsonResult)
                    arr_room.append(jsonResult)
                    # jsonResult.update({"times": list(my_time)})
                    # return jsonify({"result": jsonResult})
                return jsonify({"message": arr_room})
            elif room_id and date:
                sql_room_id = """SELECT rname,rnumber FROM `room` WHERE rid = %s and category = 'room' AND rstatus='show'"""
                cursor.execute(sql_room_id, (room_id,))
                columns = [column[0] for column in cursor.description]
                result_room_id = toJson(cursor.fetchall(), columns)
                if result_room_id:
                    room_name = result_room_id[0]['rname']
                    room_number = result_room_id[0]['rnumber']
                    sql = """SELECT t.time,room.rname,t.row
                            FROM ticketroom as r
                            LEFT JOIN time as t
                            ON r.row = t.row
                            LEFT JOIN room as room
                            ON r.rid = room.rid
                            WHERE Date(r.date) = %s AND r.rid = %s"""
                    cursor.execute(sql, (date, room_id,))
                    columns = [column[0] for column in cursor.description]
                    result = toJson(cursor.fetchall(), columns)

                    jsonResult = {"name": room_name,
                                  "rid": room_id, "rnumber": room_number}
                    sql_all_time = """SELECT time,row FROM `time`"""
                    cursor.execute(sql_all_time)
                    columns = [column[0] for column in cursor.description]
                    alltime = toJson(cursor.fetchall(), columns)

                    ## list Dict ##
                    arr_alltime = []
                    arr_selecttime = []
                    arr_time = []
                    for time in alltime:
                        arr_alltime.append(time['time'])
                    # print('alltime', arr_alltime)
                    for time in result:
                        arr_selecttime.append(time['time'])
                    # print('selectedtime', arr_selecttime)

                    my_time = set(arr_alltime) - set(arr_selecttime)

                    list_time = []
                    for t in list(my_time):
                        for time in alltime:
                            if(t == time['time']):
                                list_time.append(
                                    {"row": time['row'], "time": time['time']})

                    list_time.sort(key=extract_time, reverse=False)

                    # print('list_time', list_time)
                    # jsonResult["times"] = list_time
                    # print('json', jsonResult)
                    jsonResult.update({"times": list_time})
                    # jsonResult.update({"times": list(my_time)})
                    return jsonify({"message": jsonResult})
                else:
                    return jsonify({"message": "room_id is invalid"}), 400
    except Exception as e:
        current_app.logger.info(e)
        return jsonify({"message": str(e)}), 500


def extract_time(json):
    try:
        # Also convert to int since update_time will be string.  When comparing
        # strings, "10" is smaller than "2".
        return int(json['row'])
    except KeyError:
        return 0

# ------------------------ Vehicle with time ---------------------#
@app.route('/api/v1/available_vehicle', methods=['POST'])
@connect_sql()
def get_available_vehicle_room(cursor):
    try:
        if not request.is_json:
            return jsonify({"message": "Missing JSON in request"}), 400
        else:
            date = request.json.get('date', None)
            vehicle_id = request.json.get('rid', None)
            if not date:
                return jsonify({"message": "Missing parameter"}), 400
            elif not vehicle_id and date:
                room_sql = """SELECT rid,rname FROM room  WHERE category = 'vehicle' AND rstatus='show' """
                cursor.execute(room_sql, )
                columns = [column[0] for column in cursor.description]
                allvehicle = toJson(cursor.fetchall(), columns)
                arr_room = []
                for room in allvehicle:
                    sql = """SELECT t.time,room.rname,t.row
                            FROM ticketroom as r
                            LEFT JOIN time as t
                            ON r.row = t.row
                            LEFT JOIN room as room
                            ON r.rid = room.rid
                            WHERE Date(r.date) = %s AND r.rid = %s"""
                    cursor.execute(sql, (date, room["rid"],))
                    columns = [column[0] for column in cursor.description]
                    room_result = toJson(cursor.fetchall(), columns)

                    sql_select_room = """SELECT rnumber from room WHERE rid = %s"""
                    cursor.execute(sql_select_room, (room["rid"],))
                    columns = [column[0] for column in cursor.description]
                    room_number = toJson(cursor.fetchall(), columns)
                    # print(room_number)

                    jsonResult = {
                        "name": room["rname"], "rid": room["rid"], "rnumber": room_number[0]['rnumber']}
                    sql_all_time = """SELECT time,row FROM `time`"""
                    cursor.execute(sql_all_time)
                    columns = [column[0] for column in cursor.description]
                    alltime = toJson(cursor.fetchall(), columns)

                    ## list Dict ##
                    arr_alltime = []
                    arr_selecttime = []
                    arr_time = []
                    for time in alltime:
                        arr_alltime.append(time['time'])
                    # print('alltime', arr_alltime)
                    for time in room_result:
                        arr_selecttime.append(time['time'])
                    # print('selectedtime', arr_selecttime)

                    my_time = set(arr_alltime) - set(arr_selecttime)

                    list_time = []
                    for t in list(my_time):
                        for time in alltime:
                            if(t == time['time']):
                                list_time.append(
                                    {"row": time['row'], "time": time['time']})

                    list_time.sort(key=extract_time, reverse=False)
                    jsonResult.update({"times": list_time})
                    arr_room.append(jsonResult)

                    # jsonResult.update({"times": list(my_time)})
                    # return jsonify({"result": jsonResult})
                return jsonify({"message": arr_room})
            elif vehicle_id and date:
                sql_vehicle_id = """SELECT rname,rnumber FROM `room` WHERE rid = %s and category = 'vehicle' AND rstatus='show'"""
                cursor.execute(sql_vehicle_id, (vehicle_id,))
                columns = [column[0] for column in cursor.description]
                result_room_id = toJson(cursor.fetchall(), columns)
                if result_room_id:
                    room_name = result_room_id[0]['rname']
                    room_number = result_room_id[0]['rnumber']

                    sql = """SELECT t.time,room.rname,t.row
                            FROM ticketroom as r
                            LEFT JOIN time as t
                            ON r.row = t.row
                            LEFT JOIN room as room
                            ON r.rid = room.rid
                            WHERE Date(r.date) = %s AND r.rid = %s"""
                    cursor.execute(sql, (date, vehicle_id,))
                    columns = [column[0] for column in cursor.description]
                    result = toJson(cursor.fetchall(), columns)
                    jsonResult = {"name": room_name,
                                  "rid": vehicle_id, "rnumber": room_number}
                    sql_all_time = """SELECT time,row FROM `time`"""
                    cursor.execute(sql_all_time)
                    columns = [column[0] for column in cursor.description]
                    alltime = toJson(cursor.fetchall(), columns)

                    ## list Dict ##
                    arr_alltime = []
                    arr_selecttime = []
                    arr_time = []
                    for time in alltime:
                        arr_alltime.append(time['time'])
                    # print('alltime', arr_alltime)
                    for time in result:
                        arr_selecttime.append(time['time'])
                    # print('selectedtime', arr_selecttime)

                    my_time = set(arr_alltime) - set(arr_selecttime)

                    list_time = []
                    for t in list(my_time):
                        for time in alltime:
                            if(t == time['time']):
                                list_time.append(
                                    {"row": time['row'], "time": time['time']})

                    # print('list_time', list_time)
                    # jsonResult["times"] = list_time
                    # print('json', jsonResult)
                    list_time.sort(key=extract_time, reverse=False)
                    jsonResult.update({"times": list_time})
                    # print('mytime', my_time)
                    # print('mytimelist', list(my_time))
                    # print('listtime', list_time)
                    # jsonResult.update({"times": list(my_time)})
                    return jsonify({"message": jsonResult})
                else:
                    return jsonify({"message": "room_id is invalid"}), 400
    except Exception as e:
        current_app.logger.info(e)
        return jsonify({"message": str(e)}), 500


# ------------------------ Projector with time ---------------------#
@app.route('/api/v1/available_projector', methods=['POST'])
@connect_sql()
def get_available_projector(cursor):
    try:
        if not request.is_json:
            return jsonify({"message": "Missing JSON in request"}), 400
        else:
            date = request.json.get('date', None)
            projector_id = request.json.get('pid', None)
            if not date:
                return jsonify({"message": "Missing parameter"}), 400
            elif not projector_id and date:
                projector_sql = """ SELECT pid,pname FROM projector WHERE pstatus='show' """
                cursor.execute(projector_sql, )
                columns = [column[0] for column in cursor.description]
                allprojector = toJson(cursor.fetchall(), columns)
                arr_room = []
                for projector in allprojector:
                    sql = """SELECT t.time,projector.pname,t.row
                            FROM ticketprojector as r
                            LEFT JOIN time as t
                            ON r.row = t.row
                            LEFT JOIN projector as projector
                            ON r.pid = projector.pid
                            WHERE Date(r.date) = %s AND r.pid = %s"""
                    cursor.execute(sql, (date, projector["pid"],))
                    columns = [column[0] for column in cursor.description]
                    room_result = toJson(cursor.fetchall(), columns)
                    jsonResult = {
                        "name": projector["pname"], "pid": projector["pid"]}
                    sql_all_time = """SELECT time,row FROM `time`"""
                    cursor.execute(sql_all_time)
                    columns = [column[0] for column in cursor.description]
                    alltime = toJson(cursor.fetchall(), columns)

                    ## list Dict ##
                    arr_alltime = []
                    arr_selecttime = []
                    arr_time = []
                    for time in alltime:
                        arr_alltime.append(time['time'])
                    # print('alltime', arr_alltime)
                    for time in room_result:
                        arr_selecttime.append(time['time'])
                    # print('selectedtime', arr_selecttime)

                    my_time = set(arr_alltime) - set(arr_selecttime)

                    list_time = []
                    for mytime in my_time:
                        if mytime == "08.01-09.00":
                            list_time.append({"row": "1", "time": mytime})
                        elif mytime == "09.01-10.00":
                            list_time.append({"row": "2", "time": mytime})
                        elif mytime == "10.01-11.00":
                            list_time.append({"row": "3", "time": mytime})
                        elif mytime == "11.01-12.00":
                            list_time.append({"row": "4", "time": mytime})
                        elif mytime == "12.01-13.00":
                            list_time.append({"row": "5", "time": mytime})
                        elif mytime == "13.01-14.00":
                            list_time.append({"row": "6", "time": mytime})
                        elif mytime == "14.01-15.00":
                            list_time.append({"row": "7", "time": mytime})
                        elif mytime == "15.01-16.00":
                            list_time.append({"row": "8", "time": mytime})
                        elif mytime == "16.01-17.00":
                            list_time.append({"row": "9", "time": mytime})
                        elif mytime == "17.01-18.00":
                            list_time.append({"row": "10", "time": mytime})
                        elif mytime == "18.01-19.00":
                            list_time.append({"row": "11", "time": mytime})
                        elif mytime == "> 19.01":
                            list_time.append({"row": "12", "time": mytime})

                    list_time.sort(key=extract_time, reverse=False)
                    jsonResult.update({"times": list_time})
                    arr_room.append(jsonResult)
                    # jsonResult.update({"times": list(my_time)})
                    # return jsonify({"result": jsonResult})
                return jsonify({"message": arr_room})
            elif projector_id and date:
                sql_projector_id = """SELECT pname FROM projector WHERE pid = %s AND pstatus='show'"""
                cursor.execute(sql_projector_id, (projector_id,))
                columns = [column[0] for column in cursor.description]
                result_projector_id = toJson(cursor.fetchall(), columns)
                if result_projector_id:
                    room_name = result_projector_id[0]['pname']
                    sql = """SELECT t.time,projector.pname,t.row
                            FROM ticketprojector as r
                            LEFT JOIN time as t
                            ON r.row = t.row
                            LEFT JOIN projector as projector
                            ON r.pid = projector.pid
                            WHERE Date(r.date) = %s AND r.pid = %s"""
                    cursor.execute(sql, (date, projector_id,))
                    columns = [column[0] for column in cursor.description]
                    result = toJson(cursor.fetchall(), columns)
                    jsonResult = {"name": room_name, "pid": projector_id}
                    sql_all_time = """SELECT time,row FROM `time`"""
                    cursor.execute(sql_all_time)
                    columns = [column[0] for column in cursor.description]
                    alltime = toJson(cursor.fetchall(), columns)

                    ## list Dict ##
                    arr_alltime = []
                    arr_selecttime = []
                    arr_time = []
                    for time in alltime:
                        arr_alltime.append(time['time'])
                    # print('alltime', arr_alltime)
                    for time in result:
                        arr_selecttime.append(time['time'])
                    # print('selectedtime', arr_selecttime)

                    my_time = set(arr_alltime) - set(arr_selecttime)

                    list_time = []
                    for mytime in my_time:
                        if mytime == "08.01-09.00":
                            list_time.append({"row": "1", "time": mytime})
                        elif mytime == "09.01-10.00":
                            list_time.append({"row": "2", "time": mytime})
                        elif mytime == "10.01-11.00":
                            list_time.append({"row": "3", "time": mytime})
                        elif mytime == "11.01-12.00":
                            list_time.append({"row": "4", "time": mytime})
                        elif mytime == "12.01-13.00":
                            list_time.append({"row": "5", "time": mytime})
                        elif mytime == "13.01-14.00":
                            list_time.append({"row": "6", "time": mytime})
                        elif mytime == "14.01-15.00":
                            list_time.append({"row": "7", "time": mytime})
                        elif mytime == "15.01-16.00":
                            list_time.append({"row": "8", "time": mytime})
                        elif mytime == "16.01-17.00":
                            list_time.append({"row": "9", "time": mytime})
                        elif mytime == "17.01-18.00":
                            list_time.append({"row": "10", "time": mytime})
                        elif mytime == "18.01-19.00":
                            list_time.append({"row": "11", "time": mytime})
                        elif mytime == "> 19.01":
                            list_time.append({"row": "12", "time": mytime})

                    # print('list_time', list_time)
                    # jsonResult["times"] = list_time
                    # print('json', jsonResult)
                    list_time.sort(key=extract_time, reverse=False)
                    jsonResult.update({"times": list_time})
                    # jsonResult.update({"times": list(my_time)})
                    return jsonify({"message": jsonResult})
                else:
                    return jsonify({"message": "pid is invalid"}), 400
    except Exception as e:
        current_app.logger.info(e)
        return jsonify({"message": str(e)}), 500


@app.route('/api/v1/insert_room', methods=['POST'])
@connect_sql()
def post_available_room(cursor):
    try:
        if not request.is_json:
            return jsonify({"message": "Missing JSON in request"}), 400
        else:
            col = request.json.get('col', None)
            code = request.json.get('code', None)
            date = request.json.get('date', None)
            department = request.json.get('department', None)
            description = request.json.get('description', None)
            email = request.json.get('email', None)
            name = request.json.get('name', None)
            numberofpeople = request.json.get('numberofpeople', None)
            oneid = request.json.get('oneid', None)
            ps = request.json.get('ps', None)
            rid = request.json.get('rid', None)
            row = request.json.get('row', None)
            if not col or not code or not date or not department or not description or not email or not name or not numberofpeople or not oneid or not rid or not row:
                return jsonify({"message": "Missing parameter"}), 400

            response = requests.get(
                'https://chat-develop.one.th:8007/checkStaff/'+code+'/'+oneid)
            if response:
                raw = response.text
                raw = json.loads(raw)
                if raw['status'] == "fail":
                    # print(raw['status'])
                    return jsonify({"message": raw}), 401
                else:
                    sql_insert = []
                    for r in row:
                        sql_search_row = """ SELECT room.rname,t.time
                                            FROM ticketroom as r
                                            LEFT JOIN time as t
                                            ON r.row = t.row
                                            LEFT JOIN room as room
                                            ON r.rid = room.rid
                                            WHERE r.rid=%s AND r.row=%s AND Date(r.date) = %s """
                        cursor.execute(sql_search_row, (rid, r, date,))
                        columns = [column[0] for column in cursor.description]
                        search_row = toJson(cursor.fetchall(), columns)

                        if(search_row):
                            return jsonify({"message": "{} in {} is already Exists".format(search_row[0]['rname'], search_row[0]['time'])}), 400
                        else:
                            sql_insert.append("INSERT INTO `ticketroom`(`rid`, `row`, `col`, `oneid`, `code`, `name`, `department`, `email`, `description`, `numberofpeople`, `ps`, `date`) VALUES ('{}','{}','{}','{}','{}','{}','{}','{}','{}','{}','{}','{}'); ".format(
                                rid, r, col, oneid, code, name, department, email, description, numberofpeople, ps, date))

                for sql in sql_insert:
                    # print(sql)
                    cursor.execute(sql)

                dateThai = nextDayThai(date)
                print('dateThai', dateThai)
                bot_id = "B9f17b544628e5dfa8be224d00e759065"
                tokenBot = 'Bearer A62e8a53c57ec5330889b9f0f06e07e9cc5e82f556ae14b73acd9a53b758a5dddf8c22033ab5540788955425197bcac03'
                send_type = ''
                send_to_email = ''
                send_to_oneid = ''
                user_id = ''

                sql_all_time = """ SELECT row,time from time """
                cursor.execute(sql_all_time)
                columns = [column[0] for column in cursor.description]
                times = toJson(cursor.fetchall(), columns)

                ## Merge time ##
                strTime = ''
                strTmp = ''
                strFirst = ''
                strSecond = ''
                row.sort()
                for index, time in enumerate(times):
                    for i, r in enumerate(row):
                        if(time['row'] == r):
                            strTmp = time['time'].split('-')
                            if(len(strTmp) > 1):
                                if(strTmp[1] == strSecond):
                                    pass
                                else:
                                    strFirst = strTmp[0]
                                    strSecond = strTmp[1]
                                if(i+1 < len(row)):
                                    if(times[index+1]['row'] == row[i+1]):
                                        if(len(times[index + 1]['time'].split('-')) > 1):
                                            strSecond = times[index +
                                                              1]['time'].split('-')[1]
                                    else:
                                        strTime = strTime + strFirst + "-" + strSecond + ",\n"
                            else:
                                if(times[index-1]['row'] == row[i-1]):
                                    pass
                                else:
                                    strFirst = ''
                                strSecond = strTmp[0]
                strTime = strTime + strFirst + "-" + strSecond
                print('strTime', strTime)

                name_split = name.split('.')                    
                send_msg_oneChat_title = """คุณ {} ได้จองห้องประชุม ในวันที่ {}\n""".format(name_split[1],dateThai)
                print(send_msg_oneChat_title)

                ## Select Room Name ##
                sql_select_room = """ SELECT rname FROM `room` WHERE rid = %s """
                cursor.execute(sql_select_room, (rid))
                columns = [column[0] for column in cursor.description]
                room = toJson(cursor.fetchall(), columns)
                send_msg_oneChat = """\n{}ห้อง: {} \nเหตุผล: {}\nจำนวนคน: {} \nหมายเหตุ: {} \n เวลา:\n{} \n\nหากต้องการยกเลิกหรือแก้ไข\nคลิ้กที่นี่ https://intranet.inet.co.th/index.php/MainController/bookingroom/""".format(
                    "", room[0]['rname'], description, numberofpeople, ps, strTime)
                print(send_msg_oneChat)

                payload = {
                    "bot_id" : bot_id,
                    "key_search" : oneid
                }

                ## GET user_id
                response = requests.request("POST", url="https://chat-manage.one.th:8997/api/v1/searchfriend",
                headers={'Authorization': tokenBot}, json=payload, timeout=(60 * 1)).json()
                if response['status'] != 'fail':
                    user_id = response['friend']['user_id']                

                ## Send One chat
                payload_msg =  {
                                "to" : user_id,
                                "bot_id" : bot_id,
                                "type" : "text",
                                "message" : send_msg_oneChat_title + send_msg_oneChat
                            }
                send_type = 'one_id'
                dateTime = datetime.datetime.now()
                response_msg = requests.request("POST", url="https://chat-public.one.th:8034/api/v1/push_message",
                headers={'Authorization': tokenBot}, json=payload_msg, timeout=(60 * 1)).json()


                return jsonify({"message": "Insert Success"})
            else:
                return jsonify({"message": "one id error"}), 500
    except Exception as e:
        print('error ===', e)
        current_app.logger.info(e)
        return jsonify(str(e))


@app.route('/api/v1/insert_vehicle', methods=['POST'])
@connect_sql()
def post_available_vehicle(cursor):
    try:
        if not request.is_json:
            return jsonify({"message": "Missing JSON in request"}), 400
        else:
            col = request.json.get('col', None)
            code = request.json.get('code', None)
            date = request.json.get('date', None)
            department = request.json.get('department', None)
            description = request.json.get('description', None)
            email = request.json.get('email', None)
            name = request.json.get('name', None)
            numberofpeople = request.json.get('numberofpeople', None)
            oneid = request.json.get('oneid', None)
            ps = request.json.get('ps', None)
            rid = request.json.get('rid', None)
            row = request.json.get('row', None)
            if not col or not code or not date or not department or not description or not email or not name or not numberofpeople or not oneid or not rid or not row:
                return jsonify({"message": "Missing parameter"}), 400

            response = requests.get(
                'https://chat-develop.one.th:8007/checkStaff/'+code+'/'+oneid)
            if response:
                raw = response.text
                raw = json.loads(raw)
                if raw['status'] == "fail":
                    # print(raw['status'])
                    return jsonify({"message": raw}), 401
                else:
                    sql_insert = []
                    for r in row:
                        sql_search_row = """ SELECT room.rname,t.time
                                            FROM ticketroom as r
                                            LEFT JOIN time as t
                                            ON r.row = t.row
                                            LEFT JOIN room as room
                                            ON r.rid = room.rid
                                            WHERE r.rid=%s AND r.row=%s AND Date(r.date) = %s """
                        cursor.execute(sql_search_row, (rid, r, date,))
                        columns = [column[0] for column in cursor.description]
                        search_row = toJson(cursor.fetchall(), columns)

                        if(search_row):
                            return jsonify({"message": "{} in {} is already Exists".format(search_row[0]['rname'], search_row[0]['time'])}), 400
                        else:
                            sql_insert.append("INSERT INTO `ticketroom`(`rid`, `row`, `col`, `oneid`, `code`, `name`, `department`, `email`, `description`, `numberofpeople`, `ps`, `date`) VALUES ('{}','{}','{}','{}','{}','{}','{}','{}','{}','{}','{}','{}'); ".format(
                                rid, r, col, oneid, code, name, department, email, description, numberofpeople, ps, date))

                for sql in sql_insert:
                    # print(sql)
                    cursor.execute(sql)

                return jsonify({"message": "Insert Success"})
            else:
                return jsonify({"message": "one id error"}), 500
    except Exception as e:
        print('error ===', e)
        current_app.logger.info(e)
        return jsonify(str(e))


@app.route('/api/v1/insert_projector', methods=['POST'])
@connect_sql()
def post_available_projector(cursor):
    try:
        if not request.is_json:
            return jsonify({"message": "Missing JSON in request"}), 400
        else:
            col = request.json.get('col', None)
            code = request.json.get('code', None)
            date = request.json.get('date', None)
            department = request.json.get('department', None)
            description = request.json.get('description', None)
            email = request.json.get('email', None)
            name = request.json.get('name', None)
            numberofpeople = request.json.get('numberofpeople', None)
            oneid = request.json.get('oneid', None)
            ps = request.json.get('ps', None)
            pid = request.json.get('pid', None)
            row = request.json.get('row', None)
            if not col or not code or not date or not department or not description or not email or not name or not numberofpeople or not oneid or not pid or not row:
                return jsonify({"message": "Missing parameter"}), 400

            response = requests.get(
                'https://chat-develop.one.th:8007/checkStaff/'+code+'/'+oneid)
            if response:
                raw = response.text
                raw = json.loads(raw)
                if raw['status'] == "fail":
                    # print(raw['status'])
                    return jsonify({"message": raw}), 401
                else:
                    sql_insert = []
                    for r in row:
                        sql_search_row = """SELECT t.time,projector.pname,t.row
                                            FROM ticketprojector as r
                                            LEFT JOIN time as t
                                            ON r.row = t.row
                                            LEFT JOIN projector as projector
                                            ON r.pid = projector.pid
                                            WHERE r.pid = %s AND r.row = %s AND Date(r.date) = %s """
                        cursor.execute(sql_search_row, (pid, r, date,))
                        columns = [column[0] for column in cursor.description]
                        search_row = toJson(cursor.fetchall(), columns)
                        if(search_row):
                            return jsonify({"message": "{} in {} is already Exists".format(search_row[0]['pname'], search_row[0]['time'])}), 400
                        else:
                            sql_insert.append("INSERT INTO `ticketprojector`(`pid`, `row`, `col`, `oneid`, `code`, `name`, `department`, `email`, `description`, `numberofpeople`, `ps`, `date`) VALUES ('{}','{}','{}','{}','{}','{}','{}','{}','{}','{}','{}','{}'); ".format(
                                pid, r, col, oneid, code, name, department, email, description, numberofpeople, ps, date))
                            # print(sql_insert)
                for sql in sql_insert:
                    # print(sql)
                    cursor.execute(sql)

                return jsonify({"message": "Insert Success"})
            else:
                return jsonify({"message": "one id error"}), 500
    except Exception as e:
        print('error ===', e)
        current_app.logger.info(e)
        return jsonify(str(e)), 500

# ------------------------ Room with time ---------------------#
@app.route('/api/v1/test', methods=['GET'])
@connect_sql()
def get_all_room_with_time(cursor):
    try:
        sql = """SELECT t.time ,room.rname, r.name , r.department , r.description , r.numberofpeople , r.ps ,r.date
                FROM ticketroom as r
                LEFT JOIN time as t
                ON r.row = t.row
                LEFT JOIN room as room
                ON r.rid = room.rid
                ORDER BY r.date DESC"""
        cursor.execute(sql,)
        columns = [column[0] for column in cursor.description]
        result = toJson(cursor.fetchall(), columns)
        return jsonify({"message": result})
    except Exception as e:
        print('error ===', e)
        current_app.logger.info(e)
        return jsonify(str(e))
