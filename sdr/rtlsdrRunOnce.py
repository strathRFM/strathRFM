from SweepClassEilidh import sweep
import schedule
import time
import os

sweepRun = sweep(900e6, 1200e6, 'max')
sweepRun.capture()
sweepRun.writeNew('spike_removal4') #change to desired filename
sweepRun.writeMeta("G77 5JU")
