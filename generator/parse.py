import os
import re


def scan_protos(_protodir, _enums, _services, _messages):
    if not os.path.exists(_protodir):
        print(_protodir + " not found")
        return

    for entry in os.listdir(_protodir):
        # 跳过不是.proto的文件
        if not entry.endswith(".proto"):
            continue
        # 跳过healthy.proto
        if entry == "healthy.proto":
            continue
        proto_name = os.path.splitext(entry)[0]
        with open(os.path.join(_protodir, entry), "r", encoding="utf-8") as rf:
            content = rf.read()
            rf.close()
            #############################
            # 提取enum名
            #############################
            match = re.findall(r".*?enum\s*(.*?)\s*\{", content, re.S)
            for enum_name in match:
                _enums.append(enum_name)
            #############################
            # 提取service语句块
            #############################
            match = re.findall(r".*?service\s*(.*?\}\s*\})", content, re.S)
            for service_block in match:
                # 提取服务名
                match = re.findall(r"(\w*?)\s*\{", service_block, re.S)
                service_name = match[0]
                _services[service_name] = {}
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
                    # 提取请求
                    match = re.findall(r"\(\s*(.*?)\s*\)\s*returns", rpc_block, re.S)
                    req_name = ""
                    if len(match) > 0:
                        req_name = match[0]
                    # 提取回复
                    match = re.findall(r"returns\s*\(\s*(.*?)\s*\)", rpc_block, re.S)
                    rsp_name = ""
                    if len(match) > 0:
                        rsp_name = match[0]
                    _services[service_name][rpc_name] = (req_name, rsp_name)
            #############################
            # 提取message语句块
            #############################
            match = re.findall(r".*?message\s*(.*?\})", content, re.S)
            for message_block in match:
                # 提取消息名
                match = re.findall(r"(\w*?)\s*\{", message_block, re.S)
                message_name = match[0]
                _messages[message_name] = []
                # 提取字段
                for line in str.splitlines(message_block):
                    # 跳过不包含=的行
                    if str.find(line, "=") < 0:
                        continue
                    # 跳过不包含;的行
                    if str.find(line, ";") < 0:
                        continue
                    isRepeated = False
                    if line.find("repeated") >= 0:
                        isRepeated = True
                        line = line.replace("repeated", "")
                    # 提取字段类型
                    match = re.findall(r"\s*(.*)\s+\w+\s+=", line, re.S)
                    field_type = ""
                    if len(match) > 0:
                        field_type = match[0]
                    if isRepeated:
                        field_type = field_type + "[]"
                    if field_type.startswith("map"):
                        # field_type = 'System.Collections.Generic.Dictionary' + field_type[3:]
                        match = re.findall(r",\s+(\w*?)\>", field_type, re.S)
                        field_type = match[0] + "<>"
                    # 提取字段名
                    match = re.findall(r"\s+(\w+)\s+=", line, re.S)
                    field_name = ""
                    if len(match) > 0:
                        field_name = match[0]
                    # 提取字段注释
                    match = re.findall(r"//\s+(\w+)", line, re.S)
                    field_remark = ""
                    if len(match) > 0:
                        field_remark = str.strip(match[0])
                    _messages[message_name].append(
                        (field_name, field_type, field_remark)
                    )
