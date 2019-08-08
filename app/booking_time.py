from Config.config import *


def extract_time(json):
    try:
        # Also convert to int since update_time will be string.  When comparing
        # strings, "10" is smaller than "2".
        return int(json['rid'])
    except KeyError:
        return 0

# ------------------------ Vehicle with room ---------------------#
@app.route('/api/v1/available_time_room', methods=['POST'])
@connect_sql()
def get_available_time_room(cursor):
    try:
        if not request.is_json:
            return jsonify({"message": "Missing JSON in request"}), 400
        else:
            date = request.json.get('date', None)
            row = request.json.get('row', None)
            if not date:
                return jsonify({"message": "Missing parameter"}), 400
            elif not row and date:
                time_sql = """ SELECT row,time FROM `time` """
                cursor.execute(time_sql, )
                columns = [column[0] for column in cursor.description]
                all_time = toJson(cursor.fetchall(), columns)
                # print(all_time)
                arr_time = []
                for time in all_time:
                    sql = """SELECT r.rid,r.date,r.name,room.rname FROM ticketroom as r
                    LEFT JOIN time as t ON r.row = t.row
                    LEFT JOIN room as room ON r.rid = room.rid
                    WHERE Date(r.date) = %s AND t.row = %s"""
                    cursor.execute(sql, (date, time["row"],))
                    columns = [column[0] for column in cursor.description]
                    room_result = toJson(cursor.fetchall(), columns)
                    jsonResult = {"row": time["row"], "time": time["time"]}
                    # print(jsonResult)

                    sql_all_room = """ SELECT rid,rname,rnumber FROM `room` WHERE category='room' AND rstatus='show' """
                    cursor.execute(sql_all_room)
                    columns = [column[0] for column in cursor.description]
                    allroom = toJson(cursor.fetchall(), columns)

                    arr_allroom = []
                    arr_selectroom = []

                    for room in allroom:
                        arr_allroom.append(room['rid'])
                    # print('alltime', arr_allroom)

                    for room in room_result:
                        arr_selectroom.append(room['rid'])
                    # print('selectedtime', arr_selectroom)

                    my_room = set(arr_allroom) - set(arr_selectroom)
                    # print('my_room', my_room)

                    list_item = []
                    for r in list(my_room):
                        for room in allroom:
                            if(r == room['rid']):
                                list_item.append(
                                    {"rid": room['rid'], "rname": room['rname'], "rnumber": room['rnumber']})

                    list_item.sort(key=extract_time, reverse=False)
                    # jsonResult.update({"times": list_time})
                    arr_time.append(jsonResult)

                    jsonResult.update({"rooms": list(list_item)})
                    # print(arr_time)
                    # return jsonify({"result": jsonResult})`
                return jsonify({"message": arr_time})
            elif row and len(row) > 0 and date:
                arr_time = []
                for r in row:
                    time_sql = """ SELECT time FROM `time` where row = %s"""
                    cursor.execute(time_sql, r)
                    columns = [column[0] for column in cursor.description]
                    time = toJson(cursor.fetchall(), columns)

                    if time and len(time) > 0:
                        sql = """SELECT r.rid,r.date,r.name,room.rname FROM ticketroom as r
                        LEFT JOIN time as t ON r.row = t.row
                        LEFT JOIN room as room ON r.rid = room.rid
                        WHERE Date(r.date) = %s AND t.row = %s"""
                        cursor.execute(sql, (date, r,))
                        columns = [column[0] for column in cursor.description]
                        room_result = toJson(cursor.fetchall(), columns)
                        jsonResult = {"row": r, "time": time[0]["time"]}
                        # print(jsonResult)

                        sql_all_room = """ SELECT rid,rname,rnumber FROM `room` WHERE category='room' AND rstatus='show' """
                        cursor.execute(sql_all_room)
                        columns = [column[0] for column in cursor.description]
                        allroom = toJson(cursor.fetchall(), columns)

                        arr_allroom = []
                        arr_selectroom = []

                        for room in allroom:
                            arr_allroom.append(room['rid'])
                        # print('alltime', arr_allroom)

                        for room in room_result:
                            arr_selectroom.append(room['rid'])
                        # print('selectedtime', arr_selectroom)

                        my_room = set(arr_allroom) - set(arr_selectroom)
                        # print('my_room', my_room)
11111111111111111111111111111111111111
                        list_item = []
                        for r in list(my_room):
                            for room in allroom:
                                if(r == room['rid']):
                                    list_item.append(
                                        {"rid": room['rid'], "rname": room['rname'], "rnumber": room['rnumber']})

                        list_item.sort(key=extract_time, reverse=False)
                        arr_time.append(jsonResult)

                        jsonResult.update({"rooms": list(list_item)})
                        # print(arr_time)
                    else:
                        return jsonify({"message": "invalid row"})
                return jsonify({"message": arr_time})
    except Exception as e:
        current_app.logger.info(e)
        return jsonify({"message": str(e)}), 500


