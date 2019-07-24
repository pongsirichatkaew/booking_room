from Config.config import *

# -----------------------login---------------------------------every User -c
@app.route('/api/v2/login', methods=['POST'])
@connect_sql()
def test_login(cursor):
    try:
        if not request.is_json:
            return jsonify({"msg": "Missing JSON in request"}), 400
        else:
            username = request.json.get('username', None)
            password = request.json.get('password', None)
            if not username or not password:
                return jsonify({"msg": "Missing parameter"}), 400
            else:
                r = requests.get('http://hr.devops.inet.co.th:9999/api/v1/login/'+username+'/' +
                                 password, headers={'Authorization': 'd0aa5a1d-a58b-4a45-9c99-1e1007408ef4'})
                if r:
                    raw = r.text
                    raw = json.loads(raw)
                    sql = "SELECT role FROM user WHERE userid = %s"
                    if cursor.execute(sql, (raw['userid'])):
                        columns = [column[0] for column in cursor.description]
                        result = toJson(cursor.fetchall(), columns)
                        raw.update(result[0])
                        return jsonify(raw), 200
                    else:
                        sql = """INSERT INTO `user`(name,lastname,userid,email) VALUES (%s,%s,%s,%s)"""
                        cursor.execute(
                            sql, (raw['name'], raw['lastname'], raw['userid'], username))
                        raw.update({"role": 1})
                        return jsonify(raw), 200
                else:
                    return jsonify({"msg": "not have user"}), 401
    except Exception as e:
        print('error ===', e)
        current_app.logger.info(e)
        return jsonify(str(e))
# ----------------------------- Show Admin ---------------------------User Level 2&3 -c
@app.route('/api/v2/show_admin', methods=["POST"])
@connect_sql()
def show_admin(cursor):
    try:
        if not request.is_json:
            return jsonify({"msg": "Missing JSON in request"}), 400
        else:
            user_id = request.json.get('user_id', None)
            if not user_id:
                return jsonify({"msg": "Missing parameter"}), 400
            else:
                sql = """SELECT role FROM user WHERE userid = %s"""
                cursor.execute(sql, (user_id))
                role = toJson(cursor.fetchall(), 'i')
                print("SSS--------------", role[0]['i'])
                if role[0]['i'] == 1:
                    print("hh1")
                    return jsonify({"msg": "you cant access to this data"}), 401
                elif role[0]['i'] == 2 or role[0]['i'] == 3:
                    print("hhh2")
                    sql = """SELECT userid , role FROM user where role <= %s and role > 1"""
                    cursor.execute(sql, (role[0]['i']))
                    columns = [column[0] for column in cursor.description]
                    result = toJson(cursor.fetchall(), columns)
                    print(result)
                    arr = []
                    for x in result:
                        r = requests.get('http://hr.devops.inet.co.th:9999/api/v1/employee/'+x['userid'], headers={
                                         'Authorization': 'd0aa5a1d-a58b-4a45-9c99-1e1007408ef4'})
                        if r:
                            raw = r.text
                            raw = json.loads(raw)
                            data = {
                                "role": x['role'],
                                "code": raw['employee_detail'][0]['code'],
                                "thainame":  raw['employee_detail'][0]['thainame'],
                                "thlastname":  raw['employee_detail'][0]['thlastname'],
                                "engname": raw['employee_detail'][0]['engname'],
                                "englastname": raw['employee_detail'][0]['englastname'],
                                "email": raw['employee_detail'][0]['email'],
                                "phonenumber": raw['employee_detail'][0]['phonenumber'],
                                "positionname": raw['employee_detail'][0]['positionname'],
                            }
                            arr.append(data)

                        else:
                            continue
                    return jsonify({"msg": arr})
                else:
                    print('H23')
                    return jsonify({"msg": "invalid user id"})

    except Exception as e:
        print('error ===', e)
        current_app.logger.info(e)
        return jsonify(str(e))

