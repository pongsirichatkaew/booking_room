from Config.config import *
from send_message import *
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
        print(date)
        print(code)
        print(oneid)
        if not code and not oneid:
            return jsonify({"message": "Missing JSON in request"}), 400
        else:
            if not code or not oneid :
                return jsonify({"message": "Missing parameter"}), 400
            elif not date:
                sql = """SELECT ticketroom.rid, room.rname, ticketroom.row, 
                          time.time, ticketroom.oneid, ticketroom.code, ticketroom.name, 
                          ticketroom.description, ticketroom.ps, ticketroom.date
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
                                {"rid": room['rid'], "rname": room['rname'], "date": format_date, "times": times})
                            tmp_room_id = room['rid']
                            tmp_date = room['date']
                print('result', roomResult)
                return jsonify({"result": roomResult})
            else:
                sql = """SELECT ticketroom.rid, room.rname, ticketroom.row, 
                          time.time, ticketroom.oneid, ticketroom.code, ticketroom.name, 
                          ticketroom.description, ticketroom.ps, ticketroom.date
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
                            {"rid": room['rid'], "rname": room['rname'], "date": format_date, "times": times})
                        tmp_room_id = room['rid']
            print('result', roomResult)
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
            for del_data in data:
                sql = """ DELETE FROM ticketroom WHERE code = %s AND oneid = %s AND rid = %s AND row = %s AND date = %s """
                cursor.execute(sql, (del_data['code'], del_data['oneid'], del_data['rid'], del_data['row'], del_data['date']))
            sql = "SELECT COUNT(trid) AS trid_num FROM `ticketroom` WHERE `date` LIKE %s AND code = %s";
            cursor.execute(sql, (date_time, code))
            columns = [column[0] for column in cursor.description]
            result = toJson(cursor.fetchall(), columns)
            return jsonify({"message": "success", "data": { "result": result[0]['trid_num']}}), 200
    except Exception as e:
        return jsonify(str(e)) 
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
        print(date)
        print(code)
        print(oneid)
        if not code and not oneid:
            return jsonify({"message": "Missing JSON in request"}), 400
        else:
            if not code or not oneid :
                return jsonify({"message": "Missing parameter"}), 400
            elif not date:
                sql = """SELECT ticketroom.rid, room.rname, ticketroom.row, 
                          time.time, ticketroom.oneid, ticketroom.code, ticketroom.name, 
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
                                {"rid": room['rid'], "rname": room['rname'], "date": format_date, "times": times})
                            tmp_room_id = room['rid']
                            tmp_date = room['date']
                print('result', roomResult)
                return jsonify({"result": roomResult})
            else:
                sql = """SELECT ticketroom.rid, room.rname, ticketroom.row, 
                          time.time, ticketroom.oneid, ticketroom.code, ticketroom.name, 
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
                            {"rid": room['rid'], "rname": room['rname'], "date": format_date, "times": times})
                        tmp_room_id = room['rid']
            print('result', roomResult)
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
            for del_data in data:
                sql = """ DELETE FROM ticketroom WHERE code = %s AND oneid = %s AND rid = %s AND row = %s AND date = %s """
                cursor.execute(sql, (del_data['code'], del_data['oneid'], del_data['rid'], del_data['row'], del_data['date']))
            sql = "SELECT COUNT(trid) AS trid_num FROM `ticketroom` WHERE `date` LIKE %s AND code = %s";
            cursor.execute(sql, (date_time, code))
            columns = [column[0] for column in cursor.description]
            result = toJson(cursor.fetchall(), columns)
            return jsonify({"message": "success", "data": { "result": result[0]['trid_num']}}), 200
    except Exception as e:
        return jsonify(str(e)) 
    except Exception as e:
        print('error ===', e)
        current_app.logger.info(e)
        return jsonify(str(e)), 500