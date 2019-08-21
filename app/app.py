from Config.config import *
from booking import *
from booking_time import *
from send_message import *
from discard import *


@app.route('/connect_backend', methods=['GET'])
def hello():
    return 'hello this is backend response'


@app.route('/connect_DB', methods=['GET'])
@connect_sql()
def same(cursor):
    sql = "SELECT * FROM room"
    cursor.execute(sql)
    columns = [column[0] for column in cursor.description]
    result = toJson(cursor.fetchall(), columns)
    return jsonify(result)


@app.route("/get_my_ip", methods=["GET"])
def get_my_ip():
    return jsonify({'ip': request.remote_addr}), 200


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', threaded=True, port=5000)
