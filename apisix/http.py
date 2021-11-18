import json
import urllib.request

def send(_url, _method, _data, _apikey):
    print("****************************************************")
    print("Request: ")
    print("****************************************************")
    print(_url)
    request = urllib.request.Request(
        _url, json.dumps(_data, ensure_ascii=False).encode(encoding="utf8")
    )
    request.add_header("Content-Type", "application/json;charset=UTF-8")
    request.add_header("X-API-KEY", _apikey)
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
        return reply
    except Exception as e:
        print(e)

