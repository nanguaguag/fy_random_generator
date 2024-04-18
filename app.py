from flask import Flask, session, jsonify, render_template, request
from datetime import timedelta
import sqlite3
import uuid

app = Flask(__name__, static_url_path="")
app.config["SECRET_KEY"] = "abcdefghijklmn"
app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(days=7)  # cookies在7天后过期


def id2name(table_id):
    if table_id is None or table_id == "" or table_id == "default_table":
        return "default_table"
    return f"table{table_id.strip()}"


def get_min_max(table_name):
    connection = sqlite3.connect("unique_numbers.db")
    cursor = connection.cursor()

    # 创建表格（如果不存在）
    cursor.execute(
        f"""
        CREATE TABLE IF NOT EXISTS {table_name} (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            device_id TEXT,
            -- 0: 没抽中; 1: 抽中; 2: 管理员
            status INTEGER DEFAULT 0 CHECK(status IN (0, 1, 2, 3)),
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    )

    # 执行查询
    cursor.execute(f"SELECT MIN(id), MAX(id) FROM {table_name}")
    result = cursor.fetchone()  # 获取结果
    cursor.close()  # 关闭游标
    connection.close()  # 关闭数据库连接
    return result


def get_device_id():
    if session.get("device_id") is None:
        session["device_id"] = str(uuid.uuid4())

    return session["device_id"]


def set_to_admin(table_name):
    # 连接到数据库
    # 创建一个游标对象，用于执行sql语句。
    connection = sqlite3.connect("unique_numbers.db")
    cursor = connection.cursor()
    device_id = get_device_id()  # 创建表格（如果不存在）
    cursor.execute(
        f"""
        create table if not exists {table_name} (
            id integer primary key autoincrement,
            device_id text,
            -- 0: 没抽中; 1: 抽中; 2: 管理员
            status integer default 0 check(status in (0, 1, 2, 3)),
            timestamp timestamp default current_timestamp
        )
        """
    )
    # 升为管理员
    cursor.execute(
        f"update {table_name} SET status = 2 WHERE device_id = ?", (device_id,)
    )

    connection.commit()  # 提交更改
    cursor.close()  # 关闭游标
    connection.close()  # 关闭数据库连接


def set_id_chosen(_id, table_name):
    # 连接到数据库
    # 创建一个游标对象，用于执行SQL语句。
    connection = sqlite3.connect("unique_numbers.db")
    cursor = connection.cursor()
    # device_id = get_device_id()
    # 创建表格（如果不存在）
    cursor.execute(
        f"""
        CREATE TABLE IF NOT EXISTS {table_name} (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            device_id TEXT,
            -- 0: 没抽中; 1: 抽中; 2: 管理员
            status INTEGER DEFAULT 0 CHECK(status IN (0, 1, 2, 3)),
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    # 升为管理员
    cursor.execute(f"UPDATE {table_name} SET status = 1 WHERE id = ?", (_id,))

    # 关闭数据库连接
    connection.commit()  # 提交更改
    cursor.close()  # 关闭游标
    connection.close()  # 关闭数据库连接


def get_unique_number(table_name, insert=True):
    device_id = get_device_id()
    status = 0

    # 连接到数据库
    # 创建一个游标对象，用于执行SQL语句。
    connection = sqlite3.connect("unique_numbers.db")
    cursor = connection.cursor()

    # 创建表格（如果不存在）
    cursor.execute(
        f"""
        CREATE TABLE IF NOT EXISTS {table_name} (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            device_id TEXT,
            -- 0: 没抽中; 1: 抽中; 2: 管理员
            status INTEGER DEFAULT 0 CHECK(status IN (0, 1, 2, 3)),
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    )

    # 查询设备ID是否已存在
    cursor.execute(f"SELECT id FROM {table_name} WHERE device_id = ?", (device_id,))
    device_id_exists = cursor.fetchone()

    # 只查询，不插入
    if insert == False and not device_id_exists:
        # 关闭数据库连接
        connection.commit()  # 提交更改
        cursor.close()  # 关闭游标
        connection.close()  # 关闭数据库连接
        return {"device_id": None, "count": -1, "status": -1}

    # 查询+找不到就插入
    if device_id_exists:
        # 已经存在设备ID
        device_index = device_id_exists[0]
        cursor.execute(
            f"SELECT status FROM {table_name} WHERE device_id = ?",
            (device_id,),  # 选中号码状态
        )
        status = cursor.fetchone()[0]  # 更新status: 0/1/2/3
        print(f"Device ID already exists: {table_name}")
    else:
        # 插入数据到表格
        cursor.execute(f"INSERT INTO {table_name} (device_id) VALUES (?)", (device_id,))
        device_index = cursor.lastrowid
        print(f"Device ID not found. Inserted, device_index: {device_index}")

    # 计算是第几个
    cursor.execute(f"SELECT COUNT(*) FROM {table_name} WHERE id <= ?", (device_index,))
    count = cursor.fetchone()[0]

    connection.commit()  # 提交更改
    cursor.close()  # 关闭游标
    connection.close()  # 关闭数据库连接

    return_data = {
        "device_id": device_id,
        "count": count,
        "status": status,
    }

    return return_data


@app.route("/", methods=["GET"])
def home():
    table_id = request.args.get("token")
    user_agent = request.headers.get("User-Agent", "")
    table_name = id2name(table_id)

    if "MicroMessenger" in user_agent or "WeChat" in user_agent:
        print("在微信浏览器中打开")
        data = get_unique_number(table_name)
        return render_template(
            "assign.html", your_number=data["count"], number_status=data["status"]
        )
    else:
        print("非微信浏览器")
        return render_template("deny.html")


@app.route("/wheel", methods=["GET", "POST"])
def wheel():
    table_id = request.form.get("token")  # 抽奖id
    passwd = request.form.get("passwd")  # 管理员密码
    # "0": "登陆成功！",
    # "1": "密码错误！",
    # "2": "请填写密码",
    # "3": "未知错误！",
    if passwd == None or passwd == "":
        print("密码为空")
        return render_template("auth.html", auth_code=2)
    elif passwd == "fyscu2023":
        print("密码正确。")
        return render_template("wheel.html", token=table_id)
    elif passwd is not None:
        print("密码错误：", passwd)
        return render_template("auth.html", auth_code=1)

    return render_template("auth.html", auth_code=3)


@app.route("/api/choose", methods=["POST"])
def choose():
    data = request.get_json()
    number = int(data["number"])
    table_name = id2name(data["token"])

    try:
        min_num, _ = get_min_max(table_name)
        if min_num is None:
            return jsonify(code=-2, msg="Table not found.")
        set_id_chosen(min_num + number - 1, table_name)
        return jsonify(code=0, msg="OK")
    except ValueError as e:
        return jsonify(code=-1, msg=e)


@app.route("/api/getCount", methods=["GET"])
def getCount():
    table_id = request.args.get("token")
    print("table_id:", table_id)
    table_name = id2name(table_id)
    min_num, max_num = get_min_max(table_name)
    if min_num is None or max_num is None:
        return jsonify(count=0, msg="Table not found.")

    return jsonify(count=max_num - min_num + 1, msg="OK")


@app.route("/api/getNumber", methods=["GET"])
def getNumber():
    table_id = request.args.get("token")
    table_name = id2name(table_id)
    return jsonify(get_unique_number(table_name, insert=False))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)
    # from gevent import pywsgi
    # server = pywsgi.WSGIServer(('0.0.0.0', 5001), app)
    # server.serve_forever()
