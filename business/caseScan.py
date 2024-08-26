import requests
from copy import deepcopy

import re
import json
from variable import DIR
from common.logsMethod import info, error

with open(file=DIR + '/data/sqlInjectDb.txt', mode='r', encoding='utf-8') as f:
    attack_datas = f.readlines()
with open(file=DIR + '/data/api_checkDB.txt', mode='r', encoding='utf-8') as f:
    mysql_sensitive = f.readlines()


def response_list_len_load(response):
    for k, v in response.items():
        if isinstance(v, list):
            if len(v) > 1:
                return False
            if isinstance(v[0], dict):
                response_list_len_load(v[0])
        elif isinstance(v, dict):
            response_list_len_load(v)
    return True


def mysql_sensitive_check(response):
    for line in mysql_sensitive:
        if line.strip() in response:
            return False
    return True


def sql_injection(load_apis):
    scan_res = []

    for api in load_apis:
        if 'params' in api and 'body' in api:
            for key in api['params']:
                for attack in attack_datas:
                    fail_res = deepcopy(api)
                    d_request = deepcopy(api)
                    d_request['params'][key] = attack
                    res = requests.request(method=api['method'], url=api['url'], headers=api['headers'],
                                           json=d_request['body'],
                                           params=d_request['params'])
                    fail_res['attach_action'] = d_request
                    fail_res['status_code'] = res.status_code
                    fail_res['response'] = res.text

                    info(f'requests: {json.dumps(d_request)}')
                    info(f'code: {res.status_code}')
                    info(f'response: {res.text}')
                    if 'html' in res.text:
                        scan_res.append(fail_res)
                    elif not mysql_sensitive_check(res.text):
                        scan_res.append(fail_res)
                    elif not response_list_len_load(res.json()):
                        scan_res.append(fail_res)
            for key in api['body']:
                for attack in attack_datas:
                    fail_res = deepcopy(api)
                    d_request = deepcopy(api)
                    d_request['body'][key] = attack
                    res = requests.request(method=api['method'], url=api['url'], headers=api['headers'],
                                           json=d_request['body'],
                                           params=d_request['params'])
                    fail_res['attach_action'] = d_request
                    fail_res['status_code'] = res.status_code
                    fail_res['response'] = res.text

                    info(f'requests: {json.dumps(d_request)}')
                    info(f'code: {res.status_code}')
                    info(f'response: {res.text}')
                    if 'html' in res.text:
                        scan_res.append(fail_res)
                    elif not mysql_sensitive_check(res.text):
                        scan_res.append(fail_res)
                    elif not response_list_len_load(res.json()):
                        scan_res.append(fail_res)
        elif 'params' in api and 'body' not in api:
            for key in api['params']:
                for attack in attack_datas:
                    fail_res = deepcopy(api)
                    d_request = deepcopy(api)
                    d_request['params'][key] = attack
                    res = requests.request(method=api['method'], url=api['url'], headers=api['headers'],
                                           params=d_request['params'])
                    fail_res['attach_action'] = d_request
                    fail_res['status_code'] = res.status_code
                    fail_res['response'] = res.text

                    info(f'requests: {json.dumps(d_request)}')
                    info(f'code: {res.status_code}')
                    info(f'response: {res.text}')
                    if 'html' in res.text:
                        scan_res.append(fail_res)
                    elif not mysql_sensitive_check(res.text):
                        scan_res.append(fail_res)
                    elif not response_list_len_load(res.json()):
                        scan_res.append(fail_res)
        elif 'params' not in api and 'body' in api:
            for key in api['body']:
                for attack in attack_datas:
                    fail_res = deepcopy(api)
                    d_request = deepcopy(api)
                    d_request['body'][key] = attack
                    res = requests.request(method=api['method'], url=api['url'], headers=api['headers'],
                                           json=d_request['body'])
                    fail_res['attach_action'] = d_request
                    fail_res['status_code'] = res.status_code
                    fail_res['response'] = res.text

                    info(f'requests: {json.dumps(d_request)}')
                    info(f'code: {res.status_code}')
                    info(f'response: {res.text}')
                    if 'html' in res.text:
                        scan_res.append(fail_res)
                    elif not mysql_sensitive_check(res.text):
                        scan_res.append(fail_res)
                    elif not response_list_len_load(res.json()):
                        scan_res.append(fail_res)

        else:
            pass
    return scan_res


def dict_mgc_check(data):
    scan_res = []
    for k, v in data.items():
        if isinstance(v, str):
            if v.isdigit():
                # 手机号判断
                pattern = re.compile(r'^1[3-9]\d{9}$')
                if pattern.match(v):
                    scan_res.append({"key": k, "value": v, "error": "手机号敏感词"})
                # 其他敏感词的检测逻辑
        elif isinstance(v, int):
            # 手机号判断
            pattern = re.compile(r'^1[3-9]\d{9}$')
            if pattern.match(str(v)):
                scan_res.append({"key": k, "value": v, "error": "手机号敏感词"})
        elif isinstance(v, list):
            if len(v) > 0:
                if isinstance(v[0], dict):
                    son_res = dict_mgc_check(v[0])
                    scan_res.append({son_res})

    return scan_res


if __name__ == '__main__':
    t_load_apis = [
        {
            'url': 'http://127.0.0.1:9676/aa',
            'method': 'post',
            'body': {'q_id': '123'},
            'headers': {}
        }
    ]
    import json

    print(json.dumps(sql_injection(t_load_apis)))
