a = 0
try:
    a = 1
except:           #pragma: NO COVER
    a = 99
assert a == 1
