import os
import re
import json
from apisix import http 
from io import BytesIO

def mergeProto(_servicename, _protodir):
    buffer = BytesIO()
    buffer.write(b'syntax = "proto3";')
    buffer.write("package {};\r\n".format(_servicename).encode(encoding="utf8"))
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
    return contents

def parseProto(_contents):
    proto_table = {}
    match = re.findall(r".*?service\s*(.*?\}\s*\})", _contents, re.S)
    for service_block in match:
        # 提取服务名
        match = re.findall(r"(\w*?)\s*\{", service_block, re.S)
        service_name = match[0]
        proto_table[service_name] = []
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
            proto_table[service_name].append(rpc_name)
    return proto_table

def push(_address, _apikey, _org, _servicename, _protodir):
    if not os.path.exists(_protodir):
        print(_protodir + " not found")
        return
    """
    Step 1: 合成单文件proto
    """
    contents = mergeProto(_servicename, _protodir)
    """
    Step 2: 注册proto
    """
    data = {"content": contents}
    url = "http://" + _address + "/apisix/admin/proto/" + _servicename
    http.send(url, "PUT", data, _apikey)
    """
    Step 2: 注册Router
    """
    proto_table = parseProto(contents)
    for service_name, rpc_ary in proto_table.items():
        for rpc_name in rpc_ary:
            route_name = _org+ "." + _servicename + "." + service_name + "." + rpc_name
            data = {
                "uri": "/ogm/" + _servicename + "/" + service_name + "/" + rpc_name,
                "name": route_name,
                "methods": ["POST", "OPTIONS"],
                "plugins": {
                    "grpc-transcode": {
                        "deadline": 0,
                        "method": rpc_name,
                        "pb_option": ["no_default_values", "enum_as_value"],
                        "proto_id": _servicename,
                        "service": _servicename + "." + service_name,
                    }
                },
                "service_id": _org + "." + _servicename,
                "status": 1,
            }
            url = "http://" + _address + "/apisix/admin/routes/" + route_name
            http.send(url, "PUT", data, _apikey)

def delete(_address, _apikey, _org, _servicename):
    # get all routers
    url = "http://" + _address + "/apisix/admin/routes"
    reply = http.send(url, "GET", {}, _apikey)
    dict_reply = json.loads(reply)
    if not "node" in dict_reply:
        return
    if not "nodes" in dict_reply["node"]:
        return
    # delete the router with 
    for node in dict_reply["node"]["nodes"]:
        if not "value" in node:
            continue
        if not "id" in node["value"]:
            continue
        if not node["value"]["id"].startswith(_org+"."+_servicename):
            continue
        url = "http://" + _address + "/apisix/admin/routes/" + node["value"]["id"]
        http.send(url, "DELETE", {}, _apikey)
