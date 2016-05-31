import requests
import sys

from requests_oauth2 import OAuth2

url = 'http://127.0.0.1:5001/'
file = open(sys.argv[0], 'rb')
files = {'file': ('lala.txt', file, 'application/octet-stream', {'Expires': '0'})}

r = requests.post(url, files=files)

print(r.text)


