import tkinter as tk
import tkinter.ttk as ttk
import tkinter.font as tkFont
import tkintermapview
import tempfile
import shutil
import matplotlib
import time
import pandas as pd
from matplotlib.colors import LightSource
import matplotlib.pyplot as plt
import scipy
import pickle
import re
import numpy as np
matplotlib.use("TkAgg")#if changing back end
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg #canvas and toolbar to use as objects
from matplotlib import cm
from datetime import datetime
#will need to edit the toolbar later (or get rid of it)
from matplotlib.figure import Figure
#import SweepClass as sw
#from readData import getSigmfData
import os
import analysis_GUI
#window->frames->widgets structure

class MainWindow(tk.Tk):
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        
        
        tabControl = ttk.Notebook(self)
        
        
        #instantiate frames and place in window
        self.tab1 = MeasurementTab(self)
        self.tab2 = MapTab(self)
        self.tab3 = LiveViewTab(self)
        self.tab4 = AnalysisTab(self)
        
        #need to look into how to make tabs deatachable
        
        
        tabControl.add(self.tab1, text ='Measurements')
        tabControl.add(self.frame2, text ='Tab 2')
        tabControl.pack(expand = 1, fill ="both")
        
        tabControl.add(self.tab2, text ='Map')
        tabControl.pack(expand = 2, fill ="both")
        
        tabControl.add(self.tab3, text ='Live View')
        tabControl.pack(expand = 1, fill ="both")
        
        tabControl.add(self.tab4, text ='Analysis')
        tabControl.pack(expand = 1, fill ="both")
        
        self.menubar = tk.Menu(self)
        self.filemenu = tk.Menu(self.menubar, tearoff = 0)
        self.menubar.add_cascade(label="File", menu= self.filemenu)
        self.filemenu.add_command(label="Open", command=self.refresh_spectrum)
        self.config(menu=self.menubar)
        
        self.frame1.grid(row=0, column=0, sticky="nsew")
        self.frame2.grid(row=1,column=0, sticky="nsew")
        self.frame3.grid(row=0, column=1, sticky="nsew")
        self.frame4.grid(row=1, column=1, sticky="nsew")
#         
        
    def callback(self, ID, lat, long, event=None):	#update windows
        if (ID==-1):
            self.tab1.Spectrum.clear()
        else:
            self.refresh_spectrum(self.tab1.MeasurementList.measurements[ID].data,
                                  self.tab1.MeasurementList.measurements[ID].freq_start,
                                  self.tab1.MeasurementList.measurements[ID].freq_stop,
                                  self.tab1.MeasurementList.measurements[ID].num_samples)
            self.refresh_map(lat,long)
            self.tab4.binarised_data(self.tab1.MeasurementList.measurements[ID].path,self.tab1.MeasurementList.measurements[ID])
        
    
    def refresh_spectrum(self,data,freq_start,freq_stop,num_samples):
        self.tab1.Spectrum.refresh(data,freq_start,freq_stop,num_samples)
        
    def refresh_map(self,latitude,longitude):
        self.tab2.map.refresh_coordinates(latitude,longitude)
        
    def on_closing(self):
        dataset_dir.cleanup()
        self.destroy()
        
        
class MeasurementTab(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self,parent)
        self.parent = parent
        self.Spectrum = Spectrum(self)
        self.MeasurementList = MeasurementList(self)
        self.Spectrum.grid(column=0,row=0,sticky='NSEW')
        self.MeasurementList.grid(column=0,row=1,sticky='NSEW')
        
        self.grid_columnconfigure(0,weight=1)
        self.grid_rowconfigure(0,weight=1)
        self.grid_rowconfigure(1,weight=1)
    def fileDialog(self):
        pass
        
    def clearMeasurement(self):
        pass
    
    def clearTree(self):
        pass
    
class MapTab(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self,parent)
        self.parent = parent
        self.map = Map(self)
        self.map.pack(fill='both')
        
    def make_polygon(self,c):
        pass
        #polygon_1 = self.map.mapwidget.set_polygon(c)

class Spectrum(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self,parent)
        
        self.parent = parent
        self.f = Figure(figsize=(10,5), dpi=100)
        self.fig = self.f.add_subplot(111)
        self.fig.plot([1,2,3,4,5,6,7,8],[1,2,3,4,5,6,7,8])
                                                    
        self.canvas = FigureCanvasTkAgg(self.f, self)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)
        
        #self.line, = self.a.plot([], [], "r-") #empty line for updating            
        
        
    def refresh(self, samples, f_start, f_stop, num):
        freq_axis = np.linspace(f_start, f_stop, num)
        self.fig.clear()
        self.fig.plot(freq_axis, samples, linewidth = 0.5)
        self.canvas.draw();
        
    def clear(self):
        self.fig.clear()
        self.canvas.draw();

                
