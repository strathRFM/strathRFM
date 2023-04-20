from SweepClass import sweep
import schedule
import time
import os

#set folder and location
folder = "Dec32"
location = "G77 5JU"

#run one sweep
sweepRun = sweep(25e6, 1750e6, 'max')
sweepRun.capture()
sweepRun.write(folder, location)
    
