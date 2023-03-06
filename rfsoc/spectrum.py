#!/usr/local/ python3

# coding: utf-8
#import sys
#sys.path.append('/usr/local/share/pynq-venv/lib/python3.8/site-packages')


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

class spectrum:
    def __init__(self,_fft_size = 4096, 
                      _decimation_factor = 2, 
                      _sub_division = 1,
                      _centre_frequency = 1024):
        self.sam = Overlay()
        self.front = self.sam.radio.receiver.channels[0].frontend.analyser
        self.rec = self.front._spectrum_analyser   
        
        # set initial values to the spectrum analyser
        self.rec.fft_size = _fft_size
        self.front.decimation_factor = _decimation_factor
        self.front.centre_frequency = _centre_frequency
        self.sub_division = _sub_division
    
        # get other parameters from the spectrum analyser class
        self.fs = 4096
        self.fft_size = self.rec.fft_size
        self.decimation_factor = self.rec.decimation_factor
        self.centre_frequency = self.rec.centre_frequency
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
        self.time_start = "11-02-22_12" # start of the dataset and time
        self.time_end = ""         # end of the dataset time
        self.time_tot = 0           # total dataset time in hours
        self.fileData = []
        self.data = []
        
    def get_frame(self):
        self.rec.dma_enable = 1
        #self.front._block.UpdateEvent(1)
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
        
    # writes input datato time stamped text file
    def write_file(self,f, _data):
        # # change permission of the file to delete as required.
        # os.chmod(path_filename, 0o777)
        
        self.data = _data.astype('float32')
        #self.data.astype('float32')
        self.data.tofile(f)
        os.chmod(self.fileData, 0o777)

    # generates max hold and time average data
    def generate_data(self):
        data = []
        for cf in self.centre_frequency_arr:
            self.front.centre_frequency = float(cf)
            self.lower_lim = self.rec.centre_frequency-(((self.fs*1e6)/self.rec.decimation_factor)/2)
            self.upper_lim = self.rec.centre_frequency+(((self.fs*1e6)/self.rec.decimation_factor)/2)
            self.rec.centre_frequency = int(cf)
            time.sleep(0.4)
            _data = np.add(np.zeros(self.fft_size),-200)
            for i in range(0,self.frames):
                tdata = self.get_frame()
                _data = np.maximum(_data, tdata)
                time.sleep(0.1)
            # concatenate  multiple scans if subdivision > 1
            data = np.concatenate((data,_data))
            # average data temporarly not used.
            #self.average = np.add(self.average, data)
        self.maxhold = data
        

    # returns max hold of generate data        
    def get_maxhold(self):
        return self.maxhold
    
    # returns average of generate data
    def get_average(self):
        return self.average/self.frames
    
    # returns window type as a string
    def get_window(self):
        return self.window_type
    # set window
    def window(self, _window):
        self.rec.window = _window
        self.window_type = self.rec.window
    
    # returns fft size
    def fftsize(self):
        return self.fft_size
    # set fft size
    def fftsize(self, _fft_size):
        self.front.fft_size = _fft_size
        self.fft_size = self.rec.fft_size
        
    # returns sub-division
    def get_sub_div(self):
        return self.sub_division
        
    # set subdivision    
    def set_sub_div(self,_sub_division):
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
        self.sub_division = _sub_division
        self.front.decimation_factor = 2**_sub_division
        self.decimation_factor = self.rec.decimation_factor
        self.data_length = self.fft_size * self.decimation_factor/2
        self.maxhold = np.add(np.zeros(int(self.data_length)),-200)
        #self.average = np.zeros(int(self.data_length))
        rate = self.fft_size/self.decimation_factor
        # generate an array of center frequencies with current decimation factor and
        # fft size to cover the whole spectrum 0 - 2 GHz.
        cf_arr = np.arange(rate,self.fft_size-1,2*rate)/2
        self.centre_frequency_arr = [int(i) for i in cf_arr]
        self.lower_lim = self.rec.centre_frequency-(((self.fs*1e6)/self.rec.decimation_factor)/2)
        self.upper_lim = self.rec.centre_frequency+(((self.fs*1e6)/self.rec.decimation_factor)/2)
        
    def write_metadata(self):
        latlng = (55.8626632,-4.2468702) # robert flat gps coordinates
        self.meta = SigMFFile(
            data_file = self.fileData, # extension is optional
            global_info = {
                SigMFFile.DATATYPE_KEY: get_data_type_str(self.data),  # in this case, 'rf32_le',
                SigMFFile.SAMPLE_RATE_KEY: self.fs,
                SigMFFile.AUTHOR_KEY: 'RFSoC 2x2',
                SigMFFile.VERSION_KEY: sigmf.__version__,
                SigMFFile.GEOLOCATION_KEY: Point((latlng)),
                

            }
        )
        self.meta.add_capture(0, metadata = {
                SigMFFile.FREQUENCY_KEY: self.centre_frequency,
                SigMFFile.DATETIME_KEY: dt.datetime.utcnow().isoformat()+'Z',
            })

        self.meta.add_annotation(0, len(self.maxhold), metadata = {
                SigMFFile.FLO_KEY: 0,
                SigMFFile.FHI_KEY: 2048000000,
            })
        self.meta.tofile(self.fileMeta)
        
        #os.chmod(self.fileMeta, 0o777)
        
        """
            currently it writes a new file for each hour, but this will be
            changed to write a single data file per dataset.
        """
        
    
    
    def continuous_scan(self):
        print("------------ CONTINUOUS ------------")
        
        mins = [0, 15, 30, 45]   # times at which to run generate data
        skip_m = []
        self.time_start = datetime.now()
        
        path_filename = 'spectrum_data/S_'
        # for single file per dataset
        #self.fileData = path_filename + self.time_start.strftime("%d-%m-%y_%H")+'.sigmf-data'
        #self.fileMeta = path_filename + self.time_start.strftime("%d-%m-%y_%H")+'.sigmf-meta'
        
        animation = "|/-\\" # animation to be removed if in boot mode.
        print(self.time_start ,flush = True)
        check = int(self.time_start.strftime("%M"))
        
        b_skip = False
        for m in mins:
            if(m < check):
                skip_m.append(m)
                b_skip = True
        if(len(mins) == len(skip_m)):
            skip_m = []
            b_skip = False
        #print(datetime.now())
        if(b_skip):
            print("skipping T"+str(skip_m))
        while (True):
            # create data file every hour
            now = datetime.now()
            
            # get 4 times 40 frames a hour
            for curr in mins:
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
                    print("  waiting for T-"+str(T)+" "+ animation[anim_idx % len(animation)]+"      ",end="\r",flush = True)
                    anim_idx += 1
                    time.sleep(0.2) # wait 0.2s animation
                    #time.sleep(60) # wait 1 min boot mode
                    now = datetime.now()
                    #if(int(now.strftime("%M")) > 3):
                    #    exit()
                        
                # generate max hold for 40 frames 
                self.generate_data()
                # update time variables
                self.time_end = datetime.now()
                print("data gathered: *"+str(self.time_end))
                # write metadata
                time.sleep(5)
            
            now = datetime.now()
            file_time = now.strftime("%d-%m-%y_%H")
            # single file per hour
            self.fileData = path_filename + file_time+'.sigmf-data'
            self.fileMeta = path_filename + file_time+'.sigmf-meta'
            with open(self.fileData, "wb") as f:
                self.write_file(f, self.get_maxhold())
            self.write_metadata()
            self.time_tot = self.time_tot + 1
            print("complete data file: " +file_time, flush=True)
            self.maxhold = np.add(np.zeros(int(self.data_length)),-200)
           
    
print("initialising...")

# set system time
# set current time and date in the following string
os.system("date -s \"25 FEB 2023 12:44:00\"")
spec = spectrum()
spec.set_sub_div(3)
print("class spectrum created.")
print("division        : "+ str(spec.sub_division))
print("decimation factor: "+ str(spec.decimation_factor))
print("center_frequency: "+ str(spec.rec.centre_frequency))
print("cf array        : "+ str(spec.centre_frequency_arr))
print("window type     : "+ spec.get_window())
print("fft size        : "+ str(spec.fft_size))
print("Upper and lower limit: "+ str(spec.upper_lim) +",     " +str(spec.lower_lim))
spec.continuous_scan()

#spec.generate_data()
#print("data generated.")
#data = spec.get_maxhold()
#data = spec.get_average()
#print("values returned.")
#spec.write_file(data,"testspectrum.txt")
#print("file written.")