class MeasurementList(tk.Frame): #tree widget for listing measurements and properties
    
    ##could include a slider to flip through simultaneous measurements in a set
    
    def __init__(self, parent):
        tk.Frame.__init__(self,parent)
        self.parent = parent
        columnTitles = ("Date","Location","Device") #leave "Time" out as there is a default column that gets renamed to that
        self.tree = ttk.Treeview(self, columns = columnTitles, height = 20)
        self.measurements=list()
        self.idMeasurements = 0
        
        #self.tree.pack(padx = 5, pady = 5)
        # can probably iterate this
        self.tree.heading('#0', text='Time')
        self.tree.heading('Date', text='Date')
        self.tree.heading('Location', text='Location')
        self.tree.heading('Device', text='Device')
        self.tree.grid(column=0,row=0,columnspan=4,sticky='NSEW')	#pack places the widget within the frame, grid places the frame within the window
        self.addButton = tk.Button(self, 
                   text="Load", 
                   command=self.fileDialog)
        self.addButton.grid(column=0,row=1,sticky='NSEW')
        self.grid_columnconfigure(0,weight=1)
        self.grid_rowconfigure(0,weight=1)
        
        self.clearButton = tk.Button(self, 
                   text="Clear", 
                   command=self.clearMeasurement)
        self.clearButton.grid(column=1,row=1,sticky='NSEW')
        self.grid_columnconfigure(1,weight=1)
        
        self.clearAllButton = tk.Button(self, 
                   text="Clear All", 
                   command=self.clearTree)
        self.clearAllButton.grid(column=2,row=1,padx=(0,100),sticky='NSEW')
        self.grid_columnconfigure(2,weight=1)
        
        self.measureButton = tk.Button(self, 
                   text="Capture", 
                   command=self.measure)
        self.measureButton.grid(column=3,row=1,padx=(100,0),sticky='NSEW')
        self.grid_columnconfigure(3,weight=1)
        
          
    def fileDialog(self):
        directory = tk.filedialog.askdirectory()
        for root, dirs, files in os.walk(directory):	#iterate through folder & subfolders
            for filename in files:
                if filename.endswith(".sigmf-data"):
                    samples, metadata = getSigmfData(filename)
                    fulldir=directory+'/'+filename
                    fulldir_meta = fulldir.replace(".sigmf-data",".sigmf-meta")
                    newMeasurement = Measurement(samples,metadata,self.idMeasurements, fulldir)
                    self.tree.insert('', tk.END, iid = newMeasurement.id,
                                     text = newMeasurement.time,
                                     values = (newMeasurement.date,str(newMeasurement.latitude)+', '+str(newMeasurement.longitude),
                                                newMeasurement.device),
                                     tags = newMeasurement.id)
                    self.tree.tag_bind(newMeasurement.id, '<Button-1>',
                                       self.make_lambda(newMeasurement.id,newMeasurement.latitude,newMeasurement.longitude))
                    self.measurements.append(newMeasurement)
                    self.idMeasurements=self.idMeasurements+1
                    shutil.copy(fulldir,dataset_dir)
                    shutil.copy(fulldir_meta,dataset_dir)
                    print(newMeasurement.num_samples)
        self.parent.parent.tab4.analyse_dataset()
        coords = self.list_coordinates()
        self.parent.parent.tab2.make_polygon(coords)
        
        
    def make_lambda(self, idd, lat, long):
        return lambda event: self.parent.parent.callback(idd,lat,long)#workaround for lambda function getting overwritten in loops
        
    def clearMeasurement(self):
        print(self.tree.focus())
        
        self.tree.delete(self.tree.selection())
        self.parent.parent.callback(-1,0,0) #clear spectrum
    
    def clearTree(self):
        self.tree.delete(*self.tree.get_children())
        self.parent.parent.callback(-1,0,0)
    
    def measure(self):
        location = tk.simpledialog.askstring("Input", "Enter Post Code:") #need to foolproof this, add auto detection if desired
        filename = tk.simpledialog.askstring("Input", "Enter File Name:")
        #saveto = tk.filedialog.askdirectory()
        #will need to create an inherited class to combine these into one dialog
        sweeprun = sw.sweep(25e6,1750e6,'max')
        sweeprun.capture()
        sweeprun.writeNew(filename)
        #sweepRun.writeMeta(location) #change to desired postcode
        
        #will add a dialog here specifying for how long to measure - need to update sweepclass to accocunt for this
        #add indiciation that measuring is happening and option to interrupt
    def list_coordinates(self):
        coords = []
        for measurement in self.measurements:
            coord = measurement.latitude,measurement.longitude
            coords.append(coord)
        return coords
        
        
