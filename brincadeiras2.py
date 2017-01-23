from urllib import request
#from time import time
from timeit import default_timer as time

sites = [
    "https://www.yahoo.com",
    "http://www.geocontrol.com.br",
    "http://www.facebook.com",
    "http://www.uol.com.br",
    "http://www.terra.com.br"
]

inicio = time()
for url in sites:    
    with request.urlopen(url) as u:        
        page = u.read()
        print(url, len(page)/1024)
fim = time()

resp = fim - inicio
print(resp)
print(type(resp))


