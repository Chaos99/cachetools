a = 0
try:
    a = 1
    raise Exception("foo")
except:
    a = 99
else:
    a = 123
assert a == 99
