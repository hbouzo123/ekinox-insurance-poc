import urllib.request
import urllib.parse
import json

base_url = "http://127.0.0.1:8000/api/sales/chat"
prospect_id = "test-arabic-query-debug"
message = "je veux savoir ce que tu peux comprendre arabe"
data = urllib.parse.urlencode({'prospect_id': prospect_id, 'message': message, 'channel': 'WhatsApp'}).encode('utf-8')

req = urllib.request.Request(base_url, data=data)
try:
    resp = urllib.request.urlopen(req)
    print(resp.read().decode('utf-8'))
except urllib.error.HTTPError as e:
    print("HTTP ERROR CODE:", e.code)
    print("RESPONSE BODY:\n", e.read().decode('utf-8'))
