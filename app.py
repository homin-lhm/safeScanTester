from flask import Flask, request, jsonify
from copy import deepcopy
import jsonschema
import json
import uuid
from common.readYaml import read_yaml
import werkzeug.exceptions
from common.loadSwagger import read_swagger_yaml
import requests
from business.caseScan import sql_injection
from threading import Thread
from dbutils.pooled_db import PooledDB
import pymysql
from business.caseScan import dict_mgc_check
from variable import DIR

app = Flask(__name__)

# 定义数据库连接池
pool = PooledDB(
    creator=pymysql,
    maxconnections=100,  # 连接池中最大连接数
    mincached=10,  # 初始化时连接池中的连接数
    maxcached=100,  # 连接池中最多保留的连接数
    blocking=False,  # 当连接池中没有可用连接时是否阻塞等待 True 就会等待
    maxusage=None,  # 一个连接最多被使用的次数，None 表示无限制
    autocommit=True,  # 都会自动提交事务
    setsession=[],  # 在连接中执行的 sql 命令
    maxshared=1,
    ping=0,  # ping 数据库服务器的时间间隔，0 表示不 ping
    host='134.1xx.1xx.xxx',
    port=3306,
    user='root',
    password='xxxx.',
    database='apiSafeScan',
    charset='utf8mb4'
)

strategy_config = read_yaml(DIR + '\\config\\strategy_config.yml')


@app.route('/scan', methods=['post'])
def create_scan():
    """
    新建扫描任务的路由
    content-type form-data:file（yaml后缀文件）
    :return:
    """
    try:
        file = request.files['file']  # 获取上传的文件对象
    except werkzeug.exceptions.BadRequestKeyError:
        return jsonify({'msg': 'send file error', "status": False}), 400

    if file.filename.split('.')[1] not in ['yaml', 'yml']:  # 文件后缀校验
        return jsonify({'msg': 'file extension error', "status": False}), 400

    load_apis = read_swagger_yaml(file)  # 解析文件内容，提取所有接口请求信息

    requests_fail = []
    mgc_fail = []

    # 基准测试，确保文件提供的接口请求信息是有效的
    for api in load_apis:
        if 'params' in api:
            if 'body' in api:
                if dict_mgc_check(api['body']):
                    mgc_fail.append(dict_mgc_check(api['body']))
                if dict_mgc_check(api['params']):
                    mgc_fail.append(dict_mgc_check(api['body']))
                res = requests.request(method=api['method'], url=api['url'], headers=api['headers'], json=api['body'],
                                       params=api['params'])
                if dict_mgc_check(res.json()):
                    mgc_fail.append(dict_mgc_check(api['body']))
            else:
                res = requests.request(method=api['method'], url=api['url'], headers=api['headers'],
                                       params=api['params'])
        else:
            if 'body' in api:
                res = requests.request(method=api['method'], url=api['url'], headers=api['headers'], json=api['body'])
            else:
                res = requests.request(method=api['method'], url=api['url'], headers=api['headers'])
        if res.status_code != 200:
            api['status_code'] = res.status_code
            api['response'] = res.text
            requests_fail.append(api)

    if requests_fail:  # 如果存在接口请求状态码不等于200，说明基准测试没通过，直接结束扫描任务
        return jsonify({'msg': 'api info error', 'error_api': requests_fail, "status": False}), 403

    def case_scan(u_scan_id, l_apis):
        """扫描策略的定义"""
        conn = pool.connection()  # 数据库的连接对象
        cursor = conn.cursor()  # 游标

        sql = 'insert into status(scan_id, status) values (%s, %s)'
        val = (u_scan_id, 'scanning')
        cursor.execute(sql, val)
        conn.commit()
        scan_res = []

        if strategy_config['sqlInjection']:
            # sql注入的检测
            for item in sql_injection(l_apis):
                scan_res.append(item)

        sql = 'update status set status = %s where scan_id = %s'
        val = ('scan end', u_scan_id)
        cursor.execute(sql, val)
        conn.commit()

        if not scan_res:
            result = True
        else:
            result = False
        strategy_status = []
        for k, v in strategy_config.items():
            if v:
                strategy_status.append(k)

        sql = 'insert into results(scan_id, result, status, scan_strategy, fail_data) values (%s, %s, %s, %s, %s)'
        val = (u_scan_id, result, 'scan end', json.dumps(strategy_status), json.dumps(scan_res))
        cursor.execute(sql, val)
        conn.commit()
        cursor.close()
        conn.close()

    scan_id = str(uuid.uuid4())

    t = Thread(target=case_scan, args=(scan_id, load_apis))
    t.start()

    return jsonify({"scan_id": scan_id, "status": True}), 200


def query_scan():
    pass


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=9988, debug=True)
    pass
