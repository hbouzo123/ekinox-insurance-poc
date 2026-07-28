import urllib.request
import urllib.parse
import json

data = urllib.parse.urlencode({
    'prospect_id': 'test-voice-offers-2',
    'message': 'Je veux en savoir plus sur les offres et produits SanlamAllianz',
    'channel': 'WhatsApp'
}).encode('utf-8')

req = urllib.request.Request('http://127.0.0.1:8000/api/sales/chat', data=data)
try:
    resp = urllib.request.urlopen(req, timeout=15)
    res = json.loads(resp.read().decode('utf-8'))
    print("=== RÉPONSE CONTEXTUELLE DEEPSEEK-V4-FLASH ===")
    print(res['reply'].encode('ascii', errors='backslashreplace').decode('ascii'))
except Exception as e:
    print("Error:", e)