# ------------------------ Vehicle with time ---------------------#

@app.route('/api/v1/available_time_vehicle', methods=['POST'])
@connect_sql()
def get_available_time_vehicle(cursor):
    try:
        if not request.is_json:
            return jsonify({"message": "Missing JSON in request"}), 400
        else:
            date = request.json.get('date', None)
            row = request.json.get('row', None)
            if not date:
                return jsonify({"message": "Missing parameter"}), 400
            elif not row and date:
                time_sql = """ SELECT row,time FROM `time` """
                cursor.execute(time_sql, )
                columns = [column[0] for column in cursor.description]
                all_time = toJson(cursor.fetchall(), columns)
                # print(all_time)
                arr_time = []
                for time in all_time:
                    sql = """SELECT r.rid,r.date,r.name,room.rname FROM ticketroom as r
                    LEFT JOIN time as t ON r.row = t.row
                    LEFT JOIN room as room ON r.rid = room.rid
                    WHERE Date(r.date) = %s AND t.row = %s"""
                    cursor.execute(sql, (date, time["row"],))
                    columns = [column[0] for column in cursor.description]
                    room_result = toJson(cursor.fetchall(), columns)
                    jsonResult = {"row": time["row"], "time": time["time"]}
                    # print(jsonResult)

                    sql_all_room = """ SELECT rid,rname,rnumber FROM `room` WHERE category='vehicle' AND rstatus='show' """
                    cursor.execute(sql_all_room)
                    columns = [column[0] for column in cursor.description]
                    allroom = toJson(cursor.fetchall(), columns)

                    arr_allroom = []
                    arr_selectroom = []

                    for room in allroom:
                        arr_allroom.append(room['rid'])
                    # print('alltime', arr_allroom)

                    for room in room_result:
                        arr_selectroom.append(room['rid'])
                    # print('selectedtime', arr_selectroom)

                    my_room = set(arr_allroom) - set(arr_selectroom)
                    # print('my_room', my_room)

                    list_item = []
                    for r in list(my_room):
                        for room in allroom:
                            if(r == room['rid']):
                                list_item.append(
                                    {"rid": room['rid'], "rname": room['rname'], "rnumber": room['rnumber']})

                    list_item.sort(key=extract_time, reverse=False)
                    # jsonResult.update({"times": list_time})
                    arr_time.append(jsonResult)

                    jsonResult.update({"rooms": list(list_item)})
                    # print(arr_time)
                    # return jsonify({"result": jsonResult})`
                return jsonify({"message": arr_time})
            elif row and len(row) > 0 and date:
                arr_time = []
                for r in row:
                    time_sql = """ SELECT time FROM `time` where row = %s"""
                    cursor.execute(time_sql, r)
                    columns = [column[0] for column in cursor.description]
                    time = toJson(cursor.fetchall(), columns)
                    if time and len(time) > 0:
                        sql = """SELECT r.rid,r.date,r.name,room.rname FROM ticketroom as r
                        LEFT JOIN time as t ON r.row = t.row
                        LEFT JOIN room as room ON r.rid = room.rid
                        WHERE Date(r.date) = %s AND t.row = %s"""
                        cursor.execute(sql, (date, r,))
                        columns = [column[0] for column in cursor.description]
                        room_result = toJson(cursor.fetchall(), columns)
                        jsonResult = {"row": r, "time": time[0]["time"]}
                        # print(jsonResult)

                        sql_all_room = """ SELECT rid,rname,rnumber FROM `room` WHERE category='vehicle' AND rstatus='show' """
                        cursor.execute(sql_all_room)
                        columns = [column[0] for column in cursor.description]
                        allroom = toJson(cursor.fetchall(), columns)

                        arr_allroom = []
                        arr_selectroom = []

                        for room in allroom:
                            arr_allroom.append(room['rid'])
                        # print('alltime', arr_allroom)

                        for room in room_result:
                            arr_selectroom.append(room['rid'])
                        # print('selectedtime', arr_selectroom)

                        my_room = set(arr_allroom) - set(arr_selectroom)
                        # print('my_room', my_room)

                        list_item = []
                        for r in list(my_room):
                            for room in allroom:
                                if(r == room['rid']):
                                    list_item.append(
                                        {"rid": room['rid'], "rname": room['rname'], "rnumber": room['rnumber']})

                        list_item.sort(key=extract_time, reverse=False)
                        arr_time.append(jsonResult)

                        jsonResult.update({"rooms": list(list_item)})
                        # print(arr_time)
                    else:
                        return jsonify({"message": "invalid row"})

                return jsonify({"message": arr_time})
    except Exception as e:
        current_app.logger.info(e)
        return jsonify({"message": str(e)}), 500


