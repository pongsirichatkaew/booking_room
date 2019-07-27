from Config.config import *
import ast
# import datetime
from datetime import date
from datetime import timedelta
import json

@connect_sql()
def format_json_for_send_message (cursor, nextDay, tabel, bot_id, tokenBot):
    sql_step1 = ''
    sql_step2 = ''
    sql_step3 = ''
    category = ''
    if tabel == 'ticketprojector':
        sql_step1 = """
        SELECT r.code,r.oneid,r.name,r.department,r.email,r.description,r.numberofpeople,r.ps,r.date FROM ticketprojector as r 
        WHERE Date(r.date) = %s GROUP BY r.name
        """
        sql_step2 = """
        SELECT projector.pname AS name,r.row,r.pid AS id FROM ticketprojector as r
            LEFT JOIN projector as projector ON r.pid = projector.pid WHERE Date(r.date) = %s AND r.name = %s GROUP BY r.pid
        """
        sql_step3 = """
        SELECT t.time, t.row FROM ticketprojector as r
        LEFT JOIN time as t ON r.row = t.row WHERE Date(r.date) = %s AND r.pid = %s ORDER BY r.row ASC
        """
    elif tabel == 'ticketroom':
        sql_step1 = """
        SELECT r.name,r.oneid,r.department,r.email,r.description,r.numberofpeople,r.ps,r.date FROM ticketroom as r WHERE Date(r.date) = %s GROUP BY r.name
        """
        sql_step2 = """
        SELECT room.rname AS name,room.category,r.row,r.rid AS id FROM ticketroom as r
        LEFT JOIN room as room ON r.rid = room.rid WHERE Date(r.date) = %s AND r.name = %s GROUP BY r.rid
        """
        sql_step3 = """
        SELECT t.time, t.row FROM ticketroom as r
        LEFT JOIN time as t ON r.row = t.row WHERE Date(r.date) = %s AND r.rid = %s ORDER BY r.row ASC
        """

    sql = sql_step1
    cursor.execute(sql, nextDay)
    columns = [column[0] for column in cursor.description]
    results = toJson(cursor.fetchall(), columns)

    for result in results:
        sql = sql_step2
        cursor.execute(sql, (nextDay,result['name']))
        columns = [column[0] for column in cursor.description]
        detailList = toJson(cursor.fetchall(), columns)
        detailResult = []
        timeStart = ''
        timeEnd = ''
        for detail in detailList:
            sql = sql_step3
            cursor.execute(sql, (nextDay,detail['id']))
            columns = [column[0] for column in cursor.description]
            times = toJson(cursor.fetchall(), columns)
            time = ''
            mergedTime = []

            if len(times) > 1:
                txtTime = times[0]['time']
                txt = txtTime.split('-')
                timeStart = txt[0]
                timeEnd = ''
                for index in range(len(times)):
                    tmp = -1
                    if (index + 1 != len(times)):
                        if (times[index]['row'] - times[index + 1]['row']) == -1:
                            txtTimeLast = times[index]['time']
                            txtLast = txtTimeLast.split('-')
                            if len(txtLast) > 1:
                                timeEnd = txtLast[1]
                            else:
                                timeEnd = txtLast[0]
                        else:
                            txtTimeLast = times[index]['time']
                            txtLast = txtTimeLast.split('-')
                            if len(txtLast) > 1:
                                timeEnd = txtLast[1]
                            else:
                                timeEnd = txtLast[0]
                            mergedTime.append(timeStart + '-' + timeEnd)
                            txtTime = times[index + 1]['time']
                            txt = txtTime.split('-')
                            timeStart = txt[0]
                    else:
                        if (times[index]['row'] - times[index - 1]['row']) == 1:
                            txtTimeLast = times[index]['time']
                            txtLast = txtTimeLast.split('-')
                            if len(txtLast) > 1:
                                timeEnd = txtLast[1]
                            else:
                                timeEnd = txtLast[0]
                            mergedTime.append(timeStart + '-' + timeEnd)
                        else:
                            txtTimeLast = times[index]['time']
                            txtLast = txtTimeLast.split('-')
                            if len(txtLast) > 1:
                                timeEnd = txtLast[1]
                            else:
                                timeEnd = txtLast[0]
                            mergedTime.append(times[index]['time'])

                time = timeStart + '-' + timeEnd
            else:
                mergedTime.append(times[0]['time'])


            if tabel == 'ticketprojector':
                category = 'device'
            else:
                category = detail['category']

            detailResult.append({
                'category': category,
                'name': detail['name'],
                'times': times,
                'mergedTime': mergedTime
            })

        if result['oneid'] is not None:
            payload = {
                "bot_id" : bot_id,
                "key_search" : result['oneid']
            }
            try:
                response = requests.request("POST", url="https://chat-manage.one.th:8997/api/v1/searchfriend",
                headers={'Authorization': tokenBot}, json=payload, timeout=(60 * 1)).json()
                if response['status'] != 'fail':
                    result['user_id'] = response['friend']['user_id']
                else:
                    result['user_id'] = None
            except Exception as e:
                current_app.logger.info(e)
        else:
            result['user_id'] = None

        result['room'] = detailResult
    return results

