from Config.config import *
import ast
# import datetime
from datetime import date
from datetime import timedelta
import json
import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from email.utils import COMMASPACE, formatdate


@connect_sql()
def format_json_for_send_message(cursor, nextDay, tabel, bot_id, tokenBot):
    sql_step1 = ''
    sql_step2 = ''
    sql_step3 = ''
    category = ''
    sql_find_twin = "SELECT r.date ,r.name AS name_room, r.email AS email_room, r.oneid AS oneid_room, p.name AS name_p, p.email AS email_p, p.oneid AS oneid_p FROM `ticketroom` AS r LEFT JOIN ticketprojector AS p ON r.name = p.name WHERE r.name = %s AND r.date = %s"
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
        SELECT r.name,r.oneid,r.department,r.email,r.description,r.numberofpeople,r.ps,r.date FROM ticketroom as r LEFT JOIN room as room ON r.rid = room.rid WHERE Date(r.date) = %s AND room.category = 'room' GROUP BY r.name
        """
        sql_step2 = """
        SELECT room.rname AS name,room.category,r.row,r.rid AS id FROM ticketroom as r
        LEFT JOIN room as room ON r.rid = room.rid WHERE Date(r.date) = %s AND r.name = %s AND room.category = 'room' GROUP BY r.rid
        """
        sql_step3 = """
        SELECT t.time, t.row FROM ticketroom as r
        LEFT JOIN time as t ON r.row = t.row WHERE Date(r.date) = %s AND r.rid = %s ORDER BY r.row ASC
        """
    elif tabel == 'ticketvehicle':
        sql_step1 = """
        SELECT r.name,r.oneid,r.department,r.email,r.description,r.numberofpeople,r.ps,r.date FROM ticketroom as r LEFT JOIN room as room ON r.rid = room.rid WHERE Date(r.date) = %s AND room.category = 'vehicle' GROUP BY r.name
        """
        sql_step2 = """
        SELECT room.rname AS name,room.category,r.row,r.rid AS id FROM ticketroom as r
        LEFT JOIN room as room ON r.rid = room.rid WHERE Date(r.date) = %s AND r.name = %s AND room.category = 'vehicle' GROUP BY r.rid
        """
        sql_step3 = """
        SELECT t.time, t.row FROM ticketroom as r
        LEFT JOIN time as t ON r.row = t.row WHERE Date(r.date) = %s AND r.rid = %s ORDER BY r.row ASC
        """

    sql = sql_step1
    cursor.execute(sql, nextDay)
    columns = [column[0] for column in cursor.description]
    results = toJson(cursor.fetchall(), columns)
    if len(results) != 0:
        name = results[0]['name']
        sql = sql_find_twin
        cursor.execute(sql, (name, nextDay))
        columns = [column[0] for column in cursor.description]
        findEmail = toJson(cursor.fetchall(), columns)
        email = None
        if len(findEmail) != 0:
            for emailUser in findEmail:
                if (emailUser['email_room'] is not None) and (emailUser['email_room'] != ''):
                    email = emailUser['email_room']
                    break
                if (emailUser['email_p'] is not None) and (emailUser['email_p'] != ''):
                    email = emailUser['email_p']
                    break

        results[0]['email'] = email

        sql = sql_find_twin
        cursor.execute(sql, (name, nextDay))
        columns = [column[0] for column in cursor.description]
        findOneid = toJson(cursor.fetchall(), columns)
        oneid = None
        if len(findOneid) != 0:
            for oneidUser in findOneid:
                if (oneidUser['oneid_room'] is not None) and (oneidUser['oneid_room'] != ''):
                    oneid = oneidUser['oneid_room']
                    break
                if (oneidUser['oneid_p'] is not None) and (oneidUser['oneid_p'] != ''):
                    oneid = oneidUser['oneid_p']
                    break

        results[0]['oneid'] = oneid

    for result in results:
        sql = sql_step2
        cursor.execute(sql, (nextDay, result['name']))
        columns = [column[0] for column in cursor.description]
        detailList = toJson(cursor.fetchall(), columns)
        detailResult = []
        timeStart = ''
        timeEnd = ''
        for detail in detailList:
            sql = sql_step3
            cursor.execute(sql, (nextDay, detail['id']))
            columns = [column[0] for column in cursor.description]
            times = toJson(cursor.fetchall(), columns)
            time = ''
            mergedTime = []

            if len(times) > 1:
                #8.00-9.00 9.00-10.00 12.00-13.00
                # 1 , 2 , 4
                txtTime = times[0]['time'] #first time 8.00-9.00
                txt = txtTime.split('-') #txt[0] = 8.00 txt[1] = 9.00
                timeStart = txt[0] #timeStart = 8.00
                timeEnd = '' 
                for index in range(len(times)): # 0,1,2
                    if (index + 1 != len(times)): 
                        if (times[index]['row'] - times[index + 1]['row']) == -1:  
                            #1 1-2 = -1
                            #2 2-4 = -2
                            txtTimeLast = times[index]['time'] # 8.00 - 9.00

                            txtLast = txtTimeLast.split('-') #  [0] = 8.00 [1] = 9.00
                            if len(txtLast) > 1:
                                timeEnd = txtLast[1] # txtEnd = 9.00
                            else:
                                timeEnd = txtLast[0]
                        else:
                            txtTimeLast = times[index]['time'] # 9.00 - 10.00
                            txtLast = txtTimeLast.split('-') # [0] 9.00 [1] 10.00
                            if len(txtLast) > 1:
                                timeEnd = txtLast[1] # 10.00
                            else:
                                timeEnd = txtLast[0]
                            mergedTime.append(timeStart + '-' + timeEnd) # mergeTime [8.00 - 10.00]
                            txtTime = times[index + 1]['time'] # txttime = 12.00 - 13.00
                            txt = txtTime.split('-') # txxt = [0] = 12.00 , [1] = 13.00
                            timeStart = txt[0] #timeStart = 12.00
                    else:
                        if (times[index]['row'] - times[index - 1]['row']) == 1: # 4 - 2 = 2
                            txtTimeLast = times[index]['time']
                            txtLast = txtTimeLast.split('-')
                            if len(txtLast) > 1:
                                timeEnd = txtLast[1]
                            else:
                                timeEnd = txtLast[0]
                            mergedTime.append(timeStart + '-' + timeEnd)
                        else:
                            mergedTime.append(times[index]['time']) # mergeTime [8.00 - 10.00,12.00-13.00]

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
                "bot_id": bot_id,
                "key_search": result['oneid']
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
        'ม.ค.',
        'ก.พ.',
        'มี.ค.',
        'เม.ย.',
        'พ.ค.',
        'มิ.ย.',
        'ก.ค.',
        'ส.ค.',
        'ก.ย.',
        'ต.ค.',
        'พ.ย.',
        'ธ.ค.'
    ]
    return monthList[int(val) - 1]


def nextDayThai(val):
    splitDay = val.split('-')
    yearThai = (int(splitDay[0]) + 543)
    dateThai = "{} {} {}".format(splitDay[2], month(splitDay[1]), yearThai)
    return dateThai


@app.route('/api/v1/send_message', methods=['GET'])
@connect_sql()
def send_message(cursor):
    try:
        today = date.today()
        # today = date.today() + timedelta(days=1)
        # nextDay = '2019-08-03'
        nextDay = today.strftime("%Y-%m-%d")
        dateThai = nextDayThai(nextDay)
        # bot_id = "B9f17b544628e5dfa8be224d00e759065"
        bot_id = "Bbc41524dcbc3515ebc3cfd36a1b4ac81"
        tokenBot = 'Bearer A62e8a53c57ec5330889b9f0f06e07e9cc5e82f556ae14b73acd9a53b758a5dddf8c22033ab5540788955425197bcac03'
        send_type = ''
        send_to_email = ''
        send_to_oneid = ''
        dateTime = datetime.datetime.now()

        ticketprojector = format_json_for_send_message(
            nextDay, 'ticketprojector', bot_id, tokenBot)
        ticketroom = format_json_for_send_message(
            nextDay, 'ticketroom', bot_id, tokenBot)
        ticketvehicle = format_json_for_send_message(
            nextDay, 'ticketvehicle', bot_id, tokenBot)
        result = []
        for roomList in ticketroom:
            result.append(roomList)

        for vehicleList in ticketvehicle:
            result.append(vehicleList)

        for deviceLists in ticketprojector:
            result.append(deviceLists)

        sql = "INSERT INTO `log_send_message` (`log_id`, `send_to_email`, `send_to_oneid`, `send_type`, `response`, `date`) VALUES (NULL, %s, %s, %s, %s, %s)"
        for item in result:
            send_to_email = item['email']
            send_to_oneid = item['oneid']
            if item['user_id'] is not None:
                categoryTitle = ''
                timeSelec = ''
                categoryTitle2 = ''
                send_msg_oneChat = ''
                split_name = item['name'].split('.')

                for idx, itemticket in enumerate(item['room']):
                    if itemticket['category'] == 'room':
                        categoryTitle = 'ห้องประชุม'
                        categoryTitle2 = 'ห้อง'
                    elif itemticket['category'] == 'vehicle':
                        categoryTitle = 'รถตู้'
                    else:
                        categoryTitle = 'อุปกรณ์'
                        categoryTitle2 = 'อุปกรณ์'


                    send_msg_oneChat_title = """พรุ่งนี้วันที่ {} คุณ {} ได้ทำการจอง{} \n""".format(
                        dateThai, split_name[1], categoryTitle)
                    timeSelec = 'เวลา: \n'
                    for index in range(len(itemticket['mergedTime'])):
                        timeSelec += str(itemticket['mergedTime'][index])
                        if index != len(itemticket['mergedTime']) - 1:
                            timeSelec += "\n"

                    send_msg_oneChat += """\n{} {} \nเหตุผล: {}\nจำนวนคน: {} \nหมายเหตุ: {} \n{}\n""".format(
                        categoryTitle2, itemticket['name'], item['description'], item['numberofpeople'], item['ps'], timeSelec)

                    if (idx + 1) != len(item['room']):
                        send_msg_oneChat += "\n\n"
                    if (idx + 1) != len(item['room']):
                        send_msg_oneChat += "--------------------------------\n"
                
                send_msg_oneChat += "--------------------------------\n"

                send_msg_oneChat += "คลิ้กที่นี่ https://intranet.inet.co.th/index.php/MainController/bookingroom/"
                payload_msg = {
                    "to": item['user_id'],
                    "bot_id": bot_id,
                    "type": "text",
                            "message": send_msg_oneChat_title + send_msg_oneChat
                }
                send_type = 'one_id'
                dateTime = datetime.datetime.now()
                try:
                    response_msg = requests.request("POST", url="https://chat-public.one.th:8034/api/v1/push_message",
                                                    headers={'Authorization': tokenBot}, json=payload_msg, timeout=(60 * 1)).json()
                    response = response_msg['status']
                    cursor.execute(
                        sql, (send_to_email, send_to_oneid, send_type, response, dateTime))
                except Exception as e:
                    current_app.logger.info(e)
                    response = 'error'
                    cursor.execute(
                        sql, (send_to_email, send_to_oneid, send_type, response, dateTime))

            if item['email'] is not None:
                categoryTitle = ''
                timeSelec = ''
                
                for idx, itemticket in enumerate(item['room']):
                    if itemticket['category'] == 'room':
                        categoryTitle = 'ห้องประชุม'
                        categoryTitle2 = 'ห้อง'

                    elif itemticket['category'] == 'vehicle':
                        categoryTitle = 'รถตู้'
                    else:
                        categoryTitle = 'อุปกรณ์'
                        
                    send_msg_title = "พรุ่งนี้วันที่ " + dateThai + " คุณ " + split_name[1] + " ได้ทำการจองตามรายการ ดังนี้ <br><br>"
                    send_msg_email = ''
                    
                    timeSelec = 'เวลา: <br>'
                    timeSelec += '<ul style="padding-left: 15px;">'
                    for index in range(len(itemticket['mergedTime'])):
                        timeSelec += '<li>' + \
                            str(itemticket['mergedTime'][index]) + '</li>'
                    timeSelec += '</ul>'
                    send_msg_email += """ <ul style="list-style-type:none; padding: 0; margin: 0;"> """
                    send_msg_email += """
                    <li>{}. {} </li>
                    <li>เหตุผล: {} </li>
                    <li>จำนวนคน: {} </li>
                    <li>หมายเหตุ: {} </li>
                    <li>{} </li>""".format(
                        (idx + 1), itemticket['name'], item['description'], item['numberofpeople'], item['ps'], timeSelec)
                    send_msg_email += "</ul>"
                    send_msg_email += "<br>"

                server = "mailtx.inet.co.th"
                send_from = 'noreply.booking@inet.co.th'
                send_to = item['email']
                subject = 'แจ้งเตือนการจองห้องประชุมและรถตู้'
                text = send_msg_title + send_msg_email

                msg = MIMEMultipart()
                msg['From'] = send_from
                msg['To'] = send_to
                msg['Date'] = formatdate(localtime=True)
                msg['Subject'] = subject
                msg.attach(MIMEText(text, "html", "utf-8"))
                send_type = 'email'
                dateTime = datetime.datetime.now()
                try:
                    smtp = smtplib.SMTP(server)
                    smtp.sendmail(send_from, send_to, msg.as_string())
                    smtp.close()
                    response = 'success'
                    cursor.execute(
                        sql, (send_to_email, send_to_oneid, send_type, response, dateTime))
                except Exception as e:
                    current_app.logger.info(e)
                    response = 'error'
                    cursor.execute(
                        sql, (send_to_email, send_to_oneid, send_type, response, dateTime))

        return jsonify(result)
    except Exception as e:
        current_app.logger.info(e)
        response = 'error'
        sql = "INSERT INTO `log_send_message` (`log_id`, `send_to_email`, `send_to_oneid`, `send_type`, `response`, `date`) VALUES (NULL, %s, %s, %s, %s, %s)"
        cursor.execute(sql, (send_to_email, send_to_oneid,
                             send_type, response, dateTime))
