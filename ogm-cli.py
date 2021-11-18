import os
import sys
import apisix
import generator


print("****************************************************")
print("* OpenGM Client Tool - ver 3.0.0")
print("****************************************************")

default_api_key = "ef43c22d3e5fb1a8bc94001966a6da4d"
def generateModule(_ogm, _modulename, _protodir):
    import generator

print("1. push the service to apisix")
print("2. push the router to apisix")
print("3. delete all routers from apisix")
print("3. generate the module")
index = input("enter you choice:")

if "1" == index:
    address = input("enter apisix address (default localhost:9088):")
    if '' == address:
        address = "localhost:9088"
    apikey = input("enter apisix apikey (default "+ default_api_key + "):")
    if '' == apikey:
        apikey = default_api_key
    org_name = input("enter organization name (default ogm):")
    if '' == org_name:
        org_name = "ogm"
    upstream_host = input("enter upstream host (default 10.1.100.11):")
    if '' == upstream_host:
        upstream_host = "10.1.100.11"
    upstream_port = input("enter upstream port (default 18899):")
    if '' == upstream_port:
        upstream_port = "18899"
    service_name = input("enter service name (e.g. account):")
    from apisix import service
    service.push(address, apikey, org_name, service_name, upstream_host, upstream_port)
elif "2" == index:
    address = input("enter apisix address (default localhost:9088):")
    if '' == address:
        address = "localhost:9088"
    apikey = input("enter apisix apikey (default "+ default_api_key + "):")
    if '' == apikey:
        apikey = default_api_key
    org_name = input("enter organization name (default ogm):")
    if '' == org_name:
        org_name = "ogm"
    service_name = input("enter service name (e.g. startkit):")
    proto_dir = input("enter proto dir(e.g. ogm-msp-account/proto/account):")
    from apisix import router
    router.push(address, apikey, org_name, service_name, proto_dir)
elif "3" == index:
    address = input("enter apisix address (default localhost:9088):")
    if '' == address:
        address = "localhost:9088"
    apikey = input("enter apisix apikey (default "+ default_api_key + "):")
    if '' == apikey:
        apikey = default_api_key
    org_name = input("enter organization name (default ogm):")
    if '' == org_name:
        org_name = "ogm"
    service_name = input("enter service name (e.g. startkit):")
    from apisix import router
    router.delete(address, apikey, org_name, service_name)
elif "4" == index:
    org_name = input("enter organization name (e.g. ogm):")
    module_name = input("enter module name (e.g. account):")
    proto_dir = input("enter proto dir(e.g. ogm-msp-account/proto/account):")
    generator.createModule(org_name, module_name, proto_dir)
