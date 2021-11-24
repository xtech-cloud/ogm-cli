import os
import sys
import re
from generator import parse
from generator import file
from generator.template import msa as template
from typing import Dict, List, Tuple

def create_go_sln(_orgname, _servicename, _protodir):
    org_name = _orgname
    service_name = _servicename

    if "" == org_name:
        print("org is empty")
        sys.exit(0)

    if "" == service_name:
        print("service is empty")
        sys.exit(0)

    proto_dir = _protodir

    enums: List[str] = []

    rpc_services: Dict[str, Dict[str, Tuple]] = {}
    """
    service Healthy {
      rpc Echo(EchoRequest) returns (EchoResponse) {}
    }
    转换格式为
    {
        startkit:
        {
            healthy: (EchoRequest, EchoResponse)
        }
    }
    """

    messages: Dict[str, List[Tuple]] = {}
    """
    message EchoRequest {
      string msg = 1;  // 消息
    }
    转换为
    {
        EchoRequest:
        [
            (msg, string, 消息),
        ]
    }
    """

    parse.scan_protos(_protodir, enums, rpc_services, messages)

    # 生成go.mod文件
    filepath = "./go.mod"
    contents = template.template_go_mod
    contents = contents.replace("{{org}}", org_name)
    contents = contents.replace("{{service}}", service_name)
    file.write(filepath, contents, False)
    # 生成Makefile文件
    filepath = "./Makefile"
    contents = template.template_makefile
    contents = contents.replace("{{org}}", org_name)
    contents = contents.replace("{{service}}", service_name)
    file.write(filepath, contents, False)
    # 生成plugin.go文件
    filepath = "./plugin.go"
    contents = template.template_plugin
    file.write(filepath, contents, False)
    # 生成version.go文件
    filepath = "./version.go"
    contents = template.template_version
    file.write(filepath, contents, False)
    # 生成main.go文件
    filepath = "./main.go"
    contents = template.template_main
    handler_block = ""
    for rpc_service in rpc_services.keys():
        handler_block = handler_block + template.template_main_handler_block
        handler_block = handler_block.replace("{{rpc_service}}", rpc_service)
    contents = contents.replace("{{org}}", org_name)
    contents = contents.replace("{{service}}", service_name)
    contents = contents.replace("{{handler_block}}", handler_block)
    file.write(filepath, contents, False)
    # -----------------------------------------------------------------------------
    # 生成 config
    # -----------------------------------------------------------------------------
    os.makedirs("./config", exist_ok=True)
    # 生成config/default.go文件
    filepath = "./config/default.go"
    contents = template.template_config_default
    contents = contents.replace("{{org}}", org_name)
    contents = contents.replace("{{service}}", service_name)
    file.write(filepath, contents, False)
    # 生成config/schema.go文件
    filepath = "./config/schema.go"
    contents = template.template_config_schema
    contents = contents.replace("{{org}}", org_name)
    contents = contents.replace("{{service}}", service_name)
    file.write(filepath, contents, False)
    # 生成config/source.go文件
    filepath = "./config/source.go"
    contents = template.template_config_source
    contents = contents.replace("{{org}}", org_name)
    contents = contents.replace("{{service}}", service_name)
    file.write(filepath, contents, False)
    # -----------------------------------------------------------------------------
    # 生成 model
    # -----------------------------------------------------------------------------
    os.makedirs("./model", exist_ok=True)
    # 生成model/db.cs文件
    filepath = "./model/db.go"
    contents = template.template_model_db
    migrate_block = ""
    for rpc_service in rpc_services.keys():
        migrate_block = migrate_block + template.template_model_migrate_block
        migrate_block = migrate_block.replace("{{rpc_service}}", rpc_service)
    contents = contents.replace("{{org}}", org_name)
    contents = contents.replace("{{service}}", service_name)
    contents = contents.replace("{{migrate_block}}", migrate_block)
    file.write(filepath, contents, False)
    # 生成model/x.cs文件
    for rpc_service in rpc_services.keys():
        filepath = "./model/{}.go".format(rpc_service)
        contents = template.template_model_service
        contents = contents.replace("{{org}}", org_name)
        contents = contents.replace("{{service}}", service_name)
        contents = contents.replace("{{rpc_service}}", rpc_service)
        file.write(filepath, contents, False)
    # -----------------------------------------------------------------------------
    # 生成 handler
    # -----------------------------------------------------------------------------
    os.makedirs("./handler", exist_ok=True)
    # 生成config/healthy.go文件
    filepath = "./handler/Healthy.go"
    contents = template.template_handler_healthy
    contents = contents.replace("{{org}}", org_name)
    contents = contents.replace("{{service}}", service_name)
    file.write(filepath, contents, False)
    # 生成handler/x.cs文件
    for rpc_service in rpc_services.keys():
        method_block = ""
        for rpc_method in rpc_services[rpc_service].keys():
            req = rpc_services[rpc_service][rpc_method][0]
            rsp = rpc_services[rpc_service][rpc_method][1]
            method_block = method_block + template.template_handler_method_block
            method_block = method_block.replace("{{rpc_service}}", rpc_service)
            method_block = method_block.replace("{{rpc_method}}", rpc_method)
            method_block = method_block.replace("{{rpc_req}}", req)
            method_block = method_block.replace("{{rpc_rsp}}", rsp)
        filepath = "./handler/{}.go".format(rpc_service)
        contents = template.template_handler_service
        contents = contents.replace("{{org}}", org_name)
        contents = contents.replace("{{service}}", service_name)
        contents = contents.replace("{{rpc_service}}", rpc_service)
        contents = contents.replace("{{method_block}}", method_block)
        file.write(filepath, contents, False)
