# -*- coding: utf-8 -*-
"""
Created on Thu Apr 13 18:28:04 2023

@author: rober
"""

import tkinter as tk
from datetime import datetime
import pickle, re, time
from tkinter.messagebox import askokcancel, WARNING



class tk_gui():
    def __init__(self,_config_path=  'C:/Users/rober/.spyder-py3/Proj/config.pkl'):
        self.config_Path = _config_path# r"\\192.168.3.1\xilinx\jupyter_notebooks\strathRFM\config.pkl"
        self.data_path = ""#r"\\192.168.3.1\xilinx\jupyter_notebooks\strathRFM\data.pkl"
        self.fs = 4096
        _,self.config = self.unpickleFile(self.config_Path)
        
        self.status = self.config[b'status']                                    # string for specCTRL status
        self.continuous_scan_enable = self.config[b'continuous_scan_enable']    # bool dataset generation
        self.mins = self.config[b'mins']                                        # array of incremental number up to 59 [0,15,...,59]
        self.single_frame_enable =  self.config[b'single_frame_enable']         # bool - get a frame
        self.start_on_boot = self.config[b'start_on_boot']                      # bool - initialise on boot
        self.full_spectrum_scan = self.config[b'full_spectrum_scan']            # bool - if continuous scan enable scan full spectrum
        self.app_enable = self.config[b'app_enable']                            # bool - enable specCTRL loop
        self.fft_size = self.config[b'fft_size']                                # int powers of 2
        self.centre_frequency = self.config[b'centre_frequency']                # int defalt 1024 (MHz)
        self.decimation_factor = self.config[b'decimation_factor']              # int powers of 2
        self.units = self.config[b'units']                                      # str 'dBm' or 'dBFS' 
        self.window = self.config[b'window']                                    # string window type check list
        self.frame_number = self.config[b'frame_number']                        # int >= 1
        self.coordinates = self.config[b'coordinates']                          # tuple (lat, long)
        self.enable_time = self.config[b'enable_time']                          # bool to set time on device
        self.date_time = self.config[b'date_time']                              # datetime format
        
        
        self.data = []
        #to be completed



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
    
    def update_int_variables(self):
        _,self.config = self.unpickleFile(self.config_Path)
        
        self.status = self.config[b'status']                                    # string for specCTRL status
        self.continuous_scan_enable = self.config[b'continuous_scan_enable']    # bool dataset generation
        self.mins = self.config[b'mins']                                        # array of incremental number up to 59 [0,15,...,59]
        self.single_frame_enable =  self.config[b'single_frame_enable']         # bool - get a frame
        self.start_on_boot = self.config[b'start_on_boot']                      # bool - initialise on boot
        self.full_spectrum_scan = self.config[b'full_spectrum_scan']            # bool - if continuous scan enable scan full spectrum
        self.app_enable = self.config[b'app_enable']                            # bool - enable specCTRL loop
        self.fft_size = self.config[b'fft_size']                                # int powers of 2
        self.centre_frequency = self.config[b'centre_frequency']                # int defalt 1024 (MHz)
        self.decimation_factor = self.config[b'decimation_factor']              # int powers of 2
        self.units = self.config[b'units']                                      # str 'dBm' or 'dBFS' 
        self.window = self.config[b'window']                                    # string window type check list
        self.frame_number = self.config[b'frame_number']                        # int >= 1
        self.coordinates = self.config[b'coordinates']                          # tuple (lat, long)
        self.enable_time = self.config[b'enable_time']                          # bool to set time on device
        self.date_time = self.config[b'date_time']                              # datetime format
    
    # you can change parameters while in idle mode to
    # change the spectrum analyser settings
    # refere to spectrumWidgets on how to get rfsoc CTRL.
    def create_config(self,_changed):
        config_file = {b'changed':_changed,                                     # bool to show that spectrum settings were changed
                      b'status': self.status,                                   # string for specCTRL status
                      b'continuous_scan_enable': self.continuous_scan_enable,   # bool dataset generation
                      b'mins':self.mins,                                        # array of incremental number up to 59 [0,15,...,59]
                      b'single_frame_enable':self.single_frame_enable,          # bool - get a frame
                      b'start_on_boot': self.start_on_boot,                     # bool - initialise on boot
                      b'full_spectrum_scan':self.full_spectrum_scan,            # bool - if continuous scan enable scan full spectrum
                      b'app_enable':self.app_enable,                            # bool - enable specCTRL loop
                      b'fft_size':self.fft_size,                                # int powers of 2
                      b'centre_frequency':self.centre_frequency,                # int defalt 1024 (MHz)
                      b'decimation_factor':self.decimation_factor,              # int powers of 2
                      b'units': self.units,                                     # str 'dBm' or 'dBFS' 
                      b'window':self.window,                                    # string window type check list
                      b'frame_number':self.frame_number,                        # int >= 1
                      b'coordinates':self.coordinates,                          # tuple (lat, long)
                      b'enable_time':self.enable_time,                          # bool to set time on device
                      b'date_time':self.date_time}                              # datetime format
        res = self.pickleFile(self.config_Path, config_file)
        return res
    def create_config_new(self, _filename):
        config_file = {b'changed':False,                                     # bool to show that spectrum settings were changed
                      b'status': "self.status",                                   # string for specCTRL status
                      b'continuous_scan_enable': False,   # bool dataset generation
                      b'mins':[0,15,30,45,49],                                        # array of incremental number up to 59 [0,15,...,59]
                      b'single_frame_enable':False,          # bool - get a frame
                      b'start_on_boot': False,                     # bool - initialise on boot
                      b'full_spectrum_scan':False,            # bool - if continuous scan enable scan full spectrum
                      b'app_enable':False,                            # bool - enable specCTRL loop
                      b'fft_size':256,                                # int powers of 2
                      b'centre_frequency':1024,                # int defalt 1024 (MHz)
                      b'decimation_factor':2,              # int powers of 2
                      b'units': 'dBm',                                     # str 'dBm' or 'dBFS' 
                      b'window':'rectangular',                                    # string window type check list
                      b'frame_number':1,                        # int >= 1
                      b'coordinates':(0,0),                          # tuple (lat, long)
                      b'enable_time':False,                          # bool to set time on device
                      b'date_time':datetime.now()}                              # datetime format
        self.pickleFile(_filename, config_file)
      
    # [Settings] device name, fs,
    # Assuming a layout 
    #################################
    #                       #       #
    #                       #       #    
    #                       #       #
    #        Graph          #  CTL  #
    #                       #       #
    #                       #       #
    #                       #       #
    #################################
    
    # CTL: Logo?
    # Buttons or Boolean switches: [Start on Boot, Application enable, Start/Stop stream (live view)]
    # [Button: get frame] (get a single frame and display) 
    # [Radio: IDLE, Continuous scan, ] [if continuous scan enable checkbox or switch for "Full spectrum scan"]
    # 
    # [Label('Spectrum Settings:')]
    # [Label('Centre Frequency:']   [InputText()]   [Label('MHz')]
    # [Label('FFT size:']           [Dropdown(options: ['64','128', '256', '512', '1024', '2048', '4096', '8192' ])]
    # [Label('Decimation factor:']  [Dropdown(options: ['2', '4', '8', '16','32','64'])]
    # [Label('Window Type:']        [Dropdown(options: ['rectangular','bartlett' ,'hamming', 'hanning', 'blackman'])]
    # [Label('Units:']              [Dropdown(options: ['dBFS', 'dBm'])]
    # [Label('Minutes:']            [InputText()] - convert string to an array
    # [Label('Frames:']             [InputText()] - convert string to int  
    # [Label('Coordinates:']        [InputText()] - convert string to tuple of ints 
    # [Label('Push settings')]      [Button]
    
    # [Label('Local Time')]         [time date picker] [default value: datetime.now()]
    # [Label('Device Time')]        [Text(device time).disabled] [Button(update time)]
    
    
    # methods that are necessary:

    
    def covert_check_write(self, cf,fft,df,w,un,mn,fn,cr,dvt):
        passed = True
        err = ""
        
        try:
            self.centre_frequency = int(cf)
        except:
            passed = False
            err += "ERROR: centre frequency,  is not an integer.\n"
          
        try:
            self.fft_size = int(fft)
        except:
            passed = False
            err += "ERROR: FFT size selection error.\n"
            
        try:
            self.decimation_factor = int(df)
        except:
            passed = False
            err += "ERROR: Decimation factor selection error.\n"
            
            
        self.window = w
        self.units = un
        
        try:
            list_mins = re.sub("[\[\]]","",mn)
            self.mins = [int(i) for i in list(list_mins.split(','))]
            c = -1
            for m in self.mins:
                if (m > c):
                    c = m
                else:
                    passed = False
                    err += "ERROR: mintes must be incremental.\n"
                    break
                
            for m in self.mins:
                if (m < 0) | (m > 59):
                    passed = False
                    err += "ERROR: mintes must be between 0 and 59.\n"
                    break
            
        except:
            passed = False
            err += "ERROR: mintes wrong format.\n"
            
        try:
            self.frame_number = int(fn)
        except:
            passed = False
            err += "ERROR: frame number, is not an integer.\n"
            
        try:
            list_coor = re.sub("[())]","",cr).split(',')
            self.coordinates = (float(list_coor[0]),float(list_coor[1]))
            
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
                
                print(dvt, flush = True)
                # if input is string in that format
                dt = datetime.strptime(dvt, '%Y-%m-%d %H:%M')
                self.date_time = dt
            
        except:
            passed = False
            err += "ERROR: Error has been encountered while updating time"
    
        if passed == False:
            print(err)
            # return err or make popup window (prefered)
        else:
            if self.create_config(True) == False:
                passed = False
                err += "ERROR: writing config file encountered an error.\n"
                print(err)
            else:
                self.enable_time = False
        return passed, err
            
            
    def push_settings(self):
        #print(" %s\n %s \n %s \n %s" %(e1.get(), e2.get(), e3.get(), DF.get()))
        self.enable_time = False
        res, err = self.covert_check_write(self.e1.get(),self.FFT.get(),self.DF.get(),
                                           self.WND.get(),self.UNITS.get(), self.e3.get(),
                                           self.e2.get(),self.e4.get(),self.e6.get())
        if res:
            err = "Success. Spectrum Settings updated."
            self.open_popup("Notice.",err)
        else:
            self.open_popup('ERROR', err)
            
    def push_time(self):
        self.enable_time = True
        res, err = self.covert_check_write(self.e1.get(),self.FFT.get(),self.DF.get(),
                                           self.WND.get(),self.UNITS.get(), self.e3.get(),
                                           self.e2.get(),self.e4.get(),self.e6.get())
        if res:
            err = "Success. System Time updated."
            self.open_popup("Notice.",err)
            self.e5.delete(0,tk.END)
            self.e5.insert(0,str(datetime.now().strftime('%Y-%m-%d %H:%M')))
        else:
            self.open_popup('ERROR', err)
        self.enable_time = False
    
    def toggleAPP(self):
        if self.toggle_app.config('text')[-1] == 'ON':
            self.toggle_app.config(text='OFF',relief="raised")
            self.toggle_Continuous.config(text='OFF',relief="raised")
            self.toggle_Fscan.config(text='Full scan OFF',relief="raised")
            self.app_enable = False
            self.continuous_scan_enable = False
            self.full_spectrum_scan = False
        else:
            self.toggle_app.config(text='ON',relief="sunken")
            self.app_enable = True
            
            
    def toggleBoot(self):
        if self.toggle_boot.config('text')[-1] == 'ON':
            self.toggle_boot.config(text='OFF',relief="raised")
            self.start_on_boot = False
        else:
            self.toggle_boot.config(text='ON',relief="sunken")
            self.start_on_boot = True
          
    def toggleCont(self):
        if self.toggle_Continuous.config('text')[-1] == 'ON':
            self.toggle_Continuous.config(text='OFF',relief="raised")
            self.toggle_Fscan.config(text='Full scan OFF',relief="raised")
            self.full_spectrum_scan = False
            self.continuous_scan_enable = False
        else:
            self.toggle_Continuous.config(text='ON',relief="sunken")
            self.continuous_scan_enable = True
            
    def toggleFscan(self):
        if self.toggle_Fscan.config('text')[-1] == 'Full scan ON':
            self.toggle_Fscan.config(text='Full scan OFF',relief="raised")
            self.open_popup("Full scan", "The full scan option has been turned off.")
            self.full_spectrum_scan = False
        else:
            self.toggle_Fscan.config(text='Full scan ON',relief="sunken")
            self.full_spectrum_scan = True
    
    def toggleStream(self):
        if self.toggle_stream.config('text')[-1] == 'Stream ON':
            self.toggle_stream.config(text='Stream OFF',relief="raised")
            
            self.stream = False
        else:
            self.toggle_stream.config(text='Stream ON',relief="sunken")
            self.stream = True
    
    def get_frame(self):
        self.single_frame_enable = True
        self.push_settings()
        
        res, data = self.unpickleFile(self.data_path)
        if(res):
            print("plot the data")
        else:
            self.open_popup("Error", "Could not get data file.")
        self.single_frame_enable = False
    
    def open_popup(self, _title="Window", _text = "Notes..."):
        askokcancel(_title, _text, icon=WARNING)
       
    
    
    def gui(self):
        
        self.master = tk.Tk()
        
        self.DF = tk.StringVar(self.master)
        self.DF.set(self.decimation_factor)
        self.FFT = tk.StringVar(self.master)
        self.FFT.set(self.fft_size)
        self.WND = tk.StringVar(self.master)
        self.WND.set(self.window)
        self.UNITS = tk.StringVar(self.master)
        self.UNITS.set(self.units)
        
        tk.Label(self.master, text="Centre Frequency").grid(row=0)
        tk.Label(self.master, text="Decimation Factor").grid(row=1)
        tk.Label(self.master, text="FFT size").grid(row=2)
        tk.Label(self.master, text="Window Type").grid(row=3)
        tk.Label(self.master, text="Spectrum Units").grid(row=4)
        tk.Label(self.master, text="Frame Number").grid(row=5)
        tk.Label(self.master, text="Minutes").grid(row=6)
        tk.Label(self.master, text="Coordinates").grid(row=7)
        
        tk.Label(self.master, text="App Enable").grid(row=8)
        tk.Label(self.master, text="Start on Boot").grid(row=9)
        tk.Label(self.master, text="Continuous scan").grid(row=10)
        
        tk.Label(self.master, text="local Date Time").grid(row=12)
        #tk.Label(self.master, text=str(datetime.now().strftime('%Y-%m-%d %H:%M'))).grid(row=12, column=1)
        tk.Label(self.master, text="Device Date Time").grid(row=13)
        #tk.Label(master, text=str(datetime.now().strftime('%Y-%m-%d %H:%M'))).grid(row=13, column=1)
        
        
        self.e1 = tk.Entry(self.master)
        self.e2 = tk.Entry(self.master)
        self.e3 = tk.Entry(self.master)
        self.e4 = tk.Entry(self.master)
        self.e5 = tk.Entry(self.master)
        self.e6 = tk.Entry(self.master)
        
        self.w = tk.OptionMenu(self.master, self.DF,'2', '4', '8', '16','32','64')
        self.w1 = tk.OptionMenu(self.master, self.FFT,'64','128', '256', '512', '1024', '2048', '4096', '8192' )
        self.w2 = tk.OptionMenu(self.master, self.WND,'rectangular','bartlett' ,'hamming', 'hanning', 'blackman')
        self.w3 = tk.OptionMenu(self.master, self.UNITS,'dBFS', 'dBm')
        
        
        self.e1.grid(row=0, column=1)
        self.e2.grid(row=5, column=1)
        self.e3.grid(row=6, column=1)
        self.e4.grid(row=7, column=1)
        
        self.w.grid(row=1, column=1)
        self.w1.grid(row=2, column=1)
        self.w2.grid(row=3, column=1)
        self.w3.grid(row=4, column=1)
        
        self.e5.grid(row=13, column=1)
        self.e6.grid(row=12, column=1)
        
        self.e1.insert(0,str(int(self.centre_frequency)))
        self.e2.insert(0,str(int(self.frame_number)))
        self.e3.insert(0,str(self.mins))
        self.e4.insert(0,str(self.coordinates))
        self.e5.insert(0,str(self.date_time.strftime('%Y-%m-%d %H:%M')))
        self.e6.insert(0,str(datetime.now().strftime('%Y-%m-%d %H:%M')))
              
        
        
        self.toggle_app = tk.Button(text= "ON" if self.app_enable else "OFF",
                                    relief="sunken" if self.app_enable else "raised", width=10, command=self.toggleAPP)
        self.toggle_app.grid(row=8, 
                            column=1, 
                            sticky=tk.W, 
                            pady=4)                                             
        self.toggle_boot = tk.Button(text="ON" if self.start_on_boot else "OFF",
                                     relief="sunken" if self.start_on_boot else "raised" , width=10, command=self.toggleBoot)
        self.toggle_boot.grid(row=9, 
                            column=1, 
                            sticky=tk.W, 
                            pady=4)  
        self.toggle_Continuous = tk.Button(text="ON" if self.continuous_scan_enable else "OFF",
                                           relief="sunken" if self.continuous_scan_enable else "raised", width=10, command=self.toggleCont)
        self.toggle_Continuous.grid(row=10, 
                            column=1, 
                            sticky=tk.W, 
                            pady=4)  
        
        self.toggle_Fscan = tk.Button(text="Full scan ON" if self.full_spectrum_scan else "Full scan OFF",
                                      relief="sunken" if self.full_spectrum_scan else "raised", width=10, command=self.toggleFscan)
        self.toggle_Fscan.grid(row=10, 
                            column=2, 
                            sticky=tk.W, 
                            pady=4)  
        
        tk.Button(self.master, text='Push Time', command=self.push_time).grid(row=13, 
                                                               column=2, 
                                                               sticky=tk.W, 
                                                               pady=4)
        tk.Button(self.master,text='Push Settings', command=self.push_settings).grid(row=11, 
                                                               column=2, 
                                                               sticky=tk.W, 
                                                               pady=4)
        tk.Button(self.master,text='Get Frame', command=self.get_frame).grid(row=0, 
                                                               column=3, 
                                                               sticky=tk.W, 
                                                               pady=4)
        
        self.toggle_stream = tk.Button(text='Stream OFF',
                                      relief="raised", width=10, command=self.toggleStream)
        self.toggle_stream.grid(row=1, 
                            column=3, 
                            sticky=tk.W, 
                            pady=4)  
        
        
        tk.mainloop()
s = tk_gui()
s.gui()