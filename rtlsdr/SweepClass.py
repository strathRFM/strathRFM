##from pylab import *
import asyncio
from rtlsdr import *
import time as clock
import matplotlib.pyplot as plt
import numpy as np
from numpy.fft import fft
import matplotlib.mlab as mlab
import scipy.signal
import sigmf
from sigmf import SigMFFile
from sigmf.utils import get_data_type_str
import datetime as dt
from datetime import datetime
import geojson
from geojson import Point
import json
import geocoder
import requests
from ipstack import GeoLookup
import os


#send_url = "http://api.ipstack.com/check?access_key=7b95fd77efbf101f0326be586602155f"
#geo_req = requests.get(send_url)
#geo_json = geo_req.json()
#user_postition = [geo_json["latitude"], geo_json["longitude"]]

#print(user_postition)
#geo_lookup = GeoLookup("f3cbc704610c732ca77b700b12cf0d9d")
#location = geo_lookup.get_own_location()
#print(location)

#g= geocoder.ipinfo('me')



class sweep:
    def __init__(self, lower, upper, proc_method):
        self.startSdr()
        self.start_freq = lower #25e6 min
        self.stop_freq = upper #1750e6 max

        self.nfrmhold = 20
        self.nfrmdump = 150 ## do not change - clears buffer
        self.nfft = 4096
        self.dec_factor = 16
        self.overlap = 0.5

        self.calculations()

        self.proc = proc_method #can be 'avg' or 'max' - 'max' better   
        
    def startSdr(self):
        self.sdr = RtlSdr() #should probs add a try catch so this doesn't crash the code if sdr isn't plugged in
        self.sdr.sample_rate = 3.2e6
        self.sdr.center_freq = 100e6
        self.sdr.gain = 40
        self.sdr.frequency_correction = 0
        
    #do initial calculations from parameters
    def calculations(self):
        self.tuner_freqs = np.arange(self.start_freq, self.stop_freq, self.sdr.sample_rate*self.overlap)
        if(max(self.tuner_freqs) < self.stop_freq):
            np.append(self.tuner_freqs, max(self.tuner_freqs) + self.sdr.sample_rate*self.overlap)
        self.nretunes = len(self.tuner_freqs)
        self.fbinw = self.sdr.sample_rate/self.nfft
        self.faxis = np.arange(self.tuner_freqs[0]-self.sdr.sample_rate/2*self.overlap, (self.tuner_freqs[-1]+self.sdr.sample_rate/2*self.overlap)-self.fbinw, self.fbinw*self.dec_factor)/1e6

        self.fft_middle = np.empty([self.nfrmhold, int(self.nfft*self.overlap)])
        self.fft_dec = np.empty([self.nretunes, int(self.nfft*self.overlap/self.dec_factor)])
    
    #capture spectrum data
    def capture(self):
        #start timer
        self.t = clock.time()

        #loop for all tuner values
        for ntune in range(self.nretunes):
            #retune
            self.sdr.center_freq = self.tuner_freqs[ntune]

            #clear software buffer
            for i in range(100):
                sampled = False
                while sampled == False:
                    try:
                        samples = self.sdr.read_samples(self.nfft)
                        sampled = True
                    except OSError:
                        print("Error reading samples, trying again")
                        self.sdr.close()
                        self.startSdr()
                        self.sdr.center_freq = self.tuner_freqs[ntune]
                        clock.sleep(1)


            print(self.tuner_freqs[ntune]) ##display current value

            for frm in range(self.nfrmhold):
                sampled = False
                while sampled == False:
                    try:
                        samples = self.sdr.read_samples(self.nfft)
                        sampled = True
                    except OSError:
                        print("Error reading samples, trying again")
                        self.sdr.close()
                        self.startSdr()
                        self.sdr.center_freq = self.tuner_freqs[ntune]
                        clock.sleep(1)
                
                samples = samples - np.mean(samples)
                
                spectrum = np.abs(fft(samples, self.nfft))
                self.fft_middle[frm, :(int(self.overlap*self.nfft/2))] = spectrum[(int(self.overlap*self.nfft/2 + self.nfft/2)):]
                self.fft_middle[frm, (int(self.overlap*self.nfft/2)):] = spectrum[1:(int(self.overlap*self.nfft/2))+1]

            if self.proc == 'mean':
                self.fft_mean = np.mean(self.fft_middle, axis = 0)
            elif self.proc == 'max':
                self.fft_mean = np.max(self.fft_middle, axis = 0)
            self.fft_dec[ntune, :] = scipy.signal.decimate(self.fft_mean, self.dec_factor, 300, ftype='fir')
    
        self.fft_all = self.fft_dec.flatten()

        for i in range(int(self.nfft*self.overlap/self.dec_factor), len(self.fft_all), int(self.nfft*self.overlap/self.dec_factor)):
            self.fft_all[i] = (self.fft_all[i-1] + self.fft_all[i+1])/2
        
        elapsed = clock.time() - self.t
        print('Total Time =',elapsed)
        self.sdr.close()
        
        #h = hann(self.nfft)
        #X = fft(samples)
        #N = len(self.fft_dec[-1, :])+1
        #N = len(spectrum)+1
        N = len(self.fft_middle[-1, :])+1
        n = np.arange(N)
        T = N/self.sdr.sample_rate
        freq = n/T/2 + self.tuner_freqs[ntune] - 0.7e6
##        plt.figure()
##        #plt.plot(freq[1:], (10*np.log10(np.square(self.fft_dec[-1, :])/50)))
##        #plt.plot(spectrum)
##        #plt.plot(self.fft_middle[-1, :])
##        #plt.plot(self.fft_mean);
##        #plt.plot(self.fft_dec[-1, :]);
##        plt.plot(self.faxis, 10*np.log10(np.square(self.fft_all)/50), linewidth = 0.5)
##        #plt.xlim(self.start_freq/1e6,self.stop_freq/1e6)
##        plt.show()

        #power, psd_freq = plt.psd(samples, NFFT=4096, Fs=self.sdr.sample_rate, Fc = self.sdr.center_freq)
        #plt.show()


    def write(self, folder, location):
        now = dt.datetime.now()
        file_time = now.strftime("%d-%m-%y_%H")

        isExist = os.path.exists(folder)
        if not isExist:
           os.makedirs(folder)
        
        self.fileData = folder + '\\S_' + file_time + '.sigmf-data'
        self.f = open(self.fileData, "wb")
        self.fileMeta = folder + '\\S_' + file_time + '.sigmf-meta'
        self.data = 10*np.log10(np.square(self.fft_all)/50)
        self.data.astype(float)
        self.data.tofile(self.f)

        self.flo = [self.faxis[0]]
        self.fhi = [self.faxis[-1]]
        self.datetimekey = [dt.datetime.utcnow().isoformat()+'Z']

        self.length = [len(self.data)]

        self.f.close()
        g = geocoder.arcgis(location)
        
        self.meta = SigMFFile(
            data_file = self.fileData, # extension is optional
            global_info = {
                SigMFFile.DATATYPE_KEY: get_data_type_str(self.data),  # in this case, 'rf32_le',
                SigMFFile.AUTHOR_KEY: 'RTL-SDR',
                SigMFFile.VERSION_KEY: sigmf.__version__,
                SigMFFile.GEOLOCATION_KEY: Point((g.latlng)),
                

            }
        )
        last = 0
        print(self.flo)
        for i in range(len(self.flo)): 
            self.meta.add_capture(last, metadata = {
                SigMFFile.FREQUENCY_KEY: 2.8e6,
                SigMFFile.DATETIME_KEY: self.datetimekey[i],
            })

            self.meta.add_annotation(last, self.length[i], metadata = {
                SigMFFile.FLO_KEY: self.flo[i],
                SigMFFile.FHI_KEY: self.fhi[i],
            })
            last += self.length[i]
        self.meta.tofile(self.fileMeta)
