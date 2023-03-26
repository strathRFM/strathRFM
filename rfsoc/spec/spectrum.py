#!/usr/local/ python3

# coding: utf-8
#import sys
#sys.path.append('/usr/local/share/pynq-venv/lib/python3.8/site-packages')
"""
Author: Robert A Incze, shullat
Date:
Description:
"""

# In[1]:
import matplotlib
matplotlib.use("Agg")     # to disable matplotlib error from console.

import numpy as np
from datetime import datetime
import time 
import os
from pynq.overlays.base import BaseOverlay
from rfsoc_sam.overlay import Overlay
import sigmf
from sigmf import SigMFFile
from sigmf.utils import get_data_type_str
import geojson
from geojson import Point
import datetime as dt
import pickle

class spectrum:
    def __init__(self,_fft_size = 4096, 
                      _decimation_factor = 2, 
                      _sub_div = False,
                      _centre_frequency = 1024,
                      _coordinates = (55.86126, -4.24646) ):
        # default coordinates UoS Royal Collage
        self.sam = Overlay()
        self.front = self.sam.radio.receiver.channels[0].frontend.analyser
        self.rec = self.front._spectrum_analyser   
        
        # set initial values to the spectrum analyser
        self.rec.fft_size = _fft_size
        self.front.decimation_factor = _decimation_factor
        self.front.centre_frequency = _centre_frequency
        self.sub_div = _sub_div
    
        # get other parameters from the spectrum analyser class
        self.fs = self.rec.sample_frequency
        self.fft_size = self.rec.fft_size
        self.decimation_factor = self.rec.decimation_factor
        self.centre_frequency = self.front.centre_frequency
        self.centre_frequency_arr = [self.centre_frequency]
        self.units = self.rec.spectrum_units
        self.lower_lim = self.centre_frequency-((self.fs/self.decimation_factor)/2)
        self.upper_lim = self.centre_frequency+((self.fs/self.decimation_factor)/2)
        self.step = (self.upper_lim - self.lower_lim)/self.fft_size
        self.window_type = self.rec.window
        
        self.data_length = int(self.fft_size * self.decimation_factor/2)
        # initialise max hold and time average parameters
        self.frames = 60
        self.maxhold = np.add(np.zeros(self.data_length),-200)
        #self.data_fmt = '%1.9f' # float to 3 decimal places
        # instance info
        self.coordinates = _coordinates
        self.time_start = "11-02-22_12" # start of the dataset and time
        self.time_end = ""         # end of the dataset time
        self.time_tot = 0           # total dataset time in hours
        self.fileData = []
        self.data = []
        self.mins = [0, 15, 30, 45]
        
    # Setters and getters    
    
    # set mins
    def set_mins(self, _mins):
        self.mins = _mins
        
    # get mins
    def get_mins(self):
        return self.mins
    
    # set coordinates
    def set_coordinates(self,_coor):
        self.coordinates = _coor
        
     # get coordinates
    def get_coordinates(self):
        return self.coordinates
    
    # get upper_lim
    def get_upper_lim(self):
        self.upper_lim = self.rec.centre_frequency+((self.fs/self.rec.decimation_factor)/2)
        return self.rec.centre_frequency+((self.fs/self.rec.decimation_factor)/2)
    
    # get lower_lim
    def get_lower_lim(self):
        self.lower_lim = self.rec.centre_frequency-((self.fs/self.rec.decimation_factor)/2)
        return self.rec.centre_frequency-((self.fs/self.rec.decimation_factor)/2)
    
    # set number of frames
    def set_frames_number(self,_frames):
        self.frames = _frames
    
    # get number of frames
    def get_frames_number(self):
        return self.frames
    
    # returns max hold of generate data        
    def get_maxhold(self):
        return self.maxhold
    
    # returns window type as a string
    def get_window(self):
        return self.window_type
    
    # set window (refere to rfsoc_sam for names) 
    def set_window(self, _window):
        self.rec.window = _window
        self.window_type = self.rec.window
    
    # set spectrum usits (refere to rfsoc_sam for names)
    def set_spectrum_units(self, _units):
        self.rec.spectrum_units = _units
        self.units = self.rec.spectrum_units
        
    # get spectrum units
    def get_spectrum_units(self):
        return self.units
    
    # returns fft size
    def get_fftsize(self):
        return self.fft_size
    # set fft size
    def set_fftsize(self, _fft_size):
        self.front.fftsize = _fft_size
        self.fft_size = self.rec.fft_size
        
    # returns centre frequency 
    def get_centre_frequency(self):
        if(self.sub_div):
            return self.centre_frequency_arr
        else:
            return self.centre_frequency
        
    # set centre frequency
    def set_centre_frequency(self, _centre_frequency):
        self.front.centre_frequency = _centre_frequency
        self.centre_frequency = self.front.centre_frequency
        self.set_sub_div(False) # update subdivision
        
    # set cdecimation factor
    def set_decimation_factor(self, _decimation_factor):
        self.front.decimation_factor = _decimation_factor
        self.decimation_factor = self.rec.decimation_factor
        self.set_sub_div(self.sub_div) # update subdivision
    
    def get_decimation_factor(self):
        return self.decimation_factor
        
    # Other functionalities
         
    def get_frame(self):
        self.rec.dma_enable = 1
        _data = self.rec.get_frame()
        self.rec.dma_enable = 0
        
        # flip spectum
        center = int(self.fft_size/2)
        data1 = _data[center:]
        data2 = _data[:center]
        _data = []
        _data = np.hstack((data1,data2))
        _data = [float(i) for i in _data]
        
        # return spectrum data
        return _data
        
    # writes input data to time stamped text file
    def write_file(self,f, _data):
        # # change permission of the file to delete as required.
        # os.chmod(path_filename, 0o777)
        
        self.data = _data.astype('float32')
        self.data.tofile(f)
        os.chmod(self.fileData, 0o777)

    # generates max hold and time average data
    def generate_data(self):
        data = []
        print("generating data for frames: "+str(self.frames), end=" ", flush = True)
        for cf in self.centre_frequency_arr:
            self.front.centre_frequency = float(cf)
            if(self.sub_div):
                self.lower_lim = self.rec.centre_frequency-((self.fs/self.rec.decimation_factor)/2)
                self.upper_lim = self.rec.centre_frequency+((self.fs/self.rec.decimation_factor)/2)
            time.sleep(0.4)
            _data = np.add(np.zeros(self.fft_size),-200)
            for i in range(0,self.frames):
                tdata = self.get_frame()
                _data = np.maximum(_data, tdata)
                time.sleep(0.1)
            # concatenate  multiple scans if subdivision > 1
            data = np.concatenate((data,_data))
            # average data temporarly not used.
        self.maxhold = data
        print(" ", end="\r", flush = True)
   
    # returns sub-division
    def get_sub_div(self):
        return self.sub_div
        
    # set subdivision    
    def set_sub_div(self,_sub_div):
        """
        To generate more accurate scan the spectrum can be scanned
        with higher accuracy by increasing the decimation factor
        and appending multiple scans of the spectrum.
        e.g. the whole spectrum can be scanned with a decimation factor
        of 2 and and fft of 4096 generating 4096 samples per spectrum.
        With a decimation factor of 4 and fft 4096, the spectrum 
        scanned halves. therefore the center frequency can be shifted to
        1/4 th of the spectrum and 3/4 ths of the spectrum and scanned twice
        the subdivision variable will atomatically determine the decimation factor.
        given by: decimation factor = 2^div
        """
        self.sub_div = _sub_div
        if(self.sub_div):
            self.data_length = self.fft_size * self.decimation_factor/2
            self.maxhold = np.add(np.zeros(int(self.data_length)),-200)
            rate = self.fft_size/self.decimation_factor

            # generate an array of center frequencies with current decimation factor and
            # fft size to cover the whole spectrum 0 - 2 GHz.
            cf_arr = np.arange(rate,self.fft_size-1,2*rate)/2
            self.centre_frequency_arr = [int(i) for i in cf_arr]
            self.lower_lim = self.rec.centre_frequency-((self.fs*1e6)/4)
            self.upper_lim = self.rec.centre_frequency+((self.fs*1e6)/4)
        else:
            self.centre_frequency_arr = [self.centre_frequency]
            self.lower_lim = self.rec.centre_frequency-(((self.fs*1e6)/self.rec.decimation_factor)/2)
            self.upper_lim = self.rec.centre_frequency+(((self.fs*1e6)/self.rec.decimation_factor)/2)
        
    def write_metadata(self):
        latlng = self.coordinates
        self.meta = SigMFFile(
            data_file = self.fileData, # extension is optional
            global_info = {
                SigMFFile.DATATYPE_KEY: get_data_type_str(self.data),  # in this case, 'rf32_le',
                SigMFFile.SAMPLE_RATE_KEY: self.fs,
                SigMFFile.AUTHOR_KEY: 'RFSoC',
                SigMFFile.VERSION_KEY: sigmf.__version__,
                SigMFFile.GEOLOCATION_KEY: Point((latlng)),
            }
        )
        self.meta.add_capture(0, metadata = {
                SigMFFile.FREQUENCY_KEY: self.centre_frequency,
                SigMFFile.DATETIME_KEY: dt.datetime.utcnow().isoformat()+'Z',
            })

        self.meta.add_annotation(0, len(self.maxhold), metadata = {
                SigMFFile.FLO_KEY: self.lower_lim,
                SigMFFile.FHI_KEY: self.upper_lim,
            })
        self.meta.tofile(self.fileMeta)
        
        os.chmod(self.fileMeta, 0o777)
        
        """
            currently it writes a new file for each hour, but this will be
            changed to write a single data file per dataset.
        """
        
    def unpickleFile(self):
        idx = 0
        res = False
        cont_scan = True
        while(res == False):
            try:
                with open('config.pkl', 'rb') as fo:
                    dict = pickle.load(fo, encoding='bytes')
                    cont_scan = dict[b'continuous_scan_enable']
                    res = True
            except:
                idx += 1
                if(idx >10):
                    break
                time.sleep(0.001)
        return res, cont_scan
    
    def continuous_scan(self):
        print("------------ CONTINUOUS ------------")
        print("|current spectrum settings:        |")
        print("------------------------------------")
        print("division enable   : "+ str(self.get_sub_div()))
        print("decimation factor : "+ str(self.decimation_factor))
        print("center_frequency  : "+ str(self.rec.centre_frequency))
        print("cf array          : "+ str(self.centre_frequency_arr))
        print("window type       : "+ str(self.get_window()))
        print("fft size          : "+ str(self.fft_size))
        print("Mins array        : "+ str(self.mins))
        print("Upper and lower limit: "+ str(self.upper_lim) +",     " +str(self.lower_lim))
        print("------------------------------------")
        _mins = self.mins   # times at which to run generate data
        skip_m = []
        self.time_start = datetime.now()
        cont_scan = True
        path_filename = 'spectrum_data/S_'
        
        animation = "|/-\\" # animation to be removed if in boot mode.
        # disable in boot mode.
        print(self.time_start ,flush = True)
        check = int(self.time_start.strftime("%M"))
        
        b_skip = False
        for m in _mins:
            if(m < check):
                skip_m.append(m)
                b_skip = True
        if(len(_mins) == len(skip_m)):
            skip_m = []
            b_skip = False
        # disable whole if statement if in boot mode
        if(b_skip):
            print("skipping T"+str(skip_m))
        while (cont_scan):
            # create data file every hour
            now = datetime.now()
            
            # get 4 times 40 frames a hour
            for curr in _mins:
                if(b_skip):
                    if(skip_m == []):
                        b_skip = False
                    else:
                        skip_m.pop(0)
                        continue
                
                anim_idx = 0        # anim index init
                while(curr != int(now.strftime("%M"))):
                    # animation visualisation
                    T = curr - int(now.strftime("%M"))
                                                        
                    # disable in boot mode
                    print("  waiting for T-"+str(T)+" "+ animation[anim_idx % len(animation)]+"            ",end="\r",flush = True)
                    anim_idx += 1
                    time.sleep(0.2) # wait 0.2s animation
                    #time.sleep(60) # wait 1 min boot mode
                    now = datetime.now()
                    #if(int(now.strftime("%M")) > 3):
                    _,cont_scan = self.unpickleFile()
                    if(cont_scan == False):
                        print("exit encountered...")
                        break
                        
                # generate max hold for 40 frames 
                self.generate_data()
                # update time variables
                self.time_end = datetime.now()
                # disable in boot mode    
                print("data gathered: *"+str(self.time_end), end="\r", fluash=True)
                # write metadata
                if(cont_scan == False):
                        break
                
            now = datetime.now()
            file_time = now.strftime("%d-%m-%y_%H")
            # single file per hour
            self.fileData = path_filename + file_time+'.sigmf-data'
            self.fileMeta = path_filename + file_time+'.sigmf-meta'
            with open(self.fileData, "wb") as f:
                self.write_file(f, self.get_maxhold())
            os.chmod(self.fileData, 0o777)    
            self.write_metadata()
            self.time_tot = self.time_tot + 1
            print("complete data file: " +file_time + " total data points:" + str(self.time_tot), flush=True)
            self.maxhold = np.add(np.zeros(int(self.data_length)),-200)
