import urllib.request
import urllib.parse
import json

prospect_id = "test-e2e-ocr-client"

# 1. Send initial message
data1 = urllib.parse.urlencode({'prospect_id': prospect_id, 'message': 'Bonjour', 'channel': 'WhatsApp'}).encode('utf-8')
urllib.request.urlopen(urllib.request.Request('http://127.0.0.1:8000/api/sales/chat', data=data1))

# 2. Upload dummy Carte Grise file via multipart/form-data
boundary = '---------------------------1234567890123456789012345678'
body = []
body.append(f'--{boundary}'.encode('utf-8'))
body.append('Content-Disposition: form-data; name="prospect_id"'.encode('utf-8'))
body.append(''.encode('utf-8'))
body.append(prospect_id.encode('utf-8'))

body.append(f'--{boundary}'.encode('utf-8'))
body.append('Content-Disposition: form-data; name="file"; filename="carte_grise_peugeot_208.pdf"'.encode('utf-8'))
body.append('Content-Type: application/pdf'.encode('utf-8'))
body.append(''.encode('utf-8'))
body.append(b'%PDF-1.4 Carte Grise Peugeot 208 immatriculation CI-5099-AB2 7 CV')
body.append(f'--{boundary}--'.encode('utf-8'))

content = b'\r\n'.join(body)

upload_req = urllib.request.Request(
    'http://127.0.0.1:8000/api/sales/upload',
    data=content,
    headers={'Content-Type': f'multipart/form-data; boundary={boundary}'}
)

up_resp = urllib.request.urlopen(upload_req)
up_data = json.loads(up_resp.read().decode('utf-8'))
print("=== STEP 1: OCR FILE UPLOAD SUCCESS ===")
print("Type:", up_data['extracted_info']['type'])
print("Vehicle:", up_data['prospect_state']['vehicle'])

# 3. Prospect clicks 'Obtenir mon tarif personnalisé'
data3 = urllib.parse.urlencode({'prospect_id': prospect_id, 'message': 'Obtenir mon tarif personnalisé', 'channel': 'WhatsApp'}).encode('utf-8')
resp3 = urllib.request.urlopen(urllib.request.Request('http://127.0.0.1:8000/api/sales/chat', data=data3))
res3 = json.loads(resp3.read().decode('utf-8'))

print("\n=== STEP 2: TARIF RÉPONSE CALCULÉE SANS REDEMANDER LE SCAN ===")
clean_reply = res3['reply'].encode('ascii', errors='backslashreplace').decode('ascii')
print(clean_reply)
