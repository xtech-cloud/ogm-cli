import os
import sys
import re
from generator import parse
from generator import file
from generator.template import module as template
from generator.types import module as types
from typing import Dict, List, Tuple


def generateServiceBlock(_enums, _messages, _services, _service, _org_name, _mod_name):
    rpc_block = ""
    for rpc_name in _services[_service].keys():
        rpc = template.template_service_method.replace("{{org}}", _org_name)
        rpc = rpc.replace("{{mod}}", _mod_name)
        rpc = rpc.replace("{{service}}", _service)
        rpc = rpc.replace("{{rpc}}", rpc_name)
        rpc = rpc.replace("{{req}}", _services[_service][rpc_name][0])
        rpc = rpc.replace("{{rsp}}", _services[_service][rpc_name][1])
        rpc_block = rpc_block + str.format("{}\n", rpc)
        req_name = _services[_service][rpc_name][0]
        assign_block = ""
        for field in _messages[req_name]:
            field_name = field[0]
            field_type = field[1]
            # 转换枚举类型
            if field_type in _enums:
                field_type = "enum"
            # 转换类型
            if field_type in types.type_dict.keys():
                field_type = types.type_dict[field_type]

            if (
                field_type in types.type_dict.values()
                or field_type.endswith("[]")
                or field_type.endswith("{}")
            ):
                assign_block = assign_block + str.format(
                    '            paramMap["{}"] = _request._{};\n',
                    field_name,
                    field_name,
                )
        rpc_block = rpc_block.replace("{{assign}}", assign_block)
    return rpc_block


def generateProtoBlock(_enums, _messages):
    proto_block = ""
    for message_name in _messages.keys():
        # 成员声明
        field_block = ""
        # 构造函数中赋初值
        assign_block = ""
        # 遍历所有字段
        for field in _messages[message_name]:
            # 字段名
            field_name = field[0]
            # 字段类型
            field_type = field[1]
            # 转换枚举类型
            if field_type in _enums:
                field_type = "enum"

            if field_type.endswith("[]"):
                field_type = field_type[:-2]
                if field_type in types.type_dict.keys():
                    """可转换类型的数组, 使用Any转换"""
                    assign_block = assign_block + str.format(
                        "                _{} = Any.From{}Ary(new {}[0]);\n",
                        field_name,
                        field_type.title(),
                        field_type,
                    )
                    field_block = field_block + str.format(
                        '            [JsonPropertyName("{}")]\n            public Any _{} {{get;set;}}\n',
                        field_name,
                        field_name,
                    )
                else:
                    """不可转换类型的数组, 使用直接实例化的方式"""
                    assign_block = assign_block + str.format(
                        "                _{} = new {}[0];\n", field_name, field_type
                    )
                    field_block = field_block + str.format(
                        '            [JsonPropertyName("{}")]\n            public {}[] _{} {{get;set;}}\n',
                        field_name,
                        field_type,
                        field_name,
                    )
            elif field_type.endswith("<>"):
                field_type = field_type[:-2]
                """字典使用直接实例化的方式"""
                assign_block = assign_block + str.format(
                    "                _{} = new Dictionary<string, {}>();\n",
                    field_name,
                    field_type,
                )
                field_block = field_block + str.format(
                    '            [JsonPropertyName("{}")]\n            public Dictionary<string, {}> _{} {{get;set;}}\n',
                    field_name,
                    field_type,
                    field_name,
                )
            else:
                if field_type in types.type_dict.keys():
                    """可转换类型的数组, 使用Any转换"""
                    csharp_type = types.type_dict[field_type]
                    any_type = types.type_to_any[csharp_type]
                    assign_block = assign_block + str.format(
                        "                _{} = Any.From{}({});\n",
                        field_name,
                        any_type.title(),
                        types.type_default_value[field_type],
                    )
                    field_block = field_block + str.format(
                        '            [JsonPropertyName("{}")]\n            public Any _{} {{get;set;}}\n',
                        field_name,
                        field_name,
                    )
                else:
                    """不可转换类型, 使用直接实例化的方式"""
                    assign_block = assign_block + str.format(
                        "                _{} = new {}();\n", field_name, field_type
                    )
                    field_block = field_block + str.format(
                        '            [JsonPropertyName("{}")]\n            public {} _{} {{get;set;}}\n',
                        field_name,
                        field_type,
                        field_name,
                    )
        message_block = template.template_proto_class.replace(
            "{{message}}", message_name
        )
        message_block = message_block.replace("{{field}}", field_block)
        message_block = message_block.replace("{{assign}}", assign_block)
        proto_block = proto_block + message_block
    return proto_block


def create_vs_sln(_orgname, _servicename, _protodir):
    org_name = _orgname
    mod_name = _servicename

    if "" == org_name:
        print("org is empty")
        sys.exit(0)

    if "" == mod_name:
        print("mod is empty")
        sys.exit(0)

    proto_dir = _protodir

    enums: List[str] = []

    services: Dict[str, Dict[str, Tuple]] = {}
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

    parse.scan_protos(_protodir, enums, services, messages)

    os.makedirs("vs2019", exist_ok=True)

    # 生成..gitignore文件
    filepath = "./vs2019/.gitignore"
    contents = template.template_gitignore
    file.write(filepath, contents, False)
    # 生成.sln文件
    filepath = "./vs2019/{}-{}.sln".format(org_name, mod_name)
    contents = template.template_sln
    file.write(filepath, contents, False)

    # -----------------------------------------------------------------------------
    # 生成 app 解决方案
    # -----------------------------------------------------------------------------
    os.makedirs("vs2019/app", exist_ok=True)
    # 生成.proj文件
    filepath = "./vs2019/app/app.csproj"
    contents = template.template_proj_app
    file.write(filepath, contents, False)
    # 生成App.xaml
    filepath = "./vs2019/app/App.xaml"
    contents = template.template_app_app_xaml
    file.write(filepath, contents, False)
    # 生成App.xaml.cs
    filepath = "./vs2019/app/App.xaml.cs"
    contents = template.template_app_app_xaml_cs
    contents = contents.replace("{{org}}", org_name)
    contents = contents.replace("{{mod}}", mod_name)
    file.write(filepath, contents, False)
    # 生成AppConfig.cs
    filepath = "./vs2019/app/AppConfig.cs"
    contents = template.template_app_AppConfig_cs
    file.write(filepath, contents, False)
    # 生成AppView.cs
    filepath = "./vs2019/app/AppView.cs"
    contents = template.template_app_AppView_cs
    file.write(filepath, contents, False)
    # 生成AssemblyInfo.cs
    filepath = "./vs2019/app/AssemblyInfo.cs"
    contents = template.template_app_AssemblyInfo_cs
    file.write(filepath, contents, False)
    # 生成BlankModel.cs
    filepath = "./vs2019/app/BlankModel.cs"
    contents = template.template_app_blankmodel_cs
    file.write(filepath, contents, False)
    # 生成ConsoleLogger.cs
    filepath = "./vs2019/app/ConsoleLogger.cs"
    contents = template.template_app_ConsoleLogger_cs
    file.write(filepath, contents, False)
    # 生成MainWindow.xaml
    filepath = "./vs2019/app/MainWindow.xaml"
    contents = template.template_app_mainwindow_xaml
    file.write(filepath, contents, False)
    # 生成MainWindow.xaml.cs
    filepath = "./vs2019/app/MainWindow.xaml.cs"
    contents = template.template_app_mainwindow_xaml_cs
    file.write(filepath, contents, False)

    # -----------------------------------------------------------------------------
    # 生成 bridge 解决方案
    # -----------------------------------------------------------------------------
    os.makedirs("vs2019/bridge", exist_ok=True)
    # 生成.proj文件
    filepath = "./vs2019/bridge/bridge.csproj"
    contents = template.template_proj_bridge.replace("{{org}}", org_name).replace(
        "{{mod}}", mod_name
    )
    file.write(filepath, contents, False)
    # 生成IViewBridge.cs文件
    for service in services.keys():
        filepath = "./vs2019/bridge/I{}ViewBridge.cs".format(service)
        template_method = r"        void On{{rpc}}Submit(string _json);"
        rpc_block = ""
        for rpc_name in services[service].keys():
            rpc = template_method.replace("{{rpc}}", rpc_name)
            rpc_block = rpc_block + str.format("{}\n", rpc)
        contents = template.template_bridge_view_cs
        contents = contents.replace("{{org}}", org_name)
        contents = contents.replace("{{mod}}", mod_name)
        contents = contents.replace("{{service}}", service)
        contents = contents.replace("{{rpc}}", rpc_block)
        file.write(filepath, contents, True)
    # 生成IExtendViewBridge.cs文件
    for service in services.keys():
        filepath = "./vs2019/bridge/I{}ExtendViewBridge.cs".format(service)
        contents = template.template_bridge_extend_view_cs
        contents = contents.replace("{{org}}", org_name)
        contents = contents.replace("{{mod}}", mod_name)
        contents = contents.replace("{{service}}", service)
        file.write(filepath, contents, False)
    # 生成UiBridge.cs文件
    for service in services.keys():
        filepath = "./vs2019/bridge/I{}UiBridge.cs".format(service)
        template_method = r"        void Receive{{rpc}}(string _json);"
        rpc_block = ""
        for rpc_name in services[service].keys():
            rpc = template_method.replace("{{rpc}}", rpc_name)
            rpc_block = rpc_block + str.format("{}\n", rpc)
        contents = template.template_bridge_ui_cs
        contents = contents.replace("{{org}}", org_name)
        contents = contents.replace("{{mod}}", mod_name)
        contents = contents.replace("{{service}}", service)
        contents = contents.replace("{{rpc}}", rpc_block)
        file.write(filepath, contents, True)
    # 生成IExtendUiBridge.cs文件
    for service in services.keys():
        filepath = "./vs2019/bridge/I{}ExtendUiBridge.cs".format(service)
        contents = template.template_bridge_extend_ui_cs
        contents = contents.replace("{{org}}", org_name)
        contents = contents.replace("{{mod}}", mod_name)
        contents = contents.replace("{{service}}", service)
        file.write(filepath, contents, False)

    # -----------------------------------------------------------------------------
    # 生成 module 解决方案
    # -----------------------------------------------------------------------------
    os.makedirs("vs2019/module", exist_ok=True)
    # 生成.proj文件
    filepath = "./vs2019/module/module.csproj"
    contents = template.template_proj_module.replace("{{org}}", org_name).replace(
        "{{mod}}", mod_name
    )
    file.write(filepath, contents, False)
    # 生成ModuleRoot.cs文件
    filepath = "./vs2019/module/ModuleRoot.cs"
    register_block = ""
    cancel_block = ""
    for service in services.keys():
        register_block = (
            register_block
            + template.template_module_register_block.replace("{{service}}", service)
        )
        cancel_block = cancel_block + template.template_module_cancel_block.replace(
            "{{service}}", service
        )
    contents = template.template_module_ModuleRoot_cs
    contents = contents.replace("{{org}}", org_name)
    contents = contents.replace("{{mod}}", mod_name)
    contents = contents.replace("{{register}}", register_block)
    contents = contents.replace("{{cancel}}", cancel_block)
    file.write(filepath, contents, True)
    # 生成Model.cs文件
    for service in services.keys():
        filepath = "./vs2019/module/{}Model.cs".format(service)
        contents = template.template_module_Model_cs
        contents = contents.replace("{{org}}", org_name)
        contents = contents.replace("{{mod}}", mod_name)
        contents = contents.replace("{{service}}", service)
        file.write(filepath, contents, False)
    # 生成BaseModel.cs文件
    for service in services.keys():
        filepath = "./vs2019/module/{}BaseModel.cs".format(service)
        rpc_block = ""
        for rpc_name in services[service].keys():
            rpc = template.template_module_model_method.replace("{{rpc}}", rpc_name)
            rpc = rpc.replace("{{org}}", org_name)
            rpc = rpc.replace("{{mod}}", mod_name)
            rpc = rpc.replace("{{service}}", service)
            rpc = rpc.replace("{{rsp}}", services[service][rpc_name][1])
            rpc_block = rpc_block + str.format("{}\n", rpc)
        contents = template.template_module_BaseModel_cs
        contents = contents.replace("{{org}}", org_name)
        contents = contents.replace("{{mod}}", mod_name)
        contents = contents.replace("{{service}}", service)
        contents = contents.replace("{{rpc}}", rpc_block)
        file.write(filepath, contents, True)
    # 生成View.cs文件
    for service in services.keys():
        filepath = "./vs2019/module/{}View.cs".format(service)
        contents = template.template_module_View_cs
        contents = contents.replace("{{org}}", org_name)
        contents = contents.replace("{{mod}}", mod_name)
        contents = contents.replace("{{service}}", service)
        file.write(filepath, contents, False)
    # 生成BaseView.cs文件
    for service in services.keys():
        filepath = "./vs2019/module/{}BaseView.cs".format(service)
        router_block = ""
        handler_block = ""
        for rpc_name in services[service].keys():
            rsp_name = services[service][rpc_name][1]
            router_block = router_block + template.template_view_router.replace(
                "{{org}}", org_name
            ).replace("{{mod}}", mod_name).replace("{{service}}", service).replace(
                "{{rpc}}", rpc_name
            )
            handler_block = handler_block + template.template_view_handler.replace(
                "{{service}}", service
            ).replace("{{rpc}}", rpc_name).replace("{{rsp}}", rsp_name)
        contents = template.template_module_BaseView_cs
        contents = contents.replace("{{org}}", org_name)
        contents = contents.replace("{{mod}}", mod_name)
        contents = contents.replace("{{service}}", service)
        contents = contents.replace("{{routers}}", router_block)
        contents = contents.replace("{{handlers}}", handler_block)
        file.write(filepath, contents, True)
    # 生成Controller.cs文件
    for service in services.keys():
        filepath = "./vs2019/module/{}Controller.cs".format(service)
        contents = template.template_module_Controller_cs
        contents = contents.replace("{{org}}", org_name)
        contents = contents.replace("{{mod}}", mod_name)
        contents = contents.replace("{{service}}", service)
        file.write(filepath, contents, False)
    # 生成BaseController.cs文件
    for service in services.keys():
        filepath = "./vs2019/module/{}BaseController.cs".format(service)
        contents = template.template_module_BaseController_cs
        contents = contents.replace("{{org}}", org_name)
        contents = contents.replace("{{mod}}", mod_name)
        contents = contents.replace("{{service}}", service)
        file.write(filepath, contents, True)
    # 生成BaseViewBridge.cs文件
    for service in services.keys():
        filepath = "./vs2019/module/{}BaseViewBridge.cs".format(service)
        rpc_block = ""
        for rpc_name in services[service].keys():
            req_name = services[service][rpc_name][0]
            rpc = template.template_viewbridge_method.replace("{{rpc}}", rpc_name)
            rpc = rpc.replace("{{req}}", req_name)
            rpc_block = rpc_block + str.format("{}\n", rpc)
        contents = template.template_module_BaseViewBridge_cs
        contents = contents.replace("{{org}}", org_name)
        contents = contents.replace("{{mod}}", mod_name)
        contents = contents.replace("{{service}}", service)
        contents = contents.replace("{{rpc}}", rpc_block)
        file.write(filepath, contents, True)
    # 生成ViewBridge.cs文件
    for service in services.keys():
        filepath = "./vs2019/module/{}ViewBridge.cs".format(service)
        contents = template.template_module_ViewBridge_cs
        contents = contents.replace("{{org}}", org_name)
        contents = contents.replace("{{mod}}", mod_name)
        contents = contents.replace("{{service}}", service)
        file.write(filepath, contents, False)
    # 生成Service.cs文件
    for service in services.keys():
        filepath = "./vs2019/module/{}Service.cs".format(service)
        contents = template.template_module_Service_cs
        contents = contents.replace("{{org}}", org_name)
        contents = contents.replace("{{mod}}", mod_name)
        contents = contents.replace("{{service}}", service)
        file.write(filepath, contents, False)
    # 生成BaseService.cs文件
    for service in services.keys():
        filepath = "./vs2019/module/{}BaseService.cs".format(service)
        rpc_block = generateServiceBlock(
            enums, messages, services, service, org_name, mod_name
        )
        contents = template.template_module_BaseService_cs
        contents = contents.replace("{{org}}", org_name)
        contents = contents.replace("{{mod}}", mod_name)
        contents = contents.replace("{{service}}", service)
        contents = contents.replace("{{rpc}}", rpc_block)
        file.write(filepath, contents, True)
    # 生成Proto.cs文件
    filepath = "./vs2019/module/Protocol.cs"
    proto_block = generateProtoBlock(enums, messages)
    contents = template.template_module_Protocol_cs
    contents = contents.replace("{{org}}", org_name)
    contents = contents.replace("{{mod}}", mod_name)
    contents = contents.replace("{{proto}}", proto_block)
    file.write(filepath, contents, True)
    # 生成JsonConvert.cs文件
    filepath = "./vs2019/module/JsonConvert.cs"
    contents = template.template_module_Json_Convert_cs
    contents = contents.replace("{{org}}", org_name)
    contents = contents.replace("{{mod}}", mod_name)
    file.write(filepath, contents, False)
    # 生成JsonOptions.cs文件
    filepath = "./vs2019/module/JsonOptions.cs"
    contents = template.template_module_Json_Options_cs
    contents = contents.replace("{{org}}", org_name)
    contents = contents.replace("{{mod}}", mod_name)
    file.write(filepath, contents, False)

    # -----------------------------------------------------------------------------
    # 生成 wpf 解决方案
    # -----------------------------------------------------------------------------
    os.makedirs("vs2019/wpf", exist_ok=True)
    # 生成.proj文件
    filepath = "./vs2019/wpf/wpf.csproj"
    contents = template.template_proj_wpf.replace("{{org}}", org_name).replace(
        "{{mod}}", mod_name
    )
    file.write(filepath, contents, False)
    # 生成BaseUiBridge.cs文件
    for service in services.keys():
        filepath = "./vs2019/wpf/Base{}UiBridge.cs".format(service)
        template_method = template.template_wpf_receive_block
        rpc_block = ""
        for rpc_name in services[service].keys():
            rpc_block = rpc_block + template_method.replace("{{rpc}}", rpc_name)
        contents = template.template_wpf_BaseUiBridge_cs
        contents = contents.replace("{{org}}", org_name)
        contents = contents.replace("{{mod}}", mod_name)
        contents = contents.replace("{{service}}", service)
        contents = contents.replace("{{rpc}}", rpc_block)
        file.write(filepath, contents, True)
    # 生成BaseControlRoot.cs文件
    filepath = "./vs2019/wpf/BaseControlRoot.cs"
    members_block = ""
    register_block = ""
    cancel_block = ""
    for service in services.keys():
        members_block = members_block + template.template_wpf_members_block.replace(
            "{{service}}", service
        )
        register_block = register_block + template.template_wpf_register_block.replace(
            "{{service}}", service
        )
        cancel_block = cancel_block + template.template_wpf_cancel_block.replace(
            "{{service}}", service
        )
    contents = template.template_wpf_BaseControlRoot_cs
    contents = contents.replace("{{org}}", org_name)
    contents = contents.replace("{{mod}}", mod_name)
    contents = contents.replace("{{members}}", members_block)
    contents = contents.replace("{{register}}", register_block)
    contents = contents.replace("{{cancel}}", cancel_block)
    file.write(filepath, contents, True)
    # 生成ControlRoot.cs文件
    filepath = "./vs2019/wpf/ControlRoot.cs"
    contents = template.template_wpf_ControlRoot_cs
    contents = contents.replace("{{org}}", org_name)
    contents = contents.replace("{{mod}}", mod_name)
    file.write(filepath, contents, False)
    # 生成Reply.cs文件
    filepath = "./vs2019/wpf/Reply.cs"
    contents = template.template_wpf_Reply_cs
    contents = contents.replace("{{org}}", org_name)
    contents = contents.replace("{{mod}}", mod_name)
    file.write(filepath, contents, False)
    # 生成Facade.cs文件
    for service in services.keys():
        filepath = "./vs2019/wpf/{}Facade.cs".format(service)
        contents = template.template_wpf_Facade_cs
        contents = contents.replace("{{org}}", org_name)
        contents = contents.replace("{{mod}}", mod_name)
        contents = contents.replace("{{service}}", service)
        file.write(filepath, contents, False)
    # 生成Control.cs文件
    for service in services.keys():
        filepath = "./vs2019/wpf/{}Control.xaml.cs".format(service)
        contents = template.template_wpf_Control_cs
        contents = contents.replace("{{org}}", org_name)
        contents = contents.replace("{{mod}}", mod_name)
        contents = contents.replace("{{service}}", service)
        file.write(filepath, contents, False)
    # 生成Control.xaml文件
    for service in services.keys():
        filepath = "./vs2019/wpf/{}Control.xaml".format(service)
        contents = template.template_wpf_Control_xaml
        contents = contents.replace("{{org}}", org_name)
        contents = contents.replace("{{mod}}", mod_name)
        contents = contents.replace("{{service}}", service)
        file.write(filepath, contents, False)
