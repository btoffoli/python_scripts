from urllib import request
from multiprocessing import Pool
from timeit import default_timer as time

sites = [
    "https://www.yahoo.com",
    "http://www.geocontrol.com.br",
    "http://www.facebook.com",
    "http://www.uol.com.br",
    "http://www.terra.com.br"
]

def getSize(url):
    return (url, len(request.urlopen(url).read()))

with Pool(10) as p:
    inicio = time()
    print(p.map(lambda url:  (url, len(request.urlopen(url).read())), (i for i in sites)))
    fim = time()
    print(fim - inicio)
        