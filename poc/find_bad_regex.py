import re

patterns = [
    r"[*_#]",
    r"\(([^)]+)\)\s*\(\1\)",
    r"[ \t]+",
    r"\n{3,}",
    r"[\u0600-\u06FF]",
    r"\b\w{4,}\b",
    r"\[([^\]]+)\]",
    r"\b(toyota\s+\w+|peugeot\s+\w+|clio\s*\d*|bmw\s*\d*|mercedes\s*\w*|dacia\s*\w*|rav4|hyundai\s*\w*|nissan\s*\w*)\b",
    r"(?:je m'appelle|moi c'est|mon nom est|mon prénom est|je suis|c'est)\s+([a-zA-Z]{2,20}(?:\s+[a-zA-Z]{2,20})?)",
    r"\b([A-Z][a-z]{2,15}(?:\s+[A-Z][a-z]{2,15})?)\b",
    r"\b[a-zA-Z]{3,20}\b",
    r"(\+?\d[\d\s-]{6,14}\d)",
    r"\b(ci-\d{4}-[a-z0-9]+|\d{4}\s*[a-z]{2}\s*01)\b",
    r"\b(\d{5}-[a-z]-\d{1,2}|\d{4}-[a-z]-\d{2})\b",
    r"\b(dk-\d{4}-[a-z]+|\d{4}\s*dk)\b"
]

print("=== CHECKING ALL REGEX PATTERNS ===")
for p in patterns:
    try:
        re.compile(p)
        print("OK:", p)
    except Exception as e:
        print("BAD REGEX FOUND! Pattern:", p, "Error:", e)
