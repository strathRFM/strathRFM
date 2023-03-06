##from pylab import *
import asyncio
from rtlsdr import *
import time as clock
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.mlab as mlab
import sys
np.set_printoptions(threshold=sys.maxsize)


class sweep:
    ## init function - plan to add more so we can tweak variables but this is the default values
    def __init__(self):
        self.sdr = RtlSdr() ##should probs add a try catch so this doesn't crash the code if sdr isn't plugged in

        self.info = "No info added"
        self.start_freq = 50e6
        self.stop_freq = 1750e6
        
        self.sdr.sample_rate = 2.8e6
        self.sdr.center_freq = 100e6
        self.sdr.gain = 40
        self.sdr.frequency_correction = 0

        self.nfrmhold = 20
        self.nfrmdump = 100 ## do not change - clears buffer
        self.fft_method = 'avg' ##can be avg or max
        self.nfft = 4096
        self.dec_factor = 16
        self.overlap = 0.5

        self.calculations()
        

    #do initial calculations from parameters
    def calculations(self):
        self.tuner_freqs =np.arange(self.start_freq, self.stop_freq, self.sdr.sample_rate*self.overlap)
        if(max(self.tuner_freqs) < self.stop_freq):
            np.append(self.tuner_freqs, max(self.tuner_freqs) + self.sdr.sample_rate*self.overlap)
        self.nretunes = len(self.tuner_freqs)
        self.fbinw = self.sdr.sample_rate/self.nfft
        self.faxis = np.arange(self.tuner_freqs[0]-self.sdr.sample_rate/2*self.overlap, (self.tuner_freqs[-1]+self.sdr.sample_rate/2*self.overlap)-self.fbinw, self.fbinw*self.dec_factor)/1e6

    print('Working')
    
    
    #capture spectrum data
    
    async def capture(self):
        sdr = self.sdr
        #start timer
        self.t = clock.time()
        
        #loop for all tuner values
        for ntune in range(self.nretunes):
            #retune
            print(int(self.tuner_freqs[ntune])) ##display current value
            self.sdr.center_freq = int(self.tuner_freqs[ntune])
            print("retuned")
            
            i = 0
            j = 0
            frames = []
            frame = []
            #clock.sleep(5)
            async for samples in self.sdr.stream(1024):
#                 #clear software buffer
                 print("reached loop")
                 print(samples)
                 break
#                 i += 1
#                 if i > 100:
#                     if j < 4096:
#                        j += 1 
#                        frame.append(samples)
#                     else:
#                         j = 0
#                         print("new frame")
#                         frames.append(frame)
#                         frame = []     

            print(int(self.sdr.center_freq))

#             for frm in range(self.nfrmhold):
#                 samples = self.sdr.read_samples(1024)
# 
#                 samples = samples - np.average(samples)
# 
#                 power, psd_freq = plt.psd(samples, NFFT=self.nfft, Fs=self.sdr.sample_rate, Fc=self.sdr.center_freq)
        

        #print("hui")    
        await self.sdr.stop()
        elapsed = clock.time() - self.t
        print('Total Time =',elapsed)
        self.sdr.close()


loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)
sweepTest = sweep()
##print(sweepTest.tuner_freqs)
loop.run_until_complete(sweepTest.capture())
