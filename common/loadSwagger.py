import yaml


#
# def read_swagger_yaml(file_path):
#     with open(file_path, 'r') as file:
#         data = yaml.safe_load(file)
#
#     # 假设我们只对paths感兴趣
#     paths = data.get('paths', {})
#     for path, path_item in paths.items():
#         for method, operation in path_item.items():
#             print(f"Path: {path}, Method: {method}")
#
#             # 获取summary（如果有）
#             summary = operation.get('summary', 'No summary provided')
#             print(f"  Summary: {summary}")
#
#             # 获取parameters（如果有）
#             parameters = operation.get('parameters', [])
#             for parameter in parameters:
#                 param_name = parameter.get('name')
#                 param_in = parameter.get('in', 'unknown')
#                 print(f"  Parameter: {param_name}, In: {param_in}")
#                 # 你还可以访问其他parameter属性，如required, schema等
#
#             # 获取requestBody（如果有）
#             request_body = operation.get('requestBody')
#             if request_body:
#                 content = request_body.get('content')
#                 if content:
#                     for media_type, body_info in content.items():
#                         print(f"  Request Body: {media_type}")
#                         # 你可以访问body_info中的其他键，如schema
#
#             # 获取responses（如果有）
#             responses = operation.get('responses', {})
#             for status_code, response in responses.items():
#                 print(f"  Response {status_code}:")
#                 description = response.get('description', 'No description provided')
#                 print(f"    Description: {description}")
#                 # 你可以访问response中的其他键，如content


def find_schema_by_ref(data, ref):
    """
    根据$ref引用在OpenAPI数据中查找schema
    """
    ref_parts = ref.split('/')
    current_part = data
    for part in ref_parts[1:]:
        if part not in current_part:
            return None
        current_part = current_part[part]
    return current_part


def load_body(load_object):
    body = {}
    for k, v in load_object.items():
        if v['type'] == 'array':
            if v['items']['type'] != 'object':
                if 'example' not in v.keys():
                    body[k] = [v['items']['example']]
                else:
                    body[k] = v['example']
            else:
                res = load_body(v['items']['properties'])
                body[k] = [res]

        elif v['type'] == 'object':
            pass
        else:
            body[k] = v['example']
    return body


def parameters_load(parameters):
    params = {}
    headers = {}
    for key_item in parameters:
        if key_item['in'] == 'query':
            params[key_item['name']] = key_item['schema']['example']
        elif key_item['in'] == 'header':
            headers[key_item['name']] = str(key_item['schema']['example'])
    return params, headers


def read_swagger_yaml(file):
    data = yaml.safe_load(file)

    paths = data.get('paths', {})
    res = []
    for path, path_item in paths.items():
        for method, operation in path_item.items():
            if 'requestBody' in operation and 'parameters' not in operation:
                request_body = operation['requestBody']
                if 'content' in request_body and 'application/json' in request_body['content']:
                    content_type = request_body['content']['application/json']
                    if 'schema' in content_type and '$ref' in content_type['schema']:
                        schema_ref = content_type['schema']['$ref']
                        schema = find_schema_by_ref(data, schema_ref)
                        if schema:
                            headers = {'Content-Type': 'application/json'}
                            route_requests = {
                                'url': str(data.get('servers')[0]['url']).strip('/') + path,
                                'method': method,
                                'headers': headers,
                                'body': load_body(schema['properties'])
                            }
                            res.append(route_requests)
            elif 'requestBody' in operation and 'parameters' in operation:
                parameters = operation['parameters']
                params, headers = parameters_load(parameters)
                request_body = operation['requestBody']
                if 'content' in request_body and 'application/json' in request_body['content']:
                    content_type = request_body['content']['application/json']
                    if 'schema' in content_type and '$ref' in content_type['schema']:
                        schema_ref = content_type['schema']['$ref']
                        schema = find_schema_by_ref(data, schema_ref)
                        if schema:
                            headers['Content-Type'] = 'application/json'
                            if params == {}:
                                route_requests = {
                                    'url': str(data.get('servers')[0]['url']).strip('/') + path,
                                    'method': method,
                                    'headers': headers,
                                    'body': load_body(schema['properties'])
                                }
                                res.append(route_requests)
                            else:
                                route_requests = {
                                    'url': str(data.get('servers')[0]['url']).strip('/') + path,
                                    'method': method,
                                    'headers': headers,
                                    'params': params,
                                    'body': load_body(schema['properties'])
                                }
                                res.append(route_requests)

            elif 'requestBody' not in operation and 'parameters' in operation:
                parameters = operation['parameters']
                params, headers = parameters_load(parameters)
                route_requests = {
                    'url': str(data.get('servers')[0]['url']).strip('/') + path,
                    'method': method,
                    'headers': headers,
                    'params': params
                }
                res.append(route_requests)
    return res


if __name__ == '__main__':
    # 使用示例
    read_swagger_yaml('../openapi.yaml')
