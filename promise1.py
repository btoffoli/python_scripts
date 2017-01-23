from promise import Promise



promise = Promise (lambda resolve, reject: 2)
a = promise.then()
print(a.value)

def test_rest(res):
    return res == ['a', 'b', 'c']

p = Promise.all([Promise.resolve('a'), 'b', Promise.resolve('c')]) \
       .then(test_rest)
print(p.value)
assert p.value is True


p = Promise.resolve('a')
print(p.value)

def promessaHandler(resolve, reject):
    return reject('RESOLVIDO!')
p = Promise(promessaHandler)

print(p.value)



