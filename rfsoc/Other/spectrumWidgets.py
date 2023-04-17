#!/usr/bin/env python
# coding: utf-8

"""
    Author: Robert Incze
    Date: 26/03/2023
    Description: control class, that enables interactive editing of the config.pkl file in turn controlling the 
                specCTRL and the spectrum analyser.
"""


import pickle
import matplotlib.pyplot as plt
import time
from datetime import datetime
import collections
import numpy as np
import re
from IPython.display import clear_output
import ipywidgets as widgets
from ipywidgets import Button, HBox, VBox, Label, Layout
from IPython.display import display
import math
   
    
    
def create_config():
    config_file = {b'changed':True,
                  b'status': "config file generated.",
                  b'continuous_scan_enable': False,
                  b'single_frame_enable':False,
                  b'start_on_boot': False,
                  b'full_spectrum_scan':False,
                  b'app_enable': True,
                  b'mins':[0,15,30,45],
                  b'fft_size':4096,
                  b'centre_frequency':1024,
                  b'decimation_factor':4,
                  b'units': 'dBFS',
                  b'window':'hamming',
                  b'frame_number':60,
                  b'coordinates':(0,0),
                  b'enable_time':False,
                  b'date_time':datetime.now()}
    res = pickleFile('config.pkl', config_file)
    
def unpickleFile(file_path):
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
            
def pickleFile(file_path, data):
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
    #comment
