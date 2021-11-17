import os
import sys
import json
import re
import urllib.request
from io import BytesIO

print("****************************************************")
print("* OpenGM Client Tool - ver 3.0.0")
print("****************************************************")

api_key = "edd1c9f034335f136f87ad84b625c8f1"
address = input("enter apisix address (e.g. localhost:9080):")


def send(_url, _method, _data):
    print("****************************************************")
    print("Request: ")
    print("****************************************************")
    print(_url)
    request = urllib.request.Request(
        _url, json.dumps(_data, ensure_ascii=False).encode(encoding="utf8")
    )
    request.add_header("Content-Type", "application/json;charset=UTF-8")
    request.add_header("X-API-KEY", api_key)
    request.get_method = lambda: _method

    try:
        req = urllib.request.urlopen(request)
        reply = req.read().decode("utf-8")
        req.close()
        del req
        print("****************************************************")
        print("Response: ")
        print("****************************************************")
        print(reply)
        print("****************************************************")
    except Exception as e:
        print(e)


def generateService(_ogm, _name, _host, _port):
    service_name = _ogm + "." + _name
    data = {
        "name": service_name,
        "upstream": {
            "scheme": "grpc",
            "type": "roundrobin",
            "nodes": [{"host": _host, "port": int(_port), "weight": 1}],
            "timeout": {"connect": 6, "send": 6, "read": 6},
            "type": "roundrobin",
            "scheme": "grpc",
            "pass_host": "pass",
            "keepalive_pool": {"idle_timeout": 60, "requests": 1000, "size": 320},
        },
        "plugins": {
            "cors": {
                "allow_credential": False,
                "allow_headers": "*",
                "allow_methods": "*",
                "allow_origins": "*",
                "disable": False,
                "expose_headers": "*",
                "max_age": 5,
            },
            "key-auth": {"disable": False},
        },
    }
    url = "http://" + address + "/apisix/admin/services/" + service_name
    send(url, "PUT", data)


def generateRouter(_ogm, _protoname, _protodir):
    """
    Step 1: 合成单文件proto
    """
    buffer = BytesIO()
    buffer.write(b'syntax = "proto3";')
    buffer.write("package {};\r\n".format(_protoname).encode(encoding="utf8"))
    try:
        for root, dirs, files in os.walk(_protodir):
            for file in files:
                if not file.endswith(".proto"):
                    continue
                file_path = os.path.join(root, file)
                print("parse: " + file_path)
                with open(file_path, "rb") as f:
                    # 写入到单文件中
                    for line in f:
                        if line.startswith(b"syntax"):
                            continue
                        if line.startswith(b"option"):
                            continue
                        if line.startswith(b"//"):
                            continue
                        if line.startswith(b"import"):
                            continue
                        buffer.write(line)
        print("build proto finish")
    except Exception as e:
        print(e)

    buffer.seek(0)
    contents = buffer.read().decode(encoding="utf8")
    data = {"content": contents}
    """
    Step 2: 注册proto
    """
    url = "http://" + address + "/apisix/admin/proto/" + _protoname
    send(url, "PUT", data)
    """
    Step 2: 注册Router
    """
    match = re.findall(r".*?service\s*(.*?\}\s*\})", contents, re.S)
    for service_block in match:
        # 提取服务名
        match = re.findall(r"(\w*?)\s*\{", service_block, re.S)
        service_name = match[0]
        # 提取服务方法
        for line in str.splitlines(service_block):
            # 跳过不包含rpc的行
            if str.find(line, "rpc") < 0:
                continue
            # 跳过包含stream的行
            if str.find(line, "stream") >= 0:
                continue
            # 提取rpc语句块
            match = re.findall(r".*rpc\s*(.*?)\s*\{\s*\}", line, re.S)
            if len(match) == 0:
                continue
            rpc_block = match[0]
            # 提取方法名
            match = re.findall(r"^(.*?)\s*\(", rpc_block, re.S)
            if len(match) == 0:
                continue
            rpc_name = match[0]
            route_name = _ogm + "." + proto_name + "." + service_name + "." + rpc_name
            data = {
                "uri": "/ogm/" + proto_name + "/" + service_name + "/" + rpc_name,
                "name": route_name,
                "methods": ["POST", "OPTIONS"],
                "plugins": {
                    "grpc-transcode": {
                        "deadline": 0,
                        "method": rpc_name,
                        "pb_option": ["no_default_values"],
                        "proto_id": _protoname,
                        "service": _protoname + "." + service_name,
                    }
                },
                "service_id": _ogm + "." + _protoname,
                "status": 1,
            }
            url = "http://" + address + "/apisix/admin/routes/" + route_name
            send(url, "PUT", data)


print("1. Generate the service")
print("2. Generate the router")
index = input("enter you choice:")

if "1" == index:
    ogm_name = input("service name (e.g. ogm):")
    service_name = input("service name (e.g. account):")
    upstream_host = input("upstream host (e.g. 10.1.0.1):")
    upstream_port = input("upstream port (e.g. 18899):")
    generateService(ogm_name, service_name, upstream_host, upstream_port)
elif "2" == index:
    ogm_name = input("service name (e.g. ogm):")
    proto_name = input("proto name (e.g. account):")
    proto_dir = input("proto dir(e.g. ogm-msp-account/proto/account):")
    generateRouter(ogm_name, proto_name, proto_dir)
