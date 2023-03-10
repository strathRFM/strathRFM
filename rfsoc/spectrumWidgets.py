#!/usr/bin/env python
# coding: utf-8

"""
    Author: Robert Incze
    Date: 10/03/2023
    Description: control class, that enables interactive editing of the config.pkl file in turn controlling the 
                specCTRL and the spectrum analyser.
"""


import pickle
import matplotlib.pyplot as plt
import time
from datetime import datetime
import collections
import numpy as np
from IPython.display import clear_output
import ipywidgets as widgets
from ipywidgets import Button, HBox, VBox
from IPython.display import display
   
    
    
def create_config():
    config_file = {b'changed':True,
                  b'continuous_scan_enable': False,
                  b'single_frame_enable':False,
                  b'start_on_boot': False,
                  b'full_spectrum_scan':False,
                  b'app_enable': True,
                  b'stream_data_enable':False,
                  b'mins':[0,15,30,45],
                  b'fft_size':4096,
                  b'centre_frequency':1024000000,
                  b'decimation_factor':4,
                  b'units': 'dBFS',
                  b'window':'hamming',
                  b'frame_number':60,
                  b'coordinates':(0,0),
                  b'date_time':datetime.now()}
    res = pickleFile(config_Path, config_file)
    
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

class spectrumWidgets:
    def __init__(self,_config_Path = "config.pkl", # path to the configuration file writable by GUI
                 _spec_Data_Stream_Path = "data.pkl" ):  # path of data file writable from this calss
        
        self.config_Path = _config_Path
        _, self.f = unpickleFile(self.config_Path);
        self.out = widgets.Output(layout={'border': '1px solid black'})
        self.out2 = widgets.Output()
        
        self.get_frame = widgets.Button(description='get Frame')
        self.push_settings = widgets.Button(description='Push settings')
        # radio buttons
        self.rad = widgets.RadioButtons(
                        options=['continuous scan', 'stream data', 'idle'],
                        value=self.set_radio_val(), # Defaults to 'pineapple'
                    #    layout={'width': 'max-content'}, # If the items' names are long
                        description='MODE:',
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
            value= str(self.f[b'centre_frequency']),
            placeholder='integer',
            description='Centre f:',
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
            options=['128', '256', '512', '1024', '2048', '4096' ],
            value=str(self.f[b'fft_size']),
            description='FFT size:',
            disabled=False,
            indent=True
        )
        self.decimation_factor = widgets.Dropdown(
            options=['2', '4', '8', '16','32'],
            value=str(self.f[b'decimation_factor']),
            description='Decimation:',
            disabled=False,
            indent=True
        )
        self.window = widgets.Dropdown(
            options=['rectangular', 'hamming', 'hanning', 'Blackman'],
            value=str(self.f[b'window']),
            description='Window Type:',
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
            description='Nr of Frames:',
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
        # definitions
        
    def set_radio_val(self):
        if(self.f[b'stream_data_enable']):
            self.get_frame.disabled=True
            return 'stream data'
        elif(self.f[b'continuous_scan_enable']):
            self.get_frame.disabled=True
            return 'continuous scan'
        else:
            self.get_frame.disabled=False
            return 'idle'
        
    def AppLayout(self):
        
        data = {'Spectrum': [0,0,0,1,0]}
        self.live_plot(data)
            
            
        
        # define system settings
        Tbuttons = HBox([self.boot,self.app_enable, self.get_frame],layout={'border': '1px solid black'})
        
        self.L = VBox([Tbuttons,
                       self.rad,
                       HBox([self.center_frequency,self.push_settings]),
                       self.fft_size,
                       self.decimation_factor,
                       self.window,
                       self.units,
                       self.mins,
                       self.frames,
                       self.coordinates,
                       HBox([self.device_time,self.time])
                      ],
                      layout={'border': '1px solid black'})
        
        # on clicks and updates
        self.boot.on_click(self.update_boot)
        self.app_enable.on_click(self.update_app_enable)
        self.get_frame.on_click(self.update_frame)
        self.rad.observe(self.update_mode, names='value')
        
        # display
        display(HBox([self.L,self.out]),self.out2)
    
    def update_frame(self,b):
        #data['spectrum'] = dataf[b'data']
        data = {'Spectrum': np.random.rand(100)}
        self.live_plot(data)
    
    
    def update_boot(self,b):
        val = self.f[b'start_on_boot']
        self.f[b'start_on_boot'] = not val
        if(self.f[b'start_on_boot']):
            self.boot.style.button_color = 'lightgreen'
        else:
            self.boot.style.button_color = 'lightblue'
        
        self.f[b'changed'] = True    
        pickleFile(self.config_Path, self.f)
        
    get_ipython().run_line_magic('matplotlib', 'inline')
    def live_plot(self,data_dict, figsize=(8,7), title=''):
        with self.out:
            clear_output(wait=True)
            plt.figure(figsize=figsize)
            for label,data in data_dict.items():
                plt.plot(data, label=label)
            plt.title(title)
            plt.grid(True)
            plt.xlabel('epoch')
            plt.ylim(-1, 1)
            plt.legend(loc='center left') # the plot evolves to the right
            plt.show()
        
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
            self.f[b'stream_data_enable'] = False
            self.f[b'continuous_scan_enable'] = False
            self.rad.value = 'idle'
            self.rad.disabled = True
            self.get_frame.disabled=True
        
        self.f[b'changed'] = True    
        pickleFile(self.config_Path, self.f)
        
    def update_mode(self,change):
        #with self.out2:
        #    print(change['new'])
        if(change['new'] == 'stream data'):
            self.f[b'stream_data_enable'] = True
            self.f[b'continuous_scan_enable'] = False
            self.get_frame.disabled=True
        elif(change['new'] == 'continuous scan'):
            self.f[b'stream_data_enable'] = False
            self.f[b'continuous_scan_enable'] = True
            self.get_frame.disabled=True
        else:
            self.f[b'stream_data_enable'] = False
            self.f[b'continuous_scan_enable'] = False
            self.get_frame.disabled=False
        self.f[b'changed'] = True    
        pickleFile(self.config_Path, self.f)