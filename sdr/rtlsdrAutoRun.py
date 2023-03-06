from SweepClassEilidh import sweep
import schedule
import time
import os

sweepRun = sweep(25e6, 1750e6, 'max')
sweepRun.capture()
sweepRun.writeNew('Falkirk-24-02-23') #change to desired filename

def func():
    sweepRun.startSdr()
    sweepRun.write()
    sweepRun.capture()

def funcEnd():
    sweepRun.writeMeta("FK2 9EB") #change to desired postcode
    quit()

schedule.every(15).minutes.do(func)
schedule.every(24).hours.do(funcEnd)
#schedule.every(5).minutes.do(funcEnd)


while True:
    schedule.run_pending()
    time.sleep(1)
