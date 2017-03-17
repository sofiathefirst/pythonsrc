import threading
def run(x,y):
    for i in range(x,y):
        print i

t1= threading.Thread(target=run,args=(2,5))
t1.start()
#t1.join()
t2= threading.Thread(target=run,args=(7,9))
t2.start()
t2.join()