# ----------------------------- Add Admin ---------------------------User Level 2&3 -c
@app.route('/api/v2/add_admin', methods=["POST"])
@connect_sql()
def add_admin(cursor):
    try:
        if not request.is_json:
            return jsonify({"msg": "Missing JSON in request"}), 400
        else:
            user_id = request.json.get('user_id', None)
            user_id_add = request.json.get('user_id_add', None)
            role_user = request.json.get('role', None)
            if not user_id or not role_user or not user_id_add:
                return jsonify({"msg": "Missing parameter"}), 400
            else:
                sql = """SELECT role FROM user WHERE userid = %s"""
                cursor.execute(sql, (user_id))
                role = toJson(cursor.fetchall(), 'i')
                print("SSS--------------", role[0]['i'])
                if role[0]['i'] == 1:
                    print("hh1")
                    return jsonify({"msg": "you cant add to this data"}), 401
                elif role[0]['i'] == 2:
                    if role_user == "3":
                        return jsonify({"msg": "you cant add to this data"}), 401
                    else:
                        r = requests.get('http://hr.devops.inet.co.th:9999/api/v1/employee/'+user_id_add, headers={
                                         'Authorization': 'd0aa5a1d-a58b-4a45-9c99-1e1007408ef4'})
                        raw = r.text
                        raw = json.loads(raw)
                        if 'message' in raw:
                            return jsonify({"msg": "user not in scrope"}), 401
                        else:
                            sql = """SELECT role FROM user WHERE userid=%s"""
                            cursor.execute(sql, (user_id_add))
                            inrole = toJson(cursor.fetchall(), 'i')
                            print('inrole',inrole)
                            if inrole:
                                if inrole[0]['i'] == 3:
                                    return jsonify({"msg": "ผู้ใช้ต้องมีสิทธิ์ในระดับผู้ดูแลระบบ"}), 401
                                elif inrole[0]['i'] == 2:
                                    return jsonify({"msg": "สิทธิ์การจัดการไม่ถูกต้อง"}), 401
                                elif inrole[0]['i'] == 1:
                                    user = raw['employee_detail'][0]
                                    sql = """UPDATE user SET role = %s WHERE userid =%s"""
                                    cursor.execute(
                                        sql, (role_user, user['code']))
                                    return jsonify({"msg": "success"})
                            else:
                                user = raw['employee_detail'][0]
                                sql = """INSERT INTO `user`(role,name,lastname,userid) VALUES (%s,%s,%s,%s)"""
                                cursor.execute(
                                    sql, (role_user, user['engname'], user['englastname'], user['code']))
                                return jsonify({"msg": "success"})
                elif role[0]['i'] == 3:
                    r = requests.get('http://hr.devops.inet.co.th:9999/api/v1/employee/'+user_id_add,
                                     headers={'Authorization': 'd0aa5a1d-a58b-4a45-9c99-1e1007408ef4'})
                    raw = r.text
                    raw = json.loads(raw)
                    if 'message' in raw:
                        return jsonify({"msg": "user not in scrope"}), 401
                    else:
                        sql = """SELECT role FROM user WHERE userid=%s"""
                        cursor.execute(sql, (user_id_add))
                        inrole = toJson(cursor.fetchall(), 'i')
                        if inrole:
                            user = raw['employee_detail'][0]
                            sql = """UPDATE `user` SET role = %s WHERE userid =%s"""
                            cursor.execute(sql, (role_user, user['code']))
                            return jsonify({"msg": "success"})
                        else:
                            user = raw['employee_detail'][0]
                            sql = """INSERT INTO `user`(role,name,lastname,userid) VALUES (%s,%s,%s,%s)"""
                            cursor.execute(
                                sql, (role_user, user['engname'], user['englastname'], user['code']))
                            return jsonify({"msg": "success"})
                else:
                    print('H23')
                    return jsonify({"msg": "invalid user id"})
    except Exception as e:
        print('error ===', e)
        current_app.logger.info(e)
        return jsonify(str(e))
# ---------------------menu------------------------------------------every User -c
@app.route('/api/v2/menu', methods=["POST"])
@connect_sql()
def menu(cursor):
    try:
        if not request.is_json:
            return jsonify({"msg": "Missing JSON in request"}), 400
        else:
            user_id = request.json.get('user_id', None)
            if not user_id:
                return jsonify({"msg": "Missing parameter"}), 400
            else:
                sql = """SELECT role FROM user WHERE userid = %s """
                cursor.execute(sql, (user_id))
                role = toJson(cursor.fetchall(), 'i')
                print("SSS--------------", len(role))
                if len(role) == 0:
                    print('H23')
                    return "NOT"
                elif role[0]['i'] == 1:
                    print("hh1")
                    sql = """SELECT * FROM debt WHERE id_user = %s and status != 'สิ้นสุด'"""
                    cursor.execute(sql, (user_id))
                    columns = [column[0] for column in cursor.description]
                    result = toJson(cursor.fetchall(), columns)
                    return jsonify(result)
                elif role[0]['i'] == 2 or role[0]['i'] == 3:
                    print("hhh2")
                    sql = """SELECT * FROM debt WHERE status !='สิ้นสุด'"""
                    cursor.execute(sql)
                    columns = [column[0] for column in cursor.description]
                    result = toJson(cursor.fetchall(), columns)
                    return jsonify(result)

    except Exception as e:
        print('error ===', e)
        current_app.logger.info(e)
        return jsonify(str(e))
