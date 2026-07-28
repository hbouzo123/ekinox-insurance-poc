import traceback
from sales import assistant

try:
    res = assistant.handle_sales_conversation("test-id", "je veux savoir ce que tu peux comprendre arabe", "WhatsApp")
    print("SUCCESS! Reply:", res["reply"])
except Exception as e:
    print("EXACT TRACEBACK:")
    traceback.print_exc()
