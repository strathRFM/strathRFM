#!/usr/local/ python3

# coding: utf-8

#import "spectrum.py"
import pickle
import time
import numpy as np
import os
from datetime import datetime

class SpecCTRL:
    def __init__(self,_config_Path = "config.pkl", # path to the configuration file writable by GUI
                 _spec_Data_Stream_Path = "data.pkl" ):  # path of data file writable from this calss
                 
        self.config_Path = _config_Path
        self.spec_Data_Stream_Path = _spec_Data_Stream_Path
        self.spec = spectrum()
        self.start_on_boot = True
        self.continuous_scan_enable = False
        self.stream_data_enable = False
        self.single_frame_enable = False
        self.app_enable = True         # continuously check if system needs to run.
                                       # if False exit specCTRL class and continue with boot.
        
        # Spectrum class default values
        self.full_spectrum_scan = False # enable full spectrum scan
        self.fft_size = self.spec.get_fftsize()
        self.mins = self.spec.get_mins()
        self.centre_frequency = self.spec.get_centre_frequency()
        self.decimation_factor = self.spec.get_decimation_factor()
        self.units = self.spec.get_spectrum_units()
        self.window = self.spec.get_window()
        self.frame_number = self.spec.get_frames_number()
        self.coordinates = self.spec.get_coordinates()
        self.date_time = datetime.now()
        
    def continuous_scan(self):
        # need to modify continuous scan to only progress if 
        self.spec.continuous_scan()
       
    def unpickleFile(self, file_path):
        idx = 0
        res = False
        while(res == False):
            try:
                with open(file_path, 'rb') as fo:
                    dict = pickle.load(fo, encoding='bytes')
                    res = True
            except:
                idx += 1
                if(idx >10):
                    break
                time.sleep(0.001)
                dict = {}
                res =  False
        return res, dict
            
    def pickleFile(self, file_path, data):
        idx = 0
        res = False
        while(res == False):
            try:
                pickle.dump(data, open(file_path, 'wb'))
                res = True
            except:
                idx += 1
                if(idx >10):
                    break
                time.sleep(0.001)
                res = False
        return res
        
    def create_config(self,_changed):
        config_file = {b'changed':_changed,
                      b'continuous_scan_enable': self.continuous_scan_enable,
                      b'mins':self.mins,
                      b'single_frame_enable':self.single_frame_enable,
                      b'start_on_boot': self.start_on_boot,
                      b'full_spectrum_scan':self.full_spectrum_scan,
                      b'app_enable':self.app_enable,
                      b'stream_data_enable':self.stream_data_enable,
                      b'fft_size':self.fft_size,
                      b'center_frequency':self.centre_frequency,
                      b'decimation_factor':self.decimation_factor,
                      b'units': self.units,
                      b'window':self.window,
                      b'frame_number':self.frame_number,
                      b'coordinates':self.coordinates,
                      b'date_time':self.date_time}
        res = self.pickleFile(self.config_Path, config_file)
    
    def check_config(self):
        # this function loads in the config file and updates class variables
        res, config_file = self.unpickleFile(self.config_Path)
        if(config_file[b'changed'] == True):
            
            if(self.continuous_scan_enable != config_file[b'continuous_scan_enable']):
                self.continuous_scan_enable = config_file[b'continuous_scan_enable']
                
            if(self.single_frame_enable != config_file[b'single_frame_enable']):
                self.single_frame_enable = config_file[b'single_frame_enable']
                
            if(self.stream_data_enable != config_file[b'stream_data_enable']):
                self.stream_data_enable = config_file[b'stream_data_enable']
                
            if(self.start_on_boot != config_file[b'start_on_boot']):
                self.start_on_boot = config_file[b'start_on_boot']
                
            if(self.app_enable != config_file[b'app_enable']):
                self.app_enable = config_file[b'app_enable']
            
            # check other spectrum parameters
            if(self.full_spectrum_scan != config_file[b'full_spectrum_scan']):
                self.spec.set_sub_div(config_file[b'full_spectrum_scan'])
                self.full_spectrum_scan = self.spec.get_sub_div()
                
            if(self.mins != config_file[b'mins']):
                self.spec.set_mins(config_file[b'mins'])
                self.mins = self.spec.get_mins()
                
            if(self.fft_size != config_file[b'fft_size']):
                self.spec.set_fftsize(config_file[b'fft_size'])
                self.fft_size = self.spec.get_fftsize()
            
            if(self.center_frequency != config_file[b'center_frequency']):
                self.spec.set_center_frequency(config_file[b'center_frequency'])
                self.center_frequency = self.spec.get_center_frequency()
                
            if(self.decimation_factor != config_file[b'decimation_factor']):
                self.spec.set_decimation_factor(config_file[b'decimation_factor'])
                self.decimation_factor = self.spec.get_decimation_factor()
                
            if(self.units != config_file[b'units']):
                self.spec.set_spectrum_units(config_file[b'units'])
                self.units = self.spec.get_spectrum_units()
                
            if(self.window != config_file[b'window']):
                self.spec.set_window(config_file[b'window'])
                self.window = self.spec.get_window()
                
            if(self.frame_number != config_file[b'frame_number']):
                self.spec.set_frame_number(config_file[b'frame_number'])
                self.frame_number = self.spec.get_frame_number()
                
            if(self.coordinates != config_file[b'coordinates']):
                self.spec.set_coordinates(config_file[b'coordinates'])
                self.coordinates = self.spec.get_coordinates()
            
            if(self.date_time != config_file[b'date_time']):
                self.date_time = self.set_time(config_file[b'date_time'])
            
            self.create_config(False)
    
    
    def set_time(_time):
        os.system("date -s \""+str(_time)+"\"");
    
    def spec_get_frame(self):
        data = self.spec.get_frame()
        toFile = {b'upper_lim': self.spec.get_upper_lim(),
                  b'lower_lim': self.spec.get_lower_lim(),
                  b'data': data}
        self.pickleFile(self.spec_Data_Stream_Path,toFile)
    
    def send_spec_data(self):
        while(self.stream_data_enable):
            self.spec_get_frame()
            self.check_config()
                
        
    def start_CTRL(self):
        if(os.path.isfile(self.config_Path) != True):
            self.create_config(True)
        while(self.app_enable):
            if(self.continuous_scan_enable):
                # background gather data for dataset
                print("continuous scan enabled.")
                self.continuous_scan()
                
            if(self.stream_data_enable):
                # send data to GUI trough stream data file.
                print("sending data to GUI.")
                self.send_spec_data()
                
            if(self.single_frame_enable):
                self.spec_get_frame()
                self.single_frame_enable = False
                self.create_config(False)
            #time.sleep(4)
            self.check_config()
            
ctrl = SpecCTRL()
ctrl.start_CTRL()
