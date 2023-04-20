#!/usr/local/ python3
# coding: utf-8

"""
Author: Robert A Incze, Jakub Olszewski
Date: 14/03/2023
Description: SpecCTRL class, controlling the spectrum class using the configuration file.
            By editing the available dictionary elements within the config.pkl file, this 
            class detects is changes have been made to the file and updates the parameters
            of the spectrum analyser. It has methods for dataset generation and single
            frame generation. While the "continuous scan" generates sigMF diles on the 
            device, the get_frame function saves a data.pkl file holding the spectrum
            power spectra in a dictionary. The get frame function can be polled and easily
            implemented trough external software to generate dataset, live view or more.
"""

import pickle
import time
import numpy as np
import os
from datetime import datetime
from spectrum import spectrum

# spectrum analyser controll class
class SpecCTRL:
    def __init__(self,_config_Path = "/home/xilinx/jupyter_notebooks/strathRFM/config.pkl", # path to the configuration file writable by GUI
                 _spec_Data_Stream_Path = "/home/xilinx/jupyter_notebooks/strathRFM/data.pkl" ):  # path of data file writable from this calss
                 
        self.config_Path = _config_Path
        self.spec_Data_Stream_Path = _spec_Data_Stream_Path
        self.spec = spectrum()
        self.status = "running..."
        self.start_on_boot = True
        self.continuous_scan_enable = False
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
        self.enable_time = False
        self.date_time = datetime.now()
    
    # initialises the spectrum classes continuous scan method.    
    def continuous_scan(self):
        self.spec.continuous_scan()
       
    # read in pickle file.
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
    
    # write pickle file.
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
        
    # writes the config file with the current settings.
    def create_config(self,_changed):
        config_file = {b'changed':_changed,
                      b'status': self.status,
                      b'continuous_scan_enable': self.continuous_scan_enable,
                      b'mins':self.mins,
                      b'single_frame_enable':self.single_frame_enable,
                      b'start_on_boot': self.start_on_boot,
                      b'full_spectrum_scan':self.full_spectrum_scan,
                      b'app_enable':self.app_enable,
                      b'fft_size':self.fft_size,
                      b'centre_frequency':self.centre_frequency,
                      b'decimation_factor':self.decimation_factor,
                      b'units': self.units,
                      b'window':self.window,
                      b'frame_number':self.frame_number,
                      b'coordinates':self.coordinates,
                      b'enable_time':self.enable_time,
                      b'date_time':self.date_time}
        res = self.pickleFile(self.config_Path, config_file)
    
    # Inspect the configuration file and compare with local variables to detect
    # if any changes are required to be made, if so, make the changes.
    def check_config(self):
        # this function loads in the config file and updates class variables
        res, config_file = self.unpickleFile(self.config_Path)
        
        
        # system time update as a separate process.
        if(config_file[b'enable_time']):
            self.set_time(str(config_file[b'date_time']))
            self.enable_time = False
            self.create_config(False)
            print("System time updated: " + str(datetime.now()))
        
        # Spectrum and dataset generation settings
        if(config_file[b'changed'] == True):
            
            print("updating settings...   ")
            if(self.continuous_scan_enable != config_file[b'continuous_scan_enable']):
                self.continuous_scan_enable = config_file[b'continuous_scan_enable']
                print("-continuous scan:" + str(self.continuous_scan_enable))
                
            if(self.single_frame_enable != config_file[b'single_frame_enable']):
                self.single_frame_enable = config_file[b'single_frame_enable']
                print("-single frame enable: " + str(self.single_frame_enable))
                
                
            if(self.start_on_boot != config_file[b'start_on_boot']):
                self.start_on_boot = config_file[b'start_on_boot']
                print("-start on boot:" + str(self.start_on_boot))
                
            if(self.app_enable != config_file[b'app_enable']):
                self.app_enable = config_file[b'app_enable']
                print("-app enable: " + str(self.app_enable))
            
            # check other spectrum parameters
            if(self.full_spectrum_scan != config_file[b'full_spectrum_scan']):
                self.spec.set_sub_div(config_file[b'full_spectrum_scan'])
                self.full_spectrum_scan = self.spec.get_sub_div()
                print("-full spectrum scan enable: " + str(self.full_spectrum_scan))
                
            if(self.mins != config_file[b'mins']):
                self.spec.set_mins(config_file[b'mins'])
                self.mins = self.spec.get_mins()
                print("-minutes to scan: " + str(self.mins ))
                
            if(self.fft_size != config_file[b'fft_size']):
                self.spec.set_fftsize(config_file[b'fft_size'])
                self.fft_size = self.spec.get_fftsize()
                print("-FFT size: " + str(self.fft_size))
            
            if(self.centre_frequency != config_file[b'centre_frequency']):
                print("-old: " + str(self.spec.get_centre_frequency()))
                self.spec.set_centre_frequency(config_file[b'centre_frequency'])
                self.centre_frequency = self.spec.get_centre_frequency()
                print("-centre frequency: " + str(self.centre_frequency))
                
            if(self.decimation_factor != config_file[b'decimation_factor']):
                self.spec.set_decimation_factor(config_file[b'decimation_factor'])
                self.decimation_factor = self.spec.get_decimation_factor()
                print("-decimation factor: " + str(self.decimation_factor))
                
            if(self.units != config_file[b'units']):
                self.spec.set_spectrum_units(config_file[b'units'])
                self.units = self.spec.get_spectrum_units()
                print("-units: " + str(self.units))
                
            if(self.window != config_file[b'window']):
                self.spec.set_window(config_file[b'window'])
                self.window = self.spec.get_window()
                print("-window type: " + str(self.window))
                
            if(self.frame_number != config_file[b'frame_number']):
                self.spec.set_frames_number(config_file[b'frame_number'])
                self.frame_number = self.spec.get_frames_number()
                print("-number of frames: " + str(self.frame_number))
                
            if(self.coordinates != config_file[b'coordinates']):
                self.spec.set_coordinates(config_file[b'coordinates'])
                self.coordinates = self.spec.get_coordinates()
                print("-coordinates: " + str(self.coordinates))
            
            # update device time on config file
            self.date_time = datetime.now()
            
            self.create_config(False)
            print("update settings complete.")
    
    # update device time method using linux command.
    def set_time(self,_time):
        os.system("date -s \""+_time+"\"");
        self.date_time = datetime.now()
    
    # generate spectrum data using get frame if frame is set to 1
    # otherwise use generate data for max hold.
    def spec_get_frame(self):
        self.single_frame_enable = False
        self.create_config(False)
        if(self.frame_number == 1):
            data = self.spec.get_frame()
            toFile = {b'upper_lim': self.spec.get_upper_lim(),
                      b'lower_lim': self.spec.get_lower_lim(),
                      b'data': data}
            time.sleep(0.1)
        else:
            self.spec.generate_data()
            data = self.spec.get_maxhold()
            toFile = {b'upper_lim': self.spec.get_upper_lim(),
                      b'lower_lim': self.spec.get_lower_lim(),
                      b'data': data}
        self.pickleFile(self.spec_Data_Stream_Path,toFile)
                
    # main control method that controls mode of operation.
    def start_CTRL(self):
        animation = "|/-\\" # animation to be removed if in boot mode.
        anim_idx = 0        # anim index init
        if(os.path.isfile(self.config_Path) != True):
            print("ceated config file.")
            self.create_config(True)
        print("spectrum CTRL initialiased.")
        
        while(self.app_enable):
            if(self.continuous_scan_enable):
                self.status = "continuous scan - running..."
                # background gather data for dataset
                print("continuous scan enabled.")
                self.create_config(False)
                self.continuous_scan()
                
            if(self.single_frame_enable):
                self.spec_get_frame()
                
            self.check_config()
            if(self.status != "idle - running..."):
                self.status = "idle - running..."
                self.create_config(False)
            print("  waiting "+ animation[anim_idx % len(animation)]+"               ",end="\r",flush = True)
            anim_idx += 1
            time.sleep(0.2)
            
        self.status = "SpecCTRL exited. Please run SpecCTRL to use strathRFM."
        self.create_config(False)
        print("exited.                             ")
 
# create class and run. 
ctrl = SpecCTRL()
ctrl.start_CTRL()
