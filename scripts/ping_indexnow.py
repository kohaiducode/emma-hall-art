import urllib.request
import json

HOST = "www.emmahallpaintings.com"
KEY = "e0f7a9d312894b598d9e68270b2dfc83"
KEY_LOCATION = f"https://{HOST}/{KEY}.txt"

URL_LIST = [
    f"https://{HOST}/",
    f"https://{HOST}/sitemap.xml"
]

def ping_indexnow():
    payload = {
        "host": HOST,
        "key": KEY,
        "keyLocation": KEY_LOCATION,
        "urlList": URL_LIST
    }
    
    headers = {
        "Content-Type": "application/json; charset=utf-8",
        "User-Agent": "IndexNow-Client/1.0"
    }
    
    req = urllib.request.Request(
        "https://api.indexnow.org/indexnow",
        data=json.dumps(payload).encode("utf-8"),
        headers=headers,
        method="POST"
    )
    
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            print(f"IndexNow notification sent! Response status: {resp.status}")
    except Exception as e:
        print(f"IndexNow notice: {e} (This can be run after deployment)")

if __name__ == "__main__":
    ping_indexnow()