def month(val):
    monthList = [
    'ม.ค',
    'ก.พ',
    'มี.ค',
    'เม.ย',
    'พ.ค',
    'มิ.ย',
    'ก.ค',
    'ส.ค',
    'ก.ย',
    'ต.ค',
    'พ.ย',
    'ธ.ค'
    ]
    return monthList[int(val) - 1]

def nextDayThai (val):
    splitDay = val.split('-')
    yearThai = (int(splitDay[0]) + 543) - 2500
    dateThai = "{} {} {}".format(splitDay[2],month(splitDay[1]), yearThai)
    return dateThai

@app.route('/api/v1/send_message', methods=['GET'])
@connect_sql()
def send_message(cursor):
    try:
        today = date.today() + timedelta(days=1) 
        nextDay = '2019-07-27'
        # nextDay = today.strftime("%Y-%m-%d")
        dateThai = nextDayThai(nextDay)
        bot_id = "B9f17b544628e5dfa8be224d00e759065"
        tokenBot = 'Bearer A62e8a53c57ec5330889b9f0f06e07e9cc5e82f556ae14b73acd9a53b758a5dddf8c22033ab5540788955425197bcac03'

        ticketprojector = format_json_for_send_message(nextDay, 'ticketprojector', bot_id, tokenBot)
        ticketroom = format_json_for_send_message(nextDay, 'ticketroom', bot_id, tokenBot)
        result = []
        for roomList in ticketroom:
            result.append(roomList)
        
        for deviceLists in ticketprojector:
            result.append(deviceLists)

        for item in result:
            if item['user_id'] is not None:
                categoryTitle = ''
                timeSelec = ''
                send_msg_oneChat_title = """พรุ่งนี้วันที่ {} คุณ {} ได้ทำการจอง{} \n""".format(dateThai,item['name'],categoryTitle)
                send_msg_oneChat = ''
                for idx, itemticket in enumerate(item['room']):
                    if itemticket['category'] == 'room':
                        categoryTitle ='ห้อง'
                    elif itemticket['category'] == 'vehicle':
                        categoryTitle ='รถตู้'
                    else:
                        categoryTitle ='อุปกรณ์'
                    timeSelec = 'เวลา: \n'
                    for index in range(len(itemticket['mergedTime'])):
                        timeSelec += str(itemticket['mergedTime'][index])
                        if index != len(itemticket['mergedTime']) - 1:
                            timeSelec += "\n"

                    send_msg_oneChat += """\n{}. {} \nเหตุผล: {}\nจำนวนคน: {} \nหมายเหตุ: {} \n{}""".format(
                        (idx + 1),itemticket['name'],item['description'],item['numberofpeople'],item['ps'], timeSelec)
                    if (idx + 1) != len(item['room']):
                        send_msg_oneChat += "\n\n"
                    if (idx + 1) != len(item['room']):
                        send_msg_oneChat += "----------------------------------------\n"
                payload_msg =  {
                            "to" : item['user_id'],
                            "bot_id" : bot_id,
                            "type" : "text",
                            "message" : send_msg_oneChat_title + send_msg_oneChat
                        }
                response_msg = requests.request("POST", url="https://chat-public.one.th:8034/api/v1/push_message",
                headers={'Authorization': tokenBot}, json=payload_msg, timeout=(60 * 1)).json()

            if item['email'] is not None:
                categoryTitle = ''
                timeSelec = ''
                send_msg_title = """พรุ่งนี้วันที่ {} คุณ {} ได้ทำการจองตามรายการดังนี้ <br><br>""".format(dateThai,item['name'])
                send_msg_email = ''
                for idx, itemticket in enumerate(item['room']):
                    if itemticket['category'] == 'room':
                        categoryTitle ='ห้อง'
                    elif itemticket['category'] == 'vehicle':
                        categoryTitle ='รถตู้'
                    else:
                        categoryTitle ='อุปกรณ์'
                    timeSelec = 'เวลา: <br>'
                    timeSelec += '<ul style="padding-left: 15px;">'
                    for index in range(len(itemticket['mergedTime'])):
                        timeSelec += '<li>' + str(itemticket['mergedTime'][index]) + '</li>'
                    timeSelec += '</ul>'
                    send_msg_email += """ <ul style="list-style-type:none; padding: 0; margin: 0;"> """
                    send_msg_email += """
                    <li>{}. {} </li>
                    <li>เหตุผล: {} </li>
                    <li>จำนวนคน: {} </li>
                    <li>หมายเหตุ: {} </li> 
                    <li>{} </li>""".format(
                        (idx + 1),itemticket['name'],item['description'],item['numberofpeople'],item['ps'], timeSelec)
                    send_msg_email += "</ul>"
                    send_msg_email +="<br>"

                msg = Message('แจ้งเตือนการจองห้องประชุมและรถตู้', sender = 'noreplysotool@gmail.com', recipients = ['p.jirayusakul@gmail.com'])
                msg.html = send_msg_title + send_msg_email
                mail.send(msg)

        return jsonify(result)
    except Exception as e:
        current_app.logger.info(e)
        return jsonify(str(e)), 500