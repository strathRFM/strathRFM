from SweepClass import sweep
import schedule
import time
import os

folder = "FalkirkTest"
location = "FK2 9EB"

sweepRun = sweep(25e6, 1750e6, 'max')
sweepRun.capture()
sweepRun.write(folder, location)

def func():
    sweepRun.startSdr()
    sweepRun.capture()
    sweepRun.write(folder, location)
    
def funcEnd():
    quit()

schedule.every(1).hours.do(func)
schedule.every(24).hours.do(funcEnd)
#schedule.every(5).minutes.do(funcEnd)


while True:
    schedule.run_pending()
    time.sleep(1)
