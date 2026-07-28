import urllib.request
import urllib.parse
import json

base_url = "http://127.0.0.1:8000/api/sales/chat"
prospect_id = "test-arabic-query"

message = "je veux savoir ce que tu peux comprendre arabe"
data = urllib.parse.urlencode({'prospect_id': prospect_id, 'message': message, 'channel': 'WhatsApp'}).encode('utf-8')

try:
    resp = urllib.request.urlopen(urllib.request.Request(base_url, data=data))
    res = json.loads(resp.read().decode('utf-8'))
    reply = res['reply']
    clean_reply = reply.encode('ascii', errors='backslashreplace').decode('ascii')
    print(f"QUERY: {message}")
    print(f"API REPLY:\n{clean_reply}\n")
except Exception as e:
    print(f"EXCEPTION: {e}")
