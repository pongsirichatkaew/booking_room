from Config.config import *


def extract_time(json):
    try:
        # Also convert to int since update_time will be string.  When comparing
        # strings, "10" is smaller than "2".
        return int(json['rid'])
    except KeyError:
        return 0
# ------------------------ Vehicle with time ---------------------#
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
                print(all_time)
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
                    print(jsonResult)

                    sql_all_room = """ SELECT rid,rname,rnumber FROM `room` WHERE category='room' AND rstatus='show' """
                    cursor.execute(sql_all_room)
                    columns = [column[0] for column in cursor.description]
                    allroom = toJson(cursor.fetchall(), columns)

                    arr_allroom = []
                    arr_selectroom = []

                    for room in allroom:
                        arr_allroom.append(room['rid'])
                    print('alltime', arr_allroom)

                    for room in room_result:
                        arr_selectroom.append(room['rid'])
                    print('selectedtime', arr_selectroom)

                    my_room = set(arr_allroom) - set(arr_selectroom)
                    print('my_room', my_room)

                    list_item = []
                    for r in list(my_room):
                        for room in allroom:
                            if(r == room['rid']):
                                list_item.append(
                                    {"rid": room['rid'], "rname": room['rname']})

                    list_item.sort(key=extract_time, reverse=False)
                    # jsonResult.update({"times": list_time})
                    arr_time.append(jsonResult)

                    jsonResult.update({"rooms": list(list_item)})
                    print(arr_time)
                    # return jsonify({"result": jsonResult})`
                return jsonify({"message": arr_time})
            elif row and len(row) > 0 and date:
                arr_time = []
                for r in row:
                    time_sql = """ SELECT time FROM `time` where row = %s"""
                    cursor.execute(time_sql, r)
                    columns = [column[0] for column in cursor.description]
                    time = toJson(cursor.fetchall(), columns)

                    sql = """SELECT r.rid,r.date,r.name,room.rname FROM ticketroom as r
                    LEFT JOIN time as t ON r.row = t.row
                    LEFT JOIN room as room ON r.rid = room.rid
                    WHERE Date(r.date) = %s AND t.row = %s"""
                    cursor.execute(sql, (date, r,))
                    columns = [column[0] for column in cursor.description]
                    room_result = toJson(cursor.fetchall(), columns)
                    jsonResult = {"row": r, "time": time[0]["time"]}
                    print(jsonResult)

                    sql_all_room = """ SELECT rid,rname,rnumber FROM `room` WHERE category='room' AND rstatus='show' """
                    cursor.execute(sql_all_room)
                    columns = [column[0] for column in cursor.description]
                    allroom = toJson(cursor.fetchall(), columns)

                    arr_allroom = []
                    arr_selectroom = []

                    for room in allroom:
                        arr_allroom.append(room['rid'])
                    print('alltime', arr_allroom)

                    for room in room_result:
                        arr_selectroom.append(room['rid'])
                    print('selectedtime', arr_selectroom)

                    my_room = set(arr_allroom) - set(arr_selectroom)
                    print('my_room', my_room)

                    list_item = []
                    for r in list(my_room):
                        for room in allroom:
                            if(r == room['rid']):
                                list_item.append(
                                    {"rid": room['rid'], "rname": room['rname']})

                    list_item.sort(key=extract_time, reverse=False)
                    arr_time.append(jsonResult)

                    jsonResult.update({"rooms": list(list_item)})
                    print(arr_time)

                return jsonify({"message": arr_time})

    except Exception as e:
        current_app.logger.info(e)
        return jsonify({"message": str(e)}), 500
