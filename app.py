from flask import session, jsonify, render_template, request
import sqlite3
import uuid
import json
from __init__ import *


def get_min_max():
    connection = sqlite3.connect('unique_numbers.db')
    cursor = connection.cursor()
    device_id = get_device_id()

    # 创建表格（如果不存在）
    cursor.execute(
        '''
        CREATE TABLE IF NOT EXISTS unique_numbers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            device_id TEXT,
            -- 0: 没抽中; 1: 抽中; 2: 管理员
            status INTEGER DEFAULT 0 CHECK(status IN (0, 1, 2, 3)),
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        '''
    )

    # 执行查询
    cursor.execute("SELECT MIN(id), MAX(id) FROM unique_numbers")

    # 获取结果
    result = cursor.fetchone()

    # 关闭数据库连接
    cursor.close()
    connection.close()

    return result


def get_device_id():
    if session.get("device_id") is None:
        session['device_id'] = str(uuid.uuid4())

    return session['device_id']


def set_to_admin():
    # 连接到数据库
    # 创建一个游标对象，用于执行SQL语句。
    connection = sqlite3.connect('unique_numbers.db')
    cursor = connection.cursor()
    device_id = get_device_id()
    # 创建表格（如果不存在）
    cursor.execute(
        '''
        CREATE TABLE IF NOT EXISTS unique_numbers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            device_id TEXT,
            -- 0: 没抽中; 1: 抽中; 2: 管理员
            status INTEGER DEFAULT 0 CHECK(status IN (0, 1, 2, 3)),
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        '''
    )
    # 升为管理员
    cursor.execute(
        "UPDATE unique_numbers SET status = 2 WHERE device_id = ?", (
            device_id,)
    )

    # 关闭数据库连接
    connection.commit()  # 提交更改
    cursor.close()  # 关闭游标
    connection.close()  # 关闭数据库连接


def set_id_chosen(_id):
    # 连接到数据库
    # 创建一个游标对象，用于执行SQL语句。
    connection = sqlite3.connect('unique_numbers.db')
    cursor = connection.cursor()
    device_id = get_device_id()
    # 创建表格（如果不存在）
    cursor.execute(
        '''
        CREATE TABLE IF NOT EXISTS unique_numbers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            device_id TEXT,
            -- 0: 没抽中; 1: 抽中; 2: 管理员
            status INTEGER DEFAULT 0 CHECK(status IN (0, 1, 2, 3)),
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        '''
    )
    # 升为管理员
    cursor.execute(
        "UPDATE unique_numbers SET status = 1 WHERE id = ?", (_id,)
    )

    # 关闭数据库连接
    connection.commit()  # 提交更改
    cursor.close()  # 关闭游标
    connection.close()  # 关闭数据库连接


def get_unique_number():
    device_id = get_device_id()
    status = 0

    # 连接到数据库
    # 创建一个游标对象，用于执行SQL语句。
    connection = sqlite3.connect('unique_numbers.db')
    cursor = connection.cursor()

    # 创建表格（如果不存在）
    cursor.execute(
        '''
        CREATE TABLE IF NOT EXISTS unique_numbers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            device_id TEXT,
            -- 0: 没抽中; 1: 抽中; 2: 管理员
            status INTEGER DEFAULT 0 CHECK(status IN (0, 1, 2, 3)),
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        '''
    )

    # 查询设备ID是否已存在
    cursor.execute(
        "SELECT id FROM unique_numbers WHERE device_id = ?", (device_id,)
    )
    device_id_exists = cursor.fetchone()

    if device_id_exists:
        # 已经存在设备ID
        device_index = device_id_exists[0]
        cursor.execute(
            "SELECT status FROM unique_numbers WHERE device_id = ?", (
                device_id,)  # 选中号码状态
        )
        status = cursor.fetchone()[0]  # 更新status: 0/1/2/3
        print(f'Device ID already exists:', device_id)
    else:
        # 插入数据到表格
        cursor.execute(
            "INSERT INTO unique_numbers (device_id) VALUES (?)", (device_id,)
        )
        device_index = cursor.lastrowid
        print('Device ID not found. Inserted, device_index:', device_index)

    # 计算是第几个
    cursor.execute(
        "SELECT COUNT(*) FROM unique_numbers WHERE id <= ?", (device_index,)
    )
    count = cursor.fetchone()[0]

    # 关闭数据库连接
    connection.commit()  # 提交更改
    cursor.close()  # 关闭游标
    connection.close()  # 关闭数据库连接

    return_data = {
        "device_id": device_id,
        "count": count,
        "status": status,
        # "status": 1
    }

    return return_data


@app.route('/', methods=['GET'])
def home():
    data = get_unique_number()
    return render_template(
        "assign.html",
        your_number=data["count"],
        number_status=data["status"]
    )


@app.route('/wheel', methods=['GET', 'POST'])
def wheel():
    passwd = request.form.get("passwd")  # 管理员密码
    # "0": "登陆成功！",
    # "1": "密码错误！",
    # "2": "请填写密码",
    # "3": "未知错误！",
    if passwd == "":
        print("密码为空")
        return render_template("auth.html", auth_code=2)
    elif passwd == "fyscu2023":
        print("密码正确。")
        set_to_admin()
    elif passwd is not None:
        print("密码错误：", passwd)
        return render_template("auth.html", auth_code=1)

    # GET请求
    data = get_unique_number()
    if data["status"] != 2:  # 不是管理员
        return render_template("auth.html")
    else:
        min_num, max_num = get_min_max()
        print(min_num, max_num)
        return render_template("wheel.html", count=max_num - min_num + 1)

    return render_template("auth.html", auth_code=3)


@app.route('/api/choose', methods=['POST'])
def choose():
    data = request.get_json()
    number = data['number']
    try:
        number = int(number)
        min_num, _ = get_min_max()
        set_id_chosen(min_num + number - 1)
        return jsonify(code=0, msg="OK")
    except ValueError as e:
        return jsonify(code=-1, msg=e)


@app.route('/api/getNumber', methods=['GET'])
def getNumber():
    return jsonify(get_unique_number())


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)
    # from gevent import pywsgi
    # server = pywsgi.WSGIServer(('0.0.0.0', 5001), app)
    server.serve_forever()
