import random
from datetime import datetime
from datetime import timedelta

# apple = datetime(100,1,1,11,34,59)
# print(random.randrange(50))
# print(apple - timedelta(seconds=60))

def addSecs(tm, secs, secs2):
    secs = secs*5
    fulldate = datetime(100, 1, 1, tm.hour, tm.minute, tm.second)
    if secs2 == 0:
        fulldate = fulldate + timedelta(seconds=(secs))
        delay = secs
    else:
        fulldate = fulldate - timedelta(seconds=(secs))
        delay = -secs
    return str(fulldate.time()), delay

# a = datetime.now().time()
# b,c = addSecs(a, random.randrange(61), random.randrange(2))
# print(a)
# print(b)
# print(c)

apple = "21:49:00"
apple = datetime(100, 1, 1, int(apple[-8:-6]), int(apple[-5:-3]), int(apple[-2:]))
apple, delay = addSecs(apple, random.randrange(61), random.randrange(2))
print(apple)
print(delay)