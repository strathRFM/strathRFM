#Modified 20/04/2023
#Eilidh Hamilton, Ashleigh Reid, Martin Dimov

#Based on script in:
#B. Stewart, K. Barlee, D. Atkinson and L. Crockett
#“Software Defined Radio Using MATLAB & Simulink and the RTL-SDR,”
#in What is the RTL-SDR?, Glasgow, Strathclyde Academic Media, 2015


#import libraries
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

#defines class for sweep that can be used by other scripts
class sweep:
    #initialising method - can define upper and lower frequency and processing method
    def __init__(self, lower, upper, proc_method):
        #initialises sdr
        self.startSdr()
        #sets upper and lower frequency
        self.start_freq = lower #25e6 min
        self.stop_freq = upper #1750e6 max

        #sets dsp parameters
        self.nfrmhold = 20
        self.nfrmdump = 150 ## do not change - clears buffer
        self.nfft = 4096
        self.dec_factor = 16
        self.overlap = 0.5

        #calculates other parameters
        self.calculations()

        self.proc = proc_method #can be 'avg' or 'max' - 'max' better   

    #starts sdr    
    def startSdr(self):
        self.sdr = RtlSdr()
        ##sets sdr parameters
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
                #error handling - loops until samples
                #if sampling fails reboots sdr and waits 1 second
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


            print(self.tuner_freqs[ntune]) #display current value

            #samples x amounts of frames
            for frm in range(self.nfrmhold):
                #error handling - loops until samples
                #if sampling fails reboots sdr and waits 1 second
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
                        
                #removes dc component
                samples = samples - np.mean(samples)

                #takes fft of spectrum
                spectrum = np.abs(fft(samples, self.nfft))
                #only takes middle of fft - has to reshuffle values to correct position
                self.fft_middle[frm, :(int(self.overlap*self.nfft/2))] = spectrum[(int(self.overlap*self.nfft/2 + self.nfft/2)):]
                self.fft_middle[frm, (int(self.overlap*self.nfft/2)):] = spectrum[1:(int(self.overlap*self.nfft/2))+1]

            #finds mean or max of all frames
            if self.proc == 'mean':
                self.fft_mean = np.mean(self.fft_middle, axis = 0)
            elif self.proc == 'max':
                self.fft_mean = np.max(self.fft_middle, axis = 0)

            #decimates frame to reduce noise
            self.fft_dec[ntune, :] = scipy.signal.decimate(self.fft_mean, self.dec_factor, 300, ftype='fir')

        #flattens data from 2D array to 1D array
        self.fft_all = self.fft_dec.flatten()

        #removes discontinuities between bands
        for i in range(int(self.nfft*self.overlap/self.dec_factor), len(self.fft_all), int(self.nfft*self.overlap/self.dec_factor)):
            self.fft_all[i] = (self.fft_all[i-1] + self.fft_all[i+1])/2

        #calculates time taken for sweep
        elapsed = clock.time() - self.t
        print('Total Time =',elapsed)
        #shuts down sdr
        self.sdr.close()

        #used for plotting if required
        
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
        

    #writes to sigmf file
    def write(self, folder, location):
        #gets date and time
        now = dt.datetime.now()
        file_time = now.strftime("%d-%m-%y_%H")

        #if folder doesn't exist creates folder
        isExist = os.path.exists(folder)
        if not isExist:
           os.makedirs(folder)

        #creates file names, opens data file and writes data
        self.fileData = folder + '\\S_' + file_time + '.sigmf-data'
        self.f = open(self.fileData, "wb")
        self.fileMeta = folder + '\\S_' + file_time + '.sigmf-meta'
        self.data = 10*np.log10(np.square(self.fft_all)/50)
        self.data.astype(float)
        self.data.tofile(self.f)

        #gets upper and lower frequency, datetime and length
        self.flo = [self.faxis[0]]
        self.fhi = [self.faxis[-1]]
        self.datetimekey = [dt.datetime.utcnow().isoformat()+'Z']
        self.length = [len(self.data)]

        #closes data file
        self.f.close()

        #gets location using info passed into method
        g = geocoder.arcgis(location)

        #writes metadata to file
        self.meta = SigMFFile(
            data_file = self.fileData, # extension is optional
            global_info = {
                SigMFFile.DATATYPE_KEY: get_data_type_str(self.data),  # in this case, 'rf32_le',
                SigMFFile.AUTHOR_KEY: 'RTL-SDR',
                SigMFFile.VERSION_KEY: sigmf.__version__,
                SigMFFile.GEOLOCATION_KEY: Point((g.latlng)),
                

            }
        )
        #writes additional metadata to file
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
        #saves metadata file
        self.meta.tofile(self.fileMeta)
