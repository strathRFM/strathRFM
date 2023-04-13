from SweepClass import sweep
import schedule
import time
import os

folder = "FALKIRK_3.2MHz"
location = "FK2 9EB"

sweepRun = sweep(25e6, 1750e6, 'max')
sweepRun.capture()
sweepRun.write(folder, location)
    
