import urllib.request
import os

key = os.environ.get('GEMINI_API_KEY', 'your-api-key-here')
url = f'https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={key}'
data = b'{"contents":[{"parts":[{"text":"hi"}]}]}'
req = urllib.request.Request(url, data=data, headers={'Content-Type': 'application/json'})

try:
    print(urllib.request.urlopen(req).read().decode())
except Exception as e:
    print(e.read().decode() if hasattr(e, 'read') else e)
