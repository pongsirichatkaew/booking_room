from Config.config import *
import ast

# ------------------------ All Ticket Room -------------------#
@app.route('/api/v1/rooms', methods=['GET'])
@connect_sql()
def get_all_rooms(cursor):
    try:
        sql = """SELECT * FROM room """
        cursor.execute(sql,)
        columns = [column[0] for column in cursor.description]
        result = toJson(cursor.fetchall(), columns)
        return jsonify({"result": result})
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
                print('date_all_room', date)
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
                return jsonify(result)
            elif room_id and date:
                print('date_some_room', date)
                print('date_some_room', type(room_id))
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
                return jsonify(result)
    except Exception as e:
        current_app.logger.info(e)
        return jsonify({"message": str(e)}), 500

# ------------------------ Room with time ---------------------#
@app.route('/api/v1/available_room', methods=['POST'])
@connect_sql()
def get_available_ticket_room(cursor):
    try:
        if not request.is_json:
            return jsonify({"message": "Missing JSON in request"}), 400
        else:
            date = request.json.get('date', None)
            room_id = request.json.get('rid', None)
            if not date:
                return jsonify({"message": "Missing parameter"}), 400
            elif not room_id and date:
                room_sql = """SELECT rid,rname FROM room  WHERE category = 'room' AND rstatus='show' """
                cursor.execute(room_sql, )
                columns = [column[0] for column in cursor.description]
                allroom = toJson(cursor.fetchall(), columns)
                arr_room = []
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
                    jsonResult = {"name": room["rname"], "rid": room["rid"]}
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

                    jsonResult.update({"times": list_time})
                    arr_room.append(jsonResult)
                    # jsonResult.update({"times": list(my_time)})
                    # return jsonify({"result": jsonResult})
                return jsonify({"result": arr_room})
            elif room_id and date:
                sql_room_id = """SELECT rname FROM `room` WHERE rid = %s and category = 'room' AND rstatus='show'"""
                cursor.execute(sql_room_id, (room_id,))
                columns = [column[0] for column in cursor.description]
                result_room_id = toJson(cursor.fetchall(), columns)
                if result_room_id:
                    room_name = result_room_id[0]['rname']
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
                    jsonResult = {"name": room_name, "rid": room_id}
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
                    jsonResult.update({"times": list_time})
                    print('mytime', my_time)
                    print('mytimelist', list(my_time))
                    print('listtime', list_time)
                    # jsonResult.update({"times": list(my_time)})
                    return jsonify({"result": jsonResult})
                else:
                    return jsonify({"message": "room_id is invalid"}), 400
    except Exception as e:
        current_app.logger.info(e)
        return jsonify({"message": str(e)}), 500


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
                    jsonResult = {"name": room["rname"], "rid": room["rid"]}
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

                    jsonResult.update({"times": list_time})
                    arr_room.append(jsonResult)
                    # jsonResult.update({"times": list(my_time)})
                    # return jsonify({"result": jsonResult})
                return jsonify({"result": arr_room})
            elif vehicle_id and date:
                sql_vehicle_id = """SELECT rname FROM `room` WHERE rid = %s and category = 'vehicle' AND rstatus='show'"""
                cursor.execute(sql_vehicle_id, (vehicle_id,))
                columns = [column[0] for column in cursor.description]
                result_room_id = toJson(cursor.fetchall(), columns)
                if result_room_id:
                    room_name = result_room_id[0]['rname']
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
                    jsonResult = {"name": room_name, "rid": vehicle_id}
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
                    jsonResult.update({"times": list_time})
                    print('mytime', my_time)
                    print('mytimelist', list(my_time))
                    print('listtime', list_time)
                    # jsonResult.update({"times": list(my_time)})
                    return jsonify({"result": jsonResult})
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
                    jsonResult = {"name": projector["pname"], "pid": projector["pid"]}
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

                    jsonResult.update({"times": list_time})
                    arr_room.append(jsonResult)
                    # jsonResult.update({"times": list(my_time)})
                    # return jsonify({"result": jsonResult})
                return jsonify({"result": arr_room})
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
                    jsonResult.update({"times": list_time})
                    print('mytime', my_time)
                    print('mytimelist', list(my_time))
                    print('listtime', list_time)
                    # jsonResult.update({"times": list(my_time)})
                    return jsonify({"result": jsonResult})
                else:
                    return jsonify({"message": "pid is invalid"}), 400
    except Exception as e:
        current_app.logger.info(e)
        return jsonify({"message": str(e)}), 500

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
        return jsonify(result)
    except Exception as e:
        print('error ===', e)
        current_app.logger.info(e)
        return jsonify(str(e))
