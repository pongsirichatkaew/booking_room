from Config.config import *
from booking import *
import requests


@connect_sql()
def send_json_chatme(cursor, oneid, row, date, rid, webviewName, status_type):
    try:
        ################ Chat ME API ####################

        room_sql = """SELECT rid,rname FROM room  WHERE rid = %s AND rstatus='show' """
        cursor.execute(room_sql, (rid))
        columns = [column[0] for column in cursor.description]
        room_result = toJson(cursor.fetchall(), columns)

        room = room_result[0]['rname']

        strTime = timeMerge2(row)

        authorization = 'Bearer A62e8a53c57ec5330889b9f0f06e07e9cc5e82f556ae14b73acd9a53b758a5dddf8c22033ab5540788955425197bcac03'
        botid = 'Bbc41524dcbc3515ebc3cfd36a1b4ac81'

        playload_friend = {
            "bot_id": botid,
            "key_search": oneid
        }
        friend_check = requests.request("POST", url="https://chat-manage.one.th:8997/api/v1/searchfriend",
                                        headers={'Authorization': authorization}, json=playload_friend, timeout=(60 * 1)).json()

        if friend_check['status'] == "success":
            userID = str(friend_check['friend']['user_id'])

            json_api = {
                "userId": userID,
                "webviewName": webviewName,
                "botId": botid,
                "accessToken": "A18117d3ed0875eebb7fc1acb6e97d73e1417ec732bd64a22a0d6adb95b469d17 856d1d53a8c8432398c2f4e1995dcb51",
                "data": {
                    "type": status_type,
                    "date": date,
                    "time": strTime,
                    "room": room
                }
            }

            res = requests.request(
                "POST", url="https://cmpoc05.chatme.co.th/banitim/TVSSCRAWLER3/ebiz/ebizpushmsgwebview.php", json=json_api, timeout=(60 * 1)).json()
            if res['responseDesc'] == 'OK':
                return jsonify({"status": "success"}), 200
            else:
                return jsonify({"status": "fail", "message": res['responseDesc']}), 400
        else:
            return jsonify({"message": "one id error"}), 500
    except Exception as e:
        print('error ===', e)
        current_app.logger.info(e)
        return jsonify(str(e))


@connect_sql()
def timeMerge2(cursor, row):
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
    # print('row',row)
    # print('times',times)
    # range(len(times)) 0,1,2,3,4  range(5)
    # for(let i=0 ; i <5 ; i++)
    # for i in range(5)
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
    # print('strTime', strTime)
    return strTime
