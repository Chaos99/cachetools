a = 1; b = 2
if 1==1:
    a = 4
    b = 5
    c = 6
elif 1==0:          #pragma: NO COVER
    a = 8
    b = 9
else:          
    a = 11
    b = 12
assert a == 4 and b == 5 and c == 6