# ------------------------ Device with time ---------------------#

@app.route('/api/v1/available_time_device', methods=['POST'])
@connect_sql()
def get_available_time_device(cursor):
    try:
        if not request.is_json:
            return jsonify({"message": "Missing JSON in request"}), 400
        else:
            date = request.json.get('date', None)
            row = request.json.get('row', None)
            if not date:
                return jsonify({"message": "Missing parameter"}), 400
            elif not row and date:
                time_sql = """ SELECT row,time FROM `time` """
                cursor.execute(time_sql, )
                columns = [column[0] for column in cursor.description]
                all_time = toJson(cursor.fetchall(), columns)
                arr_time = []
                for time in all_time:
                    sql = """SELECT t.time,projector.pname,t.row,r.pid
                            FROM ticketprojector as r
                            LEFT JOIN time as t
                            ON r.row = t.row
                            LEFT JOIN projector as projector
                            ON r.pid = projector.pid
                            WHERE Date(r.date) = %s AND r.row = %s  """
                    cursor.execute(sql, (date, time["row"],))
                    columns = [column[0] for column in cursor.description]
                    device_result = toJson(cursor.fetchall(), columns)
                    jsonResult = {"row": time["row"], "time": time["time"]}

                    # print(jsonResult)

                    sql_all_device = """ SELECT pid,pname FROM `projector` WHERE pstatus ='show' """
                    cursor.execute(sql_all_device)
                    columns = [column[0] for column in cursor.description]
                    all_device = toJson(cursor.fetchall(), columns)

                    arr_alldevices = []
                    arr_selectdevice = []

                    # print('all_device', all_device)
                    # print('device_result', device_result)

                    for device in all_device:
                        arr_alldevices.append(device['pid'])

                    for device in device_result:
                        arr_selectdevice.append(device['pid'])

                    my_devices = set(arr_alldevices) - set(arr_selectdevice)

                    list_item = []
                    for r in list(my_devices):
                        for device in all_device:
                            if(r == device['pid']):
                                list_item.append(
                                    {"pid": device['pid'], "pname": device['pname']})

                    list_item.sort(key=extract_time, reverse=False)
                    arr_time.append(jsonResult)
                    jsonResult.update({"devices": list(list_item)})

                return jsonify({"message": arr_time})
            elif row and len(row) > 0 and date:
                arr_time = []
                for r in row:
                    time_sql = """ SELECT time FROM `time` where row = %s"""
                    cursor.execute(time_sql, r)
                    columns = [column[0] for column in cursor.description]
                    time = toJson(cursor.fetchall(), columns)
                    if time:
                        sql = """SELECT t.time,projector.pname,t.row,r.pid
                                    FROM ticketprojector as r
                                    LEFT JOIN time as t
                                    ON r.row = t.row
                                    LEFT JOIN projector as projector
                                    ON r.pid = projector.pid
                                    WHERE Date(r.date) = %s AND r.row = %s """
                        cursor.execute(sql, (date, r,))
                        columns = [column[0] for column in cursor.description]
                        device_result = toJson(cursor.fetchall(), columns)
                        jsonResult = {"row": r, "time": time[0]["time"]}
                        # print(jsonResult)

                        sql_all_device = """ SELECT pid,pname FROM `projector` WHERE pstatus ='show' """
                        cursor.execute(sql_all_device)
                        columns = [column[0] for column in cursor.description]
                        all_device = toJson(cursor.fetchall(), columns)

                        arr_alldevices = []
                        arr_selectdevice = []


                        for device in all_device:
                            arr_alldevices.append(device['pid'])

                        for device in device_result:
                            arr_selectdevice.append(device['pid'])

                        # print("arr_alldevices",arr_alldevices)
                        # print("arr_selectdevice",arr_selectdevice)

                        my_devices = set(arr_alldevices) - set(arr_selectdevice)

                        list_item = []
                        for r in list(my_devices):
                            for device in all_device:
                                if(r == device['pid']):
                                    list_item.append(
                                        {"pid": device['pid'], "pname": device['pname']})

                        list_item.sort(key=extract_time, reverse=False)
                        arr_time.append(jsonResult)

                        jsonResult.update({"devices": list(list_item)})
                    else:
                        return jsonify({"message": "invalid row"})

                return jsonify({"message": arr_time})
    except Exception as e:
        current_app.logger.info(e)
        return jsonify({"message": str(e)}), 500
