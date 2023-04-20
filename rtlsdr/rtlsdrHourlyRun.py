from SweepClass import sweep
import schedule
import time
import os

#set folder and location
folder = "MearnsTestNew"
location = "G77 5JU"

#run one sweep
sweepRun = sweep(25e6, 1750e6, 'max')
sweepRun.capture()
sweepRun.write(folder, location)

#function to run one sweep
def func():
    sweepRun.startSdr()
    sweepRun.capture()
    sweepRun.write(folder, location)

#function to quit script
def funcEnd():
    quit()

#run sweep every hour for 24 hours
schedule.every(1).hours.do(func)
schedule.every(24).hours.do(funcEnd)

while True:
    schedule.run_pending()
    time.sleep(1)
