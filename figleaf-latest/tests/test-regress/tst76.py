a = 0
try:
    a = 1
    raise Exception("foo")
except ImportError:    #pragma: NO COVER
    a = 99
except:
    a = 123
assert a == 123
