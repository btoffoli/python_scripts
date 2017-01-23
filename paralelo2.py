from concurrent.futures import ThreadPoolExecutor as Pool

def f(x):
    return x*x

if __name__ == '__main__':
    with Pool(max_workers=100) as p:
        with open('/tmp/lala.txt', 'w') as file:
            file.writelines(str(p.map(f, range(100000000))))
            file.flush()

        file.close()