import requests
from pathlib import Path
import sys
p = Path(__file__).resolve().parents[1] / 'data' / 'sample_facts.csv'
url = 'http://127.0.0.1:8000/api/upload/csv'
print('Uploading', p)
with p.open('rb') as f:
    files = {'file': (p.name, f, 'text/csv')}
    try:
        r = requests.post(url, files=files, timeout=600)
        print('STATUS', r.status_code)
        try:
            print(r.json())
        except Exception:
            print(r.text)
    except Exception as e:
        print('ERROR', e)
        sys.exit(2)
