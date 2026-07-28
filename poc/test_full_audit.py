import urllib.request
import urllib.parse
import json

base_url = "http://127.0.0.1:8000"

endpoints = [
    ("GET", "/", None),
    ("GET", "/sales/chat", None),
    ("GET", "/sales/workspace", None),
    ("GET", "/fraud/workspace", None),
    ("GET", "/api/country/active", None),
    ("POST", "/api/country/switch", {"country_code": "MA"}),
    ("GET", "/api/sales/prospects", None),
    ("POST", "/api/sales/chat", {"prospect_id": "audit-1", "message": "Bonjour", "channel": "WhatsApp"}),
    ("GET", "/api/sales/export", None),
    ("GET", "/api/fraud/claims", None),
    ("GET", "/api/fraud/knowledge", None),
    ("GET", "/api/fraud/network", None),
    ("POST", "/api/country/switch", {"country_code": "CI"})
]

print("=== AUDIT AUTOMATISE COMPLET DE LA PLATEFORME ===\n")

passed = 0
failed = 0

for method, path, data in endpoints:
    url = base_url + path
    try:
        if method == "POST":
            encoded_data = urllib.parse.urlencode(data).encode('utf-8')
            req = urllib.request.Request(url, data=encoded_data)
        else:
            req = urllib.request.Request(url)
            
        resp = urllib.request.urlopen(req, timeout=5)
        status = resp.status
        content_type = resp.headers.get("Content-Type", "")
        
        if status == 200:
            print(f"[OK] [{method}] {path:<30} -> Status 200 OK ({content_type[:25]})")
            passed += 1
        else:
            print(f"[FAIL] [{method}] {path:<30} -> Status {status}")
            failed += 1
    except Exception as e:
        print(f"[FAIL] [{method}] {path:<30} -> EXCEPTION: {e}")
        failed += 1

print("\n" + "="*50)
print(f"RESULTAT AUDIT : {passed} Succes / {passed + failed} Endpoints | Echecs: {failed}")
print("="*50)
