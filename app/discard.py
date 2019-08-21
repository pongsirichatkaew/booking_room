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
                cursor.execute(sql,(oneid, code))
                columns = [column[0] for column in cursor.description]
                resultBydate = toJson(cursor.fetchall(), columns)
                date_result=""
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
                    cursor.execute(sql2,(oneid, code, date['date']))
                    columns = [column[0] for column in cursor.description]
                    result = toJson(cursor.fetchall(), columns)
                    date_result = {"date": result[0]['date']}
                    jsonResult = {"rid": result[0]["rid"], "rname": result[0]["rname"], "description": result[0]['description'], "ps": result[0]['ps']}
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