###################################################################################################
class spectrumWidgets:
    def __init__(self,_config_Path = "/home/xilinx/jupyter_notebooks/strathRFM/config.pkl", # path to the configuration file writable by GUI
                 _spec_Data_Stream_Path = "/home/xilinx/jupyter_notebooks/strathRFM/data.pkl" ):  # path of data file writable from this calss
        
        self.config_Path = _config_Path
        self.data_Path = _spec_Data_Stream_Path
        _, self.f = unpickleFile(self.config_Path);
        self.out = widgets.Output(layout={'border': '1px solid black'})
        self.full_scan = widgets.Checkbox(description = 'Full Scan',
                                          value = self.f[b'full_spectrum_scan'],
                                         indent = False,
                                         layout=Layout(width = '50%'))
        self.get_frame = widgets.Button(description='get Frame')
        self.push_settings = widgets.Button(description='Push settings', indent = True)
        # radio buttons
        self.rad = widgets.RadioButtons(
                        options=['continuous scan', 'idle'],
                        value=self.set_radio_val(), # Defaults to 'pineapple'
                    #    layout={'width': 'max-content'}, # If the items' names are long
                        description='MODE:',
                        layout = self.full_scan.layout,
                        disabled=False
        )
        
        # boot
        self.boot = widgets.Button(description='start on boot')
        if(self.f[b'start_on_boot']):
            self.boot.style.button_color = 'lightgreen'
        else:
            self.boot.style.button_color = 'lightblue'
            
        # app enable
        self.app_enable = widgets.Button(description='app enable')
        if(self.f[b'app_enable']):
            self.app_enable.style.button_color = 'lightgreen'
        else:
            self.app_enable.style.button_color = 'lightblue'
            self.rad.disabled=True
            self.get_frame.disabled=True
        
        # spectrum definitions
        self.center_frequency = widgets.Text(
            value= str(int(self.f[b'centre_frequency'])),
            placeholder='integer',
            description='Centre freq:',
            disabled=False,
            indent=True
        )

        self.mins = widgets.Text(
            value= str(self.f[b'mins']),
            placeholder='[0, val, 59] - incremental',
            description='Minutes:',
            disabled=False,
            indent=True
        )
        self.fft_size = widgets.Dropdown(
            options=['64','128', '256', '512', '1024', '2048', '4096', '8192' ],
            value=str(self.f[b'fft_size']),
            description='FFT size:',
            disabled=False,
            indent=True
        )
        self.decimation_factor = widgets.Dropdown(
            options=['2', '4', '8', '16','32','64'],
            value=str(self.f[b'decimation_factor']),
            description='DF:',
            disabled=False,
            indent=True
        )
        self.window = widgets.Dropdown(
            options=['rectangular','bartlett' ,'hamming', 'hanning', 'blackman'],
            value=str(self.f[b'window']),
            description='Window:',
            hover = 'Window type to be used when computing FFT',
            disabled=False,
            indent=True
        )
        self.units = widgets.Dropdown(
            options=['dBFS', 'dBm'],
            value=str(self.f[b'units']),
            description='Spec Units:',
            disabled=False,
            indent=True
        )
        self.frames = widgets.Text(
            value= str(self.f[b'frame_number']),
            placeholder='please input a number',
            description='Frames:',
            disabled=False,
            indent=True
        )
        self.coordinates = widgets.Text(
            value= str(self.f[b'coordinates']),
            placeholder='(latitude,longitude)',
            description='Coordinates:',
            disabled=False,
            indent=True
        )
        self.device_time = widgets.Text(
            value= str(self.f[b'date_time']),
            description='Device Time:',
            disabled=True,
            indent=True
        )
        self.time = widgets.Button(description='update device time')
        self.pickdate = widgets.DatePicker(
            description='Local time:',
            disabled=False,
            value = datetime.now().date(),
            indent = True
        )
        self.picktime = widgets.Text(
            disabled=False,
            value = datetime.now().strftime("%H:%M"),
            layout=Layout(width='80px', height='38px')
        )
    # definitions
        
    def set_radio_val(self):
        
        if(self.f[b'continuous_scan_enable']):
            self.get_frame.disabled=True
            self.full_scan.disabled = False
            return 'continuous scan'
        else:
            self.get_frame.disabled=False
            self.full_scan.disabled = True
            return 'idle'
        
    def AppLayout(self):
        
        data = {b'data': [-130,0,-70,-100,-70,0,-130], b'lower_lim': -1, b'upper_lim': 2}
        self.live_plot(data)   
            
        
        # define system settings
        Tbuttons = HBox([self.boot,self.app_enable, self.get_frame],layout={'border': '1px solid black'})
        
        self.L = VBox([Label("strathRFM System Settings:"),
                       Tbuttons,
                       HBox([self.rad,self.full_scan]),
                       Label("Spectrum Settings: "),
                       HBox([self.center_frequency,Label("(Mhz)")]),
                       self.fft_size,
                       self.decimation_factor,
                       self.window,
                       HBox([self.units,Label("(Spectrum computed)")]),
                       self.mins,
                       HBox([self.frames,Label("(per sample)")]),
                       HBox([self.coordinates,Label("(Lat,Long)")]),
                       HBox([Label("To update Spectrum settings - ", indent = True),self.push_settings]),
                       VBox([HBox([self.pickdate,self.picktime]), HBox([self.device_time,self.time])],layout={'border': '1px solid black'}),
                      ],
                      layout={'border': '1px solid black'})
        
        # on clicks and updates
        self.boot.on_click(self.update_boot)
        self.app_enable.on_click(self.update_app_enable)
        self.push_settings.on_click(self.update_settings)
        self.get_frame.on_click(self.update_frame)
        self.full_scan.observe(self.update_full_scan, names = 'value')
        self.rad.observe(self.update_mode, names='value')
        self.time.on_click(self.update_time)
        self.center_frequency.observe(self.clear_setting_button, names='value')
        self.fft_size.observe(self.clear_setting_button, names='value')
        self.decimation_factor.observe(self.clear_setting_button, names='value')
        self.window.observe(self.clear_setting_button, names='value')
        self.units.observe(self.clear_setting_button, names='value')
        self.mins.observe(self.clear_setting_button, names='value')
        self.frames.observe(self.clear_setting_button, names='value')
        self.coordinates.observe(self.clear_setting_button, names='value')
        
        # display
        display(HBox([self.L,self.out]))
        
        
    def update_settings(self,b):
        self.f[b'changed'] = True
        self.f[b'single_frame_enable'] = False
        
        res, err = self.covert_check_write()
        
        if(res):
            self.push_settings.style.button_color = 'lightgreen'
            self.f[b'changed'] = False
        else:
            print(err)
            self.f[b'changed'] = False
        
    def update_time(self,b):
        self.f[b'enable_time'] = True
        
        res, err = self.covert_check_write()
        if(res):
            self.time.style.button_color = 'lightgreen'
            self.f[b'enable_time'] = False
    
    def update_frame(self,b):
        self.f[b'single_frame_enable'] = True    
        self.f[b'changed'] = True  
        res, err = self.covert_check_write()
        if res:
            self.f[b'single_frame_enable'] = False   
        sleeptime = 0.3
        if int(self.frames.value)> 1:
            sleeptime += 0.4 + 0.1 *int(self.frames.value)
        time.sleep(sleeptime)
        res, data = unpickleFile(self.data_Path)
        if(res):
            self.live_plot(data) 
            self.f[b'changed'] = False  
    def update_boot(self,b):
        val = self.f[b'start_on_boot']
        self.f[b'start_on_boot'] = not val
        if(self.f[b'start_on_boot']):
            self.boot.style.button_color = 'lightgreen'
        else:
            self.boot.style.button_color = 'lightblue'
        
        self.f[b'single_frame_enable'] = False    
        res, err = self.covert_check_write()
        if res:
            self.f[b'changed'] = False    
        
    get_ipython().run_line_magic('matplotlib', 'inline')
    def live_plot(self,data_dict, figsize=(8,7), title=''):
        with self.out:
            clear_output(wait=True)
            plt.figure(figsize=figsize)
            x = np.linspace(data_dict[b'lower_lim'], data_dict[b'upper_lim'], len(data_dict[b'data']))
            plt.plot(x/1e6,data_dict[b'data'])
            plt.title(title)
            plt.grid(True)
            plt.xlabel('Frequency [MHz]')
            plt.ylabel(self.f[b'units'])
            plt.ylim([-140,0])
            plt.show()
            print("Upper limit     (Hz): "+str(data_dict[b'upper_lim']))
            print("Lower limit     (Hz): "+str(data_dict[b'lower_lim']))
            print("Plot resolution (Hz): "+str((data_dict[b'upper_lim'] - data_dict[b'lower_lim'])/len(data_dict[b'data'])))
            print("time                : "+str(datetime.now()))
            print("RFSoC status        : "+str(self.f[b'status']))
        
    def update_app_enable(self,b):
        val = self.f[b'app_enable']
        self.f[b'app_enable'] = not val
        if(self.f[b'app_enable']):
            self.app_enable.style.button_color = 'lightgreen'
            self.rad.disabled = False
            self.get_frame.disabled=False
            # os.system(start specCTRL class background)
        else:
            self.app_enable.style.button_color = 'lightblue'
            self.f[b'continuous_scan_enable'] = False
            self.rad.value = 'idle'
            self.rad.disabled = True
            self.get_frame.disabled=True
        self.f[b'changed'] = True

    def clear_setting_button(self,change):
        self.push_settings.style.button_color = 'lightblue'
        
    def update_full_scan(self,change):
        self.f[b'changed'] = True   
        self.f[b'full_spectrum_scan'] = self.full_scan.value
        
    def update_mode(self,change):
        if(change['new'] == 'continuous scan'):
            self.f[b'continuous_scan_enable'] = True
            self.f[b'single_frame_enable'] = False  
            self.full_scan.disabled = False
            
            # disable all spectrum settings
            self.get_frame.disabled=True
            self.center_frequency.disabled = True
            self.mins.disabled = True
            self.fft_size.disabled = True
            self.decimation_factor.disabled = True
            self.window.disabled = True
            self.units.disabled = True
            self.frames.disabled = True
            self.coordinates.disabled = True
            self.device_time.disabled = True
            self.time.disabled = True
            self.pickdate.disabled = True
            self.picktime.disabled = True
        else:
            self.f[b'continuous_scan_enable'] = False
            self.f[b'single_frame_enable'] = False  
            self.full_scan.value = False
            self.full_scan.disabled = True
            self.get_frame.disabled=False
            
            # enable spectrum settings
            self.center_frequency.disabled = False
            self.mins.disabled = False
            self.fft_size.disabled = False
            self.decimation_factor.disabled = False
            self.window.disabled = False
            self.units.disabled = False
            self.frames.disabled = False
            self.coordinates.disabled = False
            self.device_time.disabled = False
            self.time.disabled = False
            self.pickdate.disabled = False
            self.picktime.disabled = False
            
            
        self.f[b'changed'] = True    
        self.clear_setting_button(change['new'])
        
    
    def covert_check_write(self):
        passed = True
        err = ""
        
        try:
            self.f[b'centre_frequency'] = int(self.center_frequency.value)
        except:
            passed = False
            err += "ERROR: centre frequency,  is not an integer.\n"
          
        try:
            self.f[b'fft_size'] = int(self.fft_size.value)
        except:
            passed = False
            err += "ERROR: FFT size selection error.\n"
            
        try:
            self.f[b'decimation_factor'] = int(self.decimation_factor.value)
        except:
            passed = False
            err += "ERROR: Decimation factor selection error.\n"
            
            
        self.f[b'window'] = self.window.value
        self.f[b'units'] = self.units.value
        
        try:
            
            list_mins = re.sub("[\[\]]","",self.mins.value)
            self.f[b'mins'] = [int(i) for i in list(list_mins.split(','))]
            
            c = -1
            for m in self.f[b'mins']:
                if (m > c):
                    c = m
                else:
                    passed = False
                    err += "ERROR: mintes must be incremental.\n"
                    break
                
            for m in self.f[b'mins']:
                if (m < 0) | (m > 59):
                    passed = False
                    err += "ERROR: mintes must be between 0 and 59.\n"
                    break
            
        except:
            passed = False
            err += "ERROR: mintes wrong format.\n"
            
        try:
            self.f[b'frame_number'] = int(self.frames.value)
        except:
            passed = False
            err += "ERROR: frame number, is not an integer.\n"
            
        try:
            list_coor = re.sub("[())]","",self.coordinates.value).split(',')
            self.f[b'coordinates'] = (float(list_coor[0]),float(list_coor[1]))
            
        except:
            passed = False
            err += "ERROR: Coordinates must be a tuple (e.g. \"(55.26, -4.65) \").\n"
        
        try:
            u_lim = self.centre_frequency + ((self.fs/self.decimation_factor)/2)
            l_lim = self.centre_frequency - ((self.fs/self.decimation_factor)/2)
            if (u_lim > self.fs/2) | (l_lim < 0):
                err += "ERROR: Nyquist stop band error: range must be within (0 and fs/2),\n >>> lower lim: "+str(l_lim)+" | upper lim: "+str(u_lim) + "\n"
                print(err)
                passed = False
                
            if self.frame_number < 1:
                passed = False
                err += "ERROR: frame number, must be higher or equeal to 1.\n" 
            
        except:
            passed = False
            err += "ERROR: other unknown error.\n"
            
            
        try:
            # ONLY update if enable time active (activated by separate button)
            if(self.enable_time):
                date_time = str(self.pickdate.value)+' '+str(self.picktime.value)
                dt = datetime.strptime(date_time, '%Y-%m-%d %H:%M')
                self.f[b'date_time'] = dt
                self.device_time.value = str(dt)
                self.pickdate.value = dt.date()
                self.picktime.value = str(dt.strftime("%H:%M"))
                self.f[b'single_frame_enable'] = False
        except:
            passed = False
            err += "ERROR: Error has been encountered while updating time"
    
        if passed == False:
            print(err)
            # return err or make popup window (prefered)
        else:
            if pickleFile(self.config_Path, self.f) == False:
                passed = False
                err += "ERROR: writing config file encountered an error.\n"
                print(err)
            else:
                self.enable_time = False
        return passed
            