import urllib.request
import json
req = urllib.request.Request("http://localhost:8000/api/v1/codegen/generate", data=b'{"prompt":"hello"}', headers={'Content-Type': 'application/json'})
try:
    res = urllib.request.urlopen(req)
    print(res.read().decode())
except Exception as e:
    if hasattr(e, 'read'):
        print(e.read().decode())
    else:
        print(e)
