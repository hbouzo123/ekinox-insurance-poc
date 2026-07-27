import urllib.request
import json
import io

boundary = '----WebKitFormBoundary7MA4YWxkTrZu0gW'
body = io.BytesIO()

def add_field(name, val):
    body.write(f'--{boundary}\r\nContent-Disposition: form-data; name="{name}"\r\n\r\n{val}\r\n'.encode('utf-8'))

def add_file(name, filename, content):
    body.write(f'--{boundary}\r\nContent-Disposition: form-data; name="{name}"; filename="{filename}"\r\nContent-Type: text/plain\r\n\r\n'.encode('utf-8'))
    body.write(content)
    body.write(b'\r\n')

add_field('prospect_id', 'lead-ocr-test-1')
add_file('file', 'carte_grise_maroc_casablanca.txt', b'ROYAUME DU MAROC - CERTIFICAT D IMMATRICULATION - CARTE GRISE - MATRICULE: 54321-B-6 - CASABLANCA - CHERY TIGGO 7 PRO')

body.write(f'--{boundary}--\r\n'.encode('utf-8'))

req = urllib.request.Request(
    'http://127.0.0.1:8000/api/sales/upload',
    data=body.getvalue(),
    headers={'Content-Type': f'multipart/form-data; boundary={boundary}'}
)

try:
    resp = urllib.request.urlopen(req)
    res = json.loads(resp.read().decode('utf-8'))
    info = res['extracted_info']
    print("=== OCR DOCUMENT INTELLIGENCE SUCCESS ===")
    print("Type:", info['type'])
    print("Country:", info['country'])
    print("Entity:", info['entity'])
    print("Auto Country Switch:", info['auto_country_switched'])
    print("Extracted Data:", info['extracted_data'])
except Exception as e:
    print("Erreur test OCR :", e)
