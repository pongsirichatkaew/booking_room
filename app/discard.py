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
                for date in resultBydate:
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
                return jsonify({"message": resultBydate})
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
        if not code and not oneid:
            return jsonify({"message": "Missing JSON in request"}), 400
        else:
            if not code or not oneid or not date:
                return jsonify({"message": "Missing parameter"}), 400
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
            for room in result:
                if room['rid'] == tmp_room_id:
                    times.append({room['row']:room['time']})
                else:
                    times = []
                    times.append({room['row']:room['time']})
                    roomResult.append({"rid":room['rid'],"rname":room['rname'],"date":room['date'],"times":times})
                    tmp_room_id = room['rid']
            print('result',roomResult)
            return jsonify({"result": roomResult})
    except Exception as e:
        print('error ===', e)
        current_app.logger.info(e)
        return jsonify(str(e)), 500
