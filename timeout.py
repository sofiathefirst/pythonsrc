import signal

# Register an handler for the timeout
def handler(signum, frame):
    print "Forever is over!"
    raise Exception("end of time")


# This function *may* run for an indetermined time...
def loop_forever():
    import time
    while 1:
        print "sec"
        time.sleep(0.001)
       

signal.signal(signal.SIGALRM, handler)

signal.alarm(1)

try:
    loop_forever()
except Exception, exc: 
    print exc