class AnalysisTab(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self,parent)
        self.parent = parent
        self.f1 = Figure(figsize=(10,5), dpi=100)
        self.fig1 = self.f1.add_subplot(111)
        self.fig1.plot([1,2,3,4,5,6,7,8],[1,2,3,4,5,6,7,8])
                                                    
        self.canvas = FigureCanvasTkAgg(self.f1, self)
        self.canvas.draw()
        self.canvas.get_tk_widget().grid(row=0,column=0)
        
        self.f2 = Figure(figsize=(10,5), dpi=100)
        self.fig2 = self.f2.add_subplot(111)
        self.fig2.plot([1,2,3,4,5,6,7,1],[1,2,3,4,5,6,7,8])
                                                    
        self.canvas2 = FigureCanvasTkAgg(self.f2, self)
        self.canvas2.draw()
        self.canvas2.get_tk_widget().grid(row=0,column=1)
        
        self.f3 = Figure(figsize=(10,5), dpi=100)
        self.fig3 = self.f3.add_subplot(111)
        self.fig3.plot([1,2,3,4,5,6,7,1],[1,2,3,4,5,6,7,8])
                                                    
        self.canvas3 = FigureCanvasTkAgg(self.f3, self)
        self.canvas3.draw()
        self.canvas3.get_tk_widget().grid(row=1,column=0)
        
        
        self.f4 = Figure(figsize=(10,5), dpi=100)
        self.fig4 = self.f4.add_subplot(111, projection = '3d')
        self.fig4.plot([1,2,3,4,5,6,7,1],[1,2,3,4,5,6,7,8])
                                                    
        self.canvas4 = FigureCanvasTkAgg(self.f4, self)
        self.canvas4.draw()
        self.canvas4.get_tk_widget().grid(row=1,column=1)
        
        
    
    def analyse_dataset(self):
        self.an = analysis_GUI.analysis(_samples_to_average = 5, _dir_path = dataset_dir)
        self.an.get_dataset_files()
        self.plot_bin_dataset(self.parent.tab1.MeasurementList.measurements[0]) # grab a sample measurement to initialise
        self.plot_freqtime(self.parent.tab1.MeasurementList.measurements[0])
        self.plot3D(dec_to= 256, ssample = 0, esample = 23, mode = 'inline', Measurement = self.parent.tab1.MeasurementList.measurements[0])
                
    def binarised_data(self,path,Measurement):
        self.an.setSigmfData(path)
        self.an.get_threshold(5)
        self.an.binarize()
        bin_data = self.an.bin_data
        freq_axis = np.linspace(Measurement.freq_start, Measurement.freq_stop, Measurement.num_samples)	#restructure, code reuse
        self.fig1.clear()
        self.fig1.plot(freq_axis,Measurement.data, label='Spectrum')
        self.fig1.plot(freq_axis,self.an.threshold, label='thresh')
        self.fig1.plot(freq_axis,bin_data, label='binary data')
        self.fig1.set_xlabel('frequency')
        self.fig1.set_ylabel('binary on / off')
        self.fig1.set_title("My Plot")
        self.fig1.legend()
        self.canvas.draw()
        
    def plot_bin_dataset(self,Measurement):
        print(self.an.filepaths[0])
        self.an.get_dataset()
        self.an.binarize_dataset()
        p = np.sum(self.an.bin_dataset,axis=0)/len(self.an.bin_dataset[:,1])
        freq_axis = np.linspace(Measurement.freq_start, Measurement.freq_stop, Measurement.num_samples)
        self.fig2.clear()
        self.fig2.plot(freq_axis,p) #
        self.fig2.set_xlabel('frequency')
        self.fig2.set_ylabel('percentage')
        self.fig2.set_title("Usage per frequencies")
        self.canvas2.draw()
        print("overall percentage: "+str(sum(p)/len(p)))
        
    def plot_freqtime(self, Measurement):		##MAKE THIS ADJUSTABLE
        self.an.get_dataset()
        #df = pd.DataFrame({'data': self.an.raw_dataset[:,1750]})
        data = self.an.raw_dataset[4,:]
        freq_axis = np.linspace(Measurement.freq_start, Measurement.freq_stop, Measurement.num_samples)
        self.fig3.clear()
        self.fig3.plot(np.arange(150,841,1),data[150:841])
        self.fig3.set_xlabel('samples time [hrs]')
        self.fig3.set_ylabel('Magnitude')
        self.fig3.set_title("Observed frequency : "+str(freq_axis[1750]/1e6)+" MHz")
        self.canvas3.draw()
        
    def plot3D(self, dec_to= 256, ssample = 0, esample = 23, mode = 'inline', Measurement = []):
        k = int(len(self.an.raw_dataset[1,:])/dec_to)
        data = scipy.signal.decimate(self.an.raw_dataset,k,axis = 1)
        z = data[ssample:esample,:]
        
        print("data shape to plot = "+str(data.shape))
        nrows, ncols = z.shape
        x = np.linspace(Measurement.freq_start, Measurement.freq_stop, ncols)
        y = np.linspace(ssample, esample, nrows)
        x, y = np.meshgrid(x, y)


        self.fig4.clear()
        #self.canvas4.rcParams['figure.figsize'] = [12, 12]
        #self.canvas4.rcParams['figure.dpi'] = 100 # 200 e.g. is really fine, but slower
        #self.fig4.set_title(" Dataset from samples "+str(ssample)+ " to " +str(esample))
        ls = LightSource(270, 45)

        
        # To use a custom hillshading mode, override the built-in shading and pass
        # in the rgb colors of the shaded surface calculated from "shade".
        rgb = ls.shade(z, cmap=cm.gist_earth, vert_exag=0.1, blend_mode='soft')
        
        surf = self.fig4.plot_surface(x, y, z, rstride=1, cstride=1, facecolors=rgb,
                                   linewidth=0, antialiased=False, shade=False)
        self.fig4.set_xlabel("Frequency [MHz]")
        self.fig4.set_ylabel("samples [n]")
        self.fig4.set_zlabel("Magnnitude [dBFS]")
        self.canvas4.draw()