# ----------------------create from----------------------------------user Lv1 -C
@app.route('/api/v2/create', methods=["POST"])
@connect_sql()
def create(cursor):
    try:
        if not request.is_json:
            return jsonify({"msg": "Missing JSON in request"}), 400
        else:
            id_user = request.json.get('id_user', None)  # 1  Y
            id_from = request.json.get('id_from', None)  # 2  Y
            status = "รออนุมัติ"  # 3  N
            create_at = request.json.get('create_at', None)  # 4  Y

            id_customer = request.json.get('id_customer', None)  # 5  Y
            customer_name = request.json.get('customer_name', None)  # 6  Y
            invoice_no = request.json.get('invoice_no', None)  # 7  Y
            ref_so = request.json.get('ref_so', None)  # 8  Y
            amount_no_vat = request.json.get('amount_no_vat', None)  # 9  Y
            service = request.json.get('service', None)  # 10 Y
            from_year = request.json.get('from_year', None)  # 11 Y
            from_month = request.json.get('from_month', None)  # 12 Y
            to_year = request.json.get('to_year', None)  # 13 Y
            to_month = request.json.get('to_month', None)  # 14 Y
            change_income = request.json.get('change_income', None)  # 15 Y
            full = request.json.get('full', None)  # 16 Y
            full_text = request.json.get('full_text', None)  # 17 Y
            some = request.json.get('some', None)  # 18 Y
            some_text = request.json.get('some_text', None)  # 19 Y
            not_change_income = request.json.get(
                'not_change_income', None)  # 20 Y
            other = request.json.get('other', None)  # 21 Y
            other_text = request.json.get('other_text', None)  # 22 Y
            debt_text = request.json.get('debt_text', None)  # 23 Y
            edit_status = '1'  # 24
            if not id_user or not create_at or not id_from or not id_customer or not customer_name or not invoice_no or not ref_so or not amount_no_vat or not service or not from_year or not from_month or not to_year or not to_month or not debt_text:
                return jsonify({"msg": "Missing parameter"}), 400
            else:
                sql = """SELECT role FROM user WHERE userid = %s"""
                cursor.execute(sql, (id_user))
                role = toJson(cursor.fetchall(), 'i')
                if role:
                    sql = """INSERT INTO `debt` (`id`, `id_user`, `id_from`, `status`, `approved_by`, `create_at`, `edit_at`, `comment`, `id_customer`, `customer_name`, `invoice_no`, `ref_so`, `amount_no_vat`, `service`, `from_year`, `from_month`, `to_year`, `to_month`, `change_income`, `full`, `full_text`, `some`, `some_text`, `not_change_income`, `other`, `other_text`, `debt_text`, `edit_status`) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"""
                    cursor.execute(sql, (None, id_user, id_from, status, None, create_at, None, None, id_customer, customer_name, invoice_no, ref_so, amount_no_vat, service,
                                         from_year, from_month, to_year, to_month, change_income, full, full_text, some, some_text, not_change_income, other, other_text, debt_text, edit_status))
                    print("SSS--------------")
                    return jsonify("ss")
                else:
                    return jsonify("nss")
    except Exception as e:
        print('error ===', e)
        current_app.logger.info(e)
        return jsonify(str(e))

# ----------------------edit from----------------------------------user Lv1
@app.route('/api/v2/edit', methods=["POST"])
@connect_sql()
def edit(cursor):
    try:
        if not request.is_json:
            return jsonify({"msg": "Missing JSON in request"}), 400
        else:
            old_id_from = request.json.get('old_id_from', None)
            id_user = request.json.get('id_user', None)  # 1  Y
            id_from = request.json.get('id_from', None)  # 2  Y
            status = 'รออนุมัติ'  # 3  Y
            create_at = request.json.get('create_at', None)  # 4  Y

            id_customer = request.json.get('id_customer', None)  # 5  Y
            customer_name = request.json.get('customer_name', None)  # 6  Y
            invoice_no = request.json.get('invoice_no', None)  # 7  Y
            ref_so = request.json.get('ref_so', None)  # 8  Y
            amount_no_vat = request.json.get('amount_no_vat', None)  # 9  Y
            service = request.json.get('service', None)  # 10 Y
            from_year = request.json.get('from_year', None)  # 11 Y
            from_month = request.json.get('from_month', None)  # 12 Y
            to_year = request.json.get('to_year', None)  # 13 Y
            to_month = request.json.get('to_month', None)  # 14 Y
            change_income = request.json.get('change_income', None)  # 15 Y
            full = request.json.get('full', None)  # 16 Y
            full_text = request.json.get('full_text', None)  # 17 Y
            some = request.json.get('some', None)  # 18 Y
            some_text = request.json.get('some_text', None)  # 19 Y
            not_change_income = request.json.get(
                'not_change_income', None)  # 20 Y
            other = request.json.get('other', None)  # 21 Y
            other_text = request.json.get('other_text', None)  # 22 Y
            debt_text = request.json.get('debt_text', None)  # 23 Y
            edit_status = '1'  # 24
            if not id_user or not create_at or not id_from or not id_customer or not customer_name or not invoice_no or not ref_so or not amount_no_vat or not service or not from_year or not from_month or not to_year or not to_month or not debt_text:
                return jsonify({"msg": "Missing parameter"}), 400
            else:
                sql = """SELECT role FROM user WHERE userid = %s"""
                cursor.execute(sql, (id_user))
                role = toJson(cursor.fetchall(), 'i')
                print('id_from',  id_from)
                if role[0]['i'] == 1:
                    sql = """UPDATE `debt` SET edit_status = '0',status = 'สิ้นสุด' WHERE id_from = %s and edit_status = '1'"""
                    cursor.execute(sql, (old_id_from))
                    sql = """INSERT INTO `debt` (`id`, `id_user`, `id_from`, `status`, `approved_by`, `create_at`, `edit_at`, `comment`, `id_customer`, `customer_name`, `invoice_no`, `ref_so`, `amount_no_vat`, `service`, `from_year`, `from_month`, `to_year`, `to_month`, `change_income`, `full`, `full_text`, `some`, `some_text`, `not_change_income`, `other`, `other_text`, `debt_text`, `edit_status`) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"""
                    cursor.execute(sql, (None, id_user, id_from, status, None, create_at, None, None, id_customer, customer_name, invoice_no, ref_so, amount_no_vat, service,
                                         from_year, from_month, to_year, to_month, change_income, full, full_text, some, some_text, not_change_income, other, other_text, debt_text, edit_status))
                    print("SSS--------------")
                    return jsonify("ss")
                else:
                    return jsonify("nss")
    except Exception as e:
        print('error ===', e)
        current_app.logger.info(e)
        return jsonify(str(e))
# # ----------------------------approve from--------------------------
@app.route('/api/v2/approve', methods=["POST"])
@connect_sql()
def approve(cursor):
    try:
        if not request.is_json:
            return jsonify({"msg": "Missing JSON in request"}), 400
        else:
            status = request.json.get('status', None)
            id_from = request.json.get('id_from', None)
            edit_at = request.json.get('edit_at', None)
            id_user = request.json.get('id_user', None)
            comment = request.json.get('comment', None)
            sql = """SELECT role FROM user WHERE userid = %s"""
            cursor.execute(sql, (id_user))
            role = toJson(cursor.fetchall(), 'i')
            if role[0]['i'] == 2 or role[0]['i'] == 3:
                sql = """UPDATE `debt` SET status = %s,approved_by = %s,edit_at = %s,comment = %s WHERE id_from = %s and status ='รออนุมัติ'"""
                cursor.execute(
                    sql, (status, id_user, edit_at, comment, id_from))
                return jsonify("SS")
            else:
                return jsonify("wrong id"), 401
    except Exception as e:
        print('error ===', e)
        current_app.logger.info(e)
        return jsonify(str(e))
# ----------------------------confirm from--------------------------
@app.route('/api/v2/confirm', methods=["POST"])
@connect_sql()
def confirm(cursor):
    try:
        if not request.is_json:
            return jsonify({"msg": "Missing JSON in request"}), 400
        else:
            id_from = request.json.get('id_from', None)
            id_user = request.json.get('id_user', None)
            password = request.json.get('password', None)
            
            if not id_from or not id_user or not password :
                return jsonify({"msg": "Missing parameter"}), 400
            else:
                sql = """SELECT role FROM user WHERE userid = %s"""
                cursor.execute(sql, (id_user))
                role = toJson(cursor.fetchall(), 'i')
                if role[0]['i'] == 2 or role[0]['i'] == 3:
                    sql = """SELECT id_from FROM debt  WHERE id_from = %s and id_user =%s and edit_status = '1'"""
                    cursor.execute(sql,(id_from,password))
                    id_from2 = toJson(cursor.fetchall(), 'i')
                    if id_from2:
                        sql = """UPDATE `debt` SET status = 'สิ้นสุด',edit_status = '0' WHERE id_from = %s"""
                        cursor.execute(sql, (id_from))
                        return jsonify("SS")
                    else:
                        return jsonify("wrong password"), 401
                else:
                    return jsonify("wrong id"), 401
    except Exception as e:
        print('error ===', e)
        current_app.logger.info(e)
        return jsonify(str(e))
# --------------------------------------------------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------------------------------------------------
