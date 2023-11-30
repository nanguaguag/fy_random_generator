from datetime import timedelta
from flask import Flask, session, jsonify, render_template
import sqlite3
import uuid
import json

app = Flask(__name__)
app.config['SECRET_KEY'] = "abcdefghijklmn"
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=7)  # cookies在7天后过期


def get_unique_number():
    if session.get("device_id") is None:
        session['device_id'] = str(uuid.uuid4())

    device_id = session['device_id']
    print(device_id)

    # 连接到数据库
    # 创建一个游标对象，用于执行SQL语句。
    conn = sqlite3.connect('unique_numbers.db')
    cursor = conn.cursor()

    # 创建表格（如果不存在）
    cursor.execute(
        '''
        CREATE TABLE IF NOT EXISTS unique_numbers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            device_id TEXT,
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
        print(f'Device ID already exists.')
    else:
        # 插入数据到表格
        cursor.execute(
            "INSERT INTO unique_numbers (device_id) VALUES (?)", (device_id,)
        )
        device_index = cursor.lastrowid
        print('Device ID not found. Inserted.')

    # 计算是第几个
    cursor.execute(
        "SELECT COUNT(*) FROM unique_numbers WHERE id <= ?", (device_index,)
    )
    counter = cursor.fetchone()[0]

    # 关闭数据库连接
    conn.commit()  # 提交更改
    cursor.close()  # 关闭游标
    conn.close()  # 关闭数据库连接

    return_data = {
        "uuid": device_id,
        "count": counter
    }

    return return_data


@app.route('/', methods=['GET'])
def home():
    your_number = get_unique_number()["count"]
    return render_template("index.html", your_number=your_number)


@app.route('/getNumber', methods=['GET'])
def getNumber():
    return jsonify(get_unique_number())


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)
