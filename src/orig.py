import time
import threading


class Thing:
    def __init__(self):
        self.foo = True


y = Thing()


def tmain():
    y.foo = False
    while True:
        time.sleep(.7)
        print("thread", y.foo)


x = threading.Thread(target=tmain)
x.daemon = True
x.start()

while True:
    time.sleep(1)
    print("main", y.foo)
