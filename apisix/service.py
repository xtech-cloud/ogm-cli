from apisix import http

def push(_address, _apikey, _org, _name, _host, _port):
    service_name = _org + "." + _name
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
    url = "http://" + _address + "/apisix/admin/services/" + service_name
    http.send(url, "PUT", data, _apikey)