class Measurement(object): 	#store info for linking between treeview/map/analysis
    def __init__(self, samples, metadata, id, path):
    #will need to add failsafes for formatting etc
        self.freq_start = samples[b'lower_lim']
        self.freq_stop = samples[b'upper_lim']
        self.id = id
        self.num_samples = samples[b'samples']
        self.data = samples[b'data']
        self.device = metadata['device']
        self.coord = metadata['geolocation']['coordinates']
        self.datetime = metadata['datetime']
        self.path = path
        self.unpack()
        
    def unpack(self):
        self.date = self.datetime[0:10]
        self.time = self.datetime[12:19]
        self.latitude = float(self.coord[0])
        self.longitude = float(self.coord[1])
    
        
class Map(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self,parent)
        #self.parent = parent
        self.mapwidget = tkintermapview.TkinterMapView(self,width=800,height=800) #might need to read from display size
        #self.mapwidget.set_position(55.86, -4.21)
        self.mapwidget.set_tile_server("https://mt0.google.com/vt/lyrs=m&hl=en&x={x}&y={y}&z={z}&s=Ga", max_zoom=22)
        self.mapwidget.set_position(55.86152790155066, -4.246978736010148)	#default position
        self.mapwidget.pack()
        
    def refresh_coordinates(self,lat,long):
        self.mapwidget.set_position(lat, long)
        self.mapwidget.pack()
        

class LiveViewTab(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self,parent)
        self.parent = parent
        self.config_path = r"\\192.168.3.1\xilinx\jupyter_notebooks\strathRFM\config.pkl"
        self.data_path = r"\\192.168.3.1\xilinx\jupyter_notebooks\strathRFM\data.pkl"
        self.fs = 4096*1e6
        _,self.config = self.unpickleFile(self.config_path)
        
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
        self.stream_data()
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
        
        
    def stream_data(self):
        while(1):
        
            self.config[b'single_frame_enable'] = True
            self.config[b'changed'] = True
            self.pickleFile(self.config_path, self.config)
            self.config[b'single_frame_enable'] = False
            self.config[b'changed'] = False
            time.sleep(0.2)
            result, self.data = self.unpickleFile(self.data_path)
            
            _,  self.config = self.unpickleFile(self.config_path)
            if result:
                print(len(self.data[b'data']))
                # data has lower lim upper lim and data you can get length using ^^
                print(self.data[b'data'][0])
                print(self.config[b'status'])
            else:
                print("shit")
                
            time.sleep(0.2)
            
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
    
    
    
    
    
    
    # this method checks that the inputs are as expected. 
    # Returns True if no errors have been encountered.
    # The err variable is a string of all the errors encountered (include as popup window or print sometwhere).
 
    
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
                
                # replace with your GUI variable
                # local time use as formatted "YYYY-MM-DD HH:MM" No seconds
                
                # hand selected
                
                # dvt = datetime.now().strftime("%Y-%m-%d %H:%M")
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
    
    
    

with tempfile.TemporaryDirectory() as dataset_dir:
    window = MainWindow(); #window instance
    width, height = window.winfo_screenwidth()/2, window.winfo_screenheight()-200
    window.geometry('%dx%d+0+0' % (width,height))
    window.protocol("WM_DELETE_WINDOW", window.on_closing)
    window.mainloop();