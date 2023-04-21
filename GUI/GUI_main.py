#GUI for StrathRFM
#Author: Martin Dimov


##3rd party dependencies
import tkinter as tk
import tkinter.ttk as ttk
import tkinter.font as tkFont
import tkintermapview
import tempfile
import shutil
import matplotlib
import time
import glob
import pandas as pd
from matplotlib.colors import LightSource
import matplotlib.pyplot as plt
import scipy
import pickle
import numpy as np
matplotlib.use("TkAgg")#if changing back end
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk #canvas and toolbar to use as objects
from matplotlib import cm

#will need to edit the toolbar later (or get rid of it)
from matplotlib.figure import Figure


#support files
import SweepClass as sw
from readData import getSigmfData
import os
import analysis_GUI
import GUI_support
#window->frames->widgets structure

class MainWindow(tk.Tk):
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        
        
        tabControl = ttk.Notebook(self)
        
        
        #instantiate frames and place in window
        self.tab1 = MeasurementTab(self)
        self.tab2 = MapTab(self)		##NOTE: tkintermapview is unstable on some PC's, comment this out if there are problems, as well as lines 57-58
        self.tab3 = LiveViewTab(self)	##NOTE: For live view, make sure there is access to \\192.168.3.1 network drive in windows explorer
        self.tab4 = AnalysisTab(self)
        
        #need to look into how to make tabs deatachable
        
        
        tabControl.add(self.tab1, text ='Measurements')
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
        self.filemenu.add_command(label="Settings", command=self.set_globals)
        self.config(menu=self.menubar)
      
        
    def callback(self, ID, lat, long, event=None):	#update windows based on loaaded data
        if (ID==-1):	#called back upon clearing
            self.tab1.Spectrum.clear()
        else:			#update spectrum and single analysis
            self.refresh_spectrum(self.tab1.MeasurementList.measurements[ID].data,
                                  self.tab1.MeasurementList.measurements[ID].freq_start,
                                  self.tab1.MeasurementList.measurements[ID].freq_stop,
                                  self.tab1.MeasurementList.measurements[ID].num_samples)
            self.tab4.tab1.binarised_data(self.tab1.MeasurementList.measurements[ID].path,self.tab1.MeasurementList.measurements[ID])
            
    
    def refresh_spectrum(self,data,freq_start,freq_stop,num_samples):
        self.tab1.Spectrum.refresh(data,freq_start,freq_stop,num_samples)
    def refresh_map(self,coordlist):
        if coordlist[1]: #check if valid
            self.tab2.map.make_polygon(coordlist)
            self.tab2.map.mapwidget.set_position(coordlist[1])
        
    def on_closing(self):
        self.destroy()
        
    def set_globals(self):
        pass
        #self.settings = tkconfig.tk_gui(self)
        #self.settings.pack()
        # formatting - to be completed
        

        
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
    
class MapTab(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self,parent)
        self.parent = parent
        self.map = Map(self)
        self.map.pack(fill='both')
         
    def make_polygon(self,c):							#create overlay to show measurement locations
        self.polygon = self.map.mapwidget.set_polygon(c)
    def clear_polygon(self):
        self.polygon.delete()
    

class Spectrum(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self,parent)
        
        #figure settings
        self.parent = parent
        self.f = Figure(figsize=(10,5), dpi=100)
        self.fig = self.f.add_subplot(111)
        self.fig.plot([1,2,3,4,5,6,7,8],[1,2,3,4,5,6,7,8])
        self.fig.set_xlabel('Frequency (Hz)')
        self.fig.set_ylabel('Magnitude (dbM)')
        self.fig.set_title("Frequency Spectrum (Selected Data)")
                                                    
        self.canvas = FigureCanvasTkAgg(self.f, self)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)     
        
        
    def refresh(self, samples, f_start, f_stop, num):
        freq_axis = np.linspace(f_start, f_stop, num)
        self.fig.clear()
        self.fig.grid()
        self.fig.set_xlabel('Frequency (Hz)')
        self.fig.set_ylabel('Magnitude (dBFS)')
        self.fig.set_title("Frequency Spectrum (Current)")
        self.fig.plot(freq_axis, samples, linewidth = 0.5)
        self.canvas.draw();
        
    def clear(self):
        self.fig.clear()
        self.canvas.draw();
    def addgrid(self):
        self.fig.grid()

                
class MeasurementList(tk.Frame): #tree widget for listing measurements and properties
    
    def __init__(self, parent):
        tk.Frame.__init__(self,parent)
        self.parent = parent
        columnTitles = ("Date","Location","Device") #leave "Time" out as there is a default column that gets renamed to that
        self.tree = ttk.Treeview(self, columns = columnTitles, height = 20)
        self.measurements=list()
        self.idMeasurements = 0
        
        self.tree.heading('#0', text='Time')
        self.tree.heading('Date', text='Date')
        self.tree.heading('Location', text='Location')
        self.tree.heading('Device', text='Device')
        self.tree.grid(column=0,row=0,columnspan=4,sticky='NSEW')	#pack places the widget within the frame, grid places the frame within the window
        
        
        #buttons for functionality
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
                if filename.endswith(".sigmf-data"):	#find sigmf
                    if self.idMeasurements>1:	#error check - can't analyse mismatched data length (for now)
                        cur = self.measurements[self.idMeasurements-1]
                        prev = self.measurements[self.idMeasurements-2]
                        if cur.num_samples != prev.num_samples:
                            print("error, mismatch in measurement size")
                            break
                    
                    fulldir=directory+'/'+filename				#ensure full directory is input
                    samples, metadata = getSigmfData(fulldir)
                    fulldir_meta = fulldir.replace(".sigmf-data",".sigmf-meta")
                    newMeasurement = Measurement(samples,metadata,self.idMeasurements, fulldir)	#create measurement and set parameters
                    self.tree.insert('', tk.END, iid = newMeasurement.id,						#make treeview items for measurements
                                        text = newMeasurement.time,
                                        values = (newMeasurement.date,str(newMeasurement.latitude)+', '+str(newMeasurement.longitude),
                                                newMeasurement.device),
                                        tags = newMeasurement.id)
                    self.tree.tag_bind(newMeasurement.id, '<Button-1>',			#link measurement to tree item to allow updating
                                        self.make_lambda(newMeasurement.id,newMeasurement.latitude,newMeasurement.longitude))
                    self.measurements.append(newMeasurement)
                    self.idMeasurements=self.idMeasurements+1
                    shutil.copy(fulldir,dataset_dir)			#copy into temporary dir
                    shutil.copy(fulldir_meta,dataset_dir)
                    print(newMeasurement.num_samples)
        self.parent.parent.tab4.tab1.analyse_dataset() #do analysis
        self.parent.parent.tab4.tab2.analyse_dataset()
        coords = self.list_coordinates()
        self.parent.parent.tab2.make_polygon(coords)	#make map
        
        
    def make_lambda(self, idd, lat, long):
        return lambda event: self.parent.parent.callback(idd,lat,long)#workaround for lambda function getting overwritten in loops
        
    def clearMeasurement(self):
        print(self.tree.focus())
        
        self.tree.delete(self.tree.selection())
        self.parent.parent.callback(-1,0,0) #clear spectrum
    
    def clearTree(self):
        self.tree.delete(*self.tree.get_children())
        self.measurements = []
        files = glob.glob(dataset_dir)
        name = dataset_dir
        for f in files:
            shutil.rmtree(f)
        os.makedirs(name)			#delete folder and remake - workaround to avoid admin permissions
        self.idMeasurements=0
        self.parent.parent.callback(-1,0,0)
    
    def measure(self):
        location = tk.simpledialog.askstring("Input", "Enter Post Code:") 
        filename = tk.simpledialog.askstring("Input", "Enter File Name:")
        #saveto = tk.filedialog.askdirectory()
        #will need to create an inherited class to combine these into one dialog
        sweeprun = sw.sweep(25e6,1750e6,'max')
        sweeprun.capture()
        sweeprun.writeNew(filename)
        sweepRun.writeMeta(location) #change to desired postcode
        
        #will add a dialog here specifying for how long to measure - need to update sweepclass to accocunt for this

    def list_coordinates(self):
        coords = set()		#list unique coordinates in dataseet
        for measurement in self.measurements:
            coord = measurement.latitude,measurement.longitude
            coords.add(coord)
        return coords
        
        
class AnalysisTab(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self,parent)
        self.parent = parent
        #subtabs
        tabControlAn = ttk.Notebook(self)
        self.tab1 = analysisSubtab1(self)
        self.tab2 = analysisSubtab2(self)
        tabControlAn.add(self.tab1, text ='Measurement Analysis')
        tabControlAn.pack(expand = 1, fill ="both")
        tabControlAn.add(self.tab2, text ='Dataset Analysis')
        tabControlAn.pack(expand = 1, fill ="both")
        
    
class analysisSubtab1(tk.Frame):
    def __init__(self,parent):
        tk.Frame.__init__(self,parent)
        self.parent = parent
        self.f1 = GUI_support.borderFigure(self, (9,5), 100, "black", 2)
        self.f1.grid(row=0,column=0)
        
       
        self.f2 = GUI_support.borderFigure(self, (9,5), 100, "black", 2)
        self.f2.grid(row=0,column=1)
        
        self.grid_columnconfigure(0,weight=1)
        self.grid_columnconfigure(1,weight=1)
        self.grid_rowconfigure(0,weight=1)
        
        
    
    def analyse_dataset(self):	#use analysis class to get parameters
        self.an = analysis_GUI.analysis(_samples_to_average = 5, _dir_path = dataset_dir)
        self.an.get_dataset_files()
                        
    def binarised_data(self,path,Measurement): #get spectrum occupancy for measurement
        self.an.setSigmfData(path)
        self.an.get_threshold(2)
        self.an.binarize()
        bin_data = self.an.bin_data
        freq_axis = np.linspace(Measurement.freq_start, Measurement.freq_stop, Measurement.num_samples)	#restructure, code reuse
        self.f1.fig.clear()
        self.f1.fig.plot(freq_axis,Measurement.data, label='Spectrum')
        self.f1.fig.plot(freq_axis,self.an.threshold, label='thresh')
        self.f1.fig.plot(freq_axis,bin_data, label='binary data')
        self.f1.fig.set_xlabel('Frequency')
        self.f1.fig.set_ylabel('Magnitude')
        self.f1.fig.set_title("Thresholding and binarization of selected data file")
        self.f1.fig.legend()
        self.f1.canvas.draw()
        
        self.f2.fig.clear()
        self.f2.fig.plot(freq_axis,bin_data)
        self.f2.fig.set_xlabel('Frequency')
        self.f2.fig.set_ylabel('Occupancy')
        self.f2.fig.set_title('Binarised occupancy')
        self.f2.fig.set_ylim([0,1])
        
        
        self.f2.canvas.draw()
    
class analysisSubtab2(tk.Frame):
    def __init__(self,parent):
        tk.Frame.__init__(self,parent)
        self.an = analysis_GUI.analysis(_samples_to_average = 5, _dir_path = dataset_dir)
        self.parent = parent
        
        self.f2 = GUI_support.borderFigure(self, (9,4), 100, "black", 2)
        self.f2.grid(row=0,column=0, padx=10, pady=10)
            
        self.f3 = GUI_support.figureAndDialog(self)
                                                        
        self.f3.grid(row=0,column=1, padx=10, pady=10)
            
            
        self.f4 = GUI_support.threeDborderfigure(self, (4,3.5), 100, "black", 2)
        self.f4.grid(row=1,column=1)
        
        self.f5 = GUI_support.borderFigure(self, (5,4), 100, "black", 2)
        self.f5.grid(row=1,column=0)
        
        self.grid_columnconfigure(0,weight=1)
        self.grid_columnconfigure(1,weight=1)
        self.grid_rowconfigure(0,weight=1)
        self.grid_rowconfigure(1,weight=1)
        
    def analyse_dataset(self):
        self.an = analysis_GUI.analysis(_samples_to_average = 5, _dir_path = dataset_dir)
        self.an.get_dataset_files()
        self.an.get_dataset()
        #analyse whole dataset, make plots
        self.plot_bin_dataset(self.parent.parent.tab1.MeasurementList.measurements[1]) # grab a sample measurement to initialise
        self.plot_freqtime(self.parent.parent.tab1.MeasurementList.measurements[1])
        self.plot3D(dec_to= 256, ssample = 0, esample = 23, mode = 'inline', Measurement = self.parent.parent.tab1.MeasurementList.measurements[0])
        self.plotHeatmap()
        
    def plot_bin_dataset(self,Measurement):
        print(self.an.filepaths[0])
        print(Measurement.freq_stop)
        self.an.get_threshold(5)
        #self.an.get_dataset()
        self.an.binarize_dataset()
        p = np.sum(self.an.bin_dataset,axis=0)/len(self.an.bin_dataset[:,1])
        freq_axis = np.linspace(Measurement.freq_start, Measurement.freq_stop, Measurement.num_samples)
        self.f2.fig.clear()
        self.f2.fig.plot(freq_axis,p) #
        self.f2.fig.set_xlabel('Frequency')
        self.f2.fig.set_ylabel('Percentage')
        self.f2.fig.set_title("Binarised Usage per Frequency")
        self.f2.canvas.draw()
        print("overall percentage: "+str(sum(p)/len(p)))
        
    def plot_freqtime(self, Measurement):		##MAKE THIS ADJUSTABLE
        #self.an.get_dataset()
        #df = pd.DataFrame({'data': self.an.raw_dataset[:,1750]})
        data = self.an.raw_dataset[4,:]
        freq_axis = np.linspace(Measurement.freq_start, Measurement.freq_stop, Measurement.num_samples)
        self.f3.fig.clear()
        self.f3.fig.plot(np.arange(150,841,1),data[150:841])
        self.f3.fig.set_xlabel('Sample time [hrs]')
        self.f3.fig.set_ylabel('Magnitude')
        self.f3.fig.set_title("Observed frequency : 218.76 MHz")
        self.f3.canvas.draw()
        
    def plot3D(self, dec_to= 256, ssample = 0, esample = 23, mode = 'inline', Measurement = []):
        k = int(len(self.an.raw_dataset[1,:])/dec_to)
        data = scipy.signal.decimate(self.an.raw_dataset,k,axis = 1)
        z = data[ssample:esample,:]
        
        print("data shape to plot = "+str(data.shape))
        nrows, ncols = z.shape
        x = np.linspace(Measurement.freq_start, Measurement.freq_stop, ncols)
        y = np.linspace(ssample, esample, nrows)
        x, y = np.meshgrid(x, y)


        self.f4.fig.clear()
        ls = LightSource(270, 45)

        
        rgb = ls.shade(z, cmap=cm.gist_earth, vert_exag=0.1, blend_mode='soft')
        
        surf = self.f4.fig.plot_surface(x, y, z, rstride=1, cstride=1, facecolors=rgb,
                                   linewidth=0, antialiased=False, shade=False)
        self.f4.fig.set_xlabel("Frequency [MHz]")
        self.f4.fig.set_ylabel("Samples [n]")
        self.f4.fig.set_zlabel("Magnnitude [dBFS]")
        self.f4.canvas.draw()
        
        
    def plotHeatmap(self):
        data = self.an.raw_dataset[1:]
        print(data.shape)
        print(self.an.filepaths)
                
        self.f5.fig.clear()
        self.f5.fig.set_title('Heatmap (Dataset)')
        self.f5.fig.set_ylabel('Time (Hrs)')
        self.f5.fig.set_xlabel('Frequency (Hrs)')
        self.f5.fig.imshow(data, extent = [self.an.f_axis[0], self.an.f_axis[-1], len(data[:,1])-1, 0], aspect="auto")
        #ax.set_aspect('equal')

        self.cax = self.f5.f.add_axes([0, 1, 0, 1])
        self.cax.get_xaxis().set_visible(False)
        self.cax.get_yaxis().set_visible(False)
        self.cax.patch.set_alpha(0)
        self.cax.set_frame_on(False)
        self.f5.canvas.draw()
        

class Measurement(object): 	#store info for linking between treeview/map/analysis
    def __init__(self, samples, metadata, id, path):
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
        self.parent = parent
        self.mapwidget = tkintermapview.TkinterMapView(self,width=800,height=800) #might need to read from display size
        self.mapwidget.set_position(55.86, -4.21)
        self.mapwidget.set_tile_server("https://mt0.google.com/vt/lyrs=m&hl=en&x={x}&y={y}&z={z}&s=Ga", max_zoom=22)
        self.mapwidget.set_position(55.86152790155066, -4.246978736010148)	#default position
        self.mapwidget.pack()

class LiveSpectrum(tk.Frame):	#alternative spectrum for live updating
    def __init__(self, parent):
        tk.Frame.__init__(self,parent)
        self.parent = parent
        self.f = Figure(figsize=(20,6), dpi=100)
        self.fig = self.f.add_subplot(111)
        self.ax = plt.axes()
        self.line, = self.ax.plot([], [], lw=3)
        self.line.set_data([], [])
        self.fig.set_xlabel('Frequency (Hz)')
        self.fig.set_ylabel('Magnitude (dbM)')
        self.fig.set_title("Frequency Spectrum (Selected Data)")
        self.addgrid()
        self.freq_axis = np.linspace(0.0, 2048000000.0, 4096) #defaults
        self.data = []
        self.fig.set_xlim([0, 2048000000])
        self.fig.set_ylim([-150, -50])
                          
        self.canvas = FigureCanvasTkAgg(self.f, self)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)
        
    def refresh(self, samples, num_samples):
        self.fig.clear()
        self.fig.grid()
        self.fig.set_xlabel('Frequency (Hz)')
        self.fig.set_ylabel('Magnitude (dBFS)')
        self.fig.set_title("Frequency Spectrum (Current)")
        self.freq_axis = np.linspace(0.0, 2048000000.0, num_samples)
        self.fig.plot(self.freq_axis, samples, linewidth = 0.5)
        self.canvas.draw();

    def addgrid(self):
        self.fig.grid()


class LiveViewTab(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self,parent)
        self.parent = parent
        self.config_path = r"\\192.168.3.1\xilinx\jupyter_notebooks\strathRFM\config.pkl"
        self.data_path = r"\\192.168.3.1\xilinx\jupyter_notebooks\strathRFM\data.pkl"
        self.fs = 4096*1e6
        if os.path.isfile(self.config_path):	#check for rfsoc
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
        else: print("no RFSoC connected or data path error")
        self.Spectrum = LiveSpectrum(self)
        
        self.Spectrum.addgrid()
        self.Spectrum.grid(row=0,column=0)
        self.startbutton = tk.Button(self, 
                   text="Start", 
                   command=self.startstream)
        self.startbutton.grid(row=1,column=0)
        self.stopbutton = tk.Button(self, 
                   text="Stop", 
                   command=self.stopstream)
        self.stopbutton.grid(row=2,column=0)
        self.stopbutton['state'] = ['disabled']
        self.status = 0;
        self.data = []
        
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
                dict = {}
                res =  False
        return res, dict
            
    def pickleFile(self, file_path, data): #pickle/data stream with failsafes
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
        if self.status:
        
                self.config[b'single_frame_enable'] = True
                self.config[b'changed'] = True
                self.pickleFile(self.config_path, self.config)
                self.config[b'single_frame_enable'] = False
                self.config[b'changed'] = False
                result, self.data = self.unpickleFile(self.data_path)
                
                _,  self.config = self.unpickleFile(self.config_path)
                if result:
                    print(len(self.data[b'data']))
                    # data has lower lim upper lim and data you can get length using ^^
                    print(len(self.data[b'data']))
                    print(self.data[b'lower_lim'])
                    print(self.data[b'upper_lim'])
                    self.live_graph(self.data)
                else:
                    print("no data returned")
            
        
 
    def live_graph(self, data):
        self.Spectrum.refresh(data[b'data'], len(data[b'data']))
        self.after(100, self.stream_data)
    
    def startstream(self):
        self.startbutton['state'] = ['disabled']		#flip-flop buttons
        self.stopbutton['state'] = ['normal']
        self.status = 1
        self.stream_data()
        
    def stopstream(self):
        self.startbutton['state'] = ['normal']
        self.stopbutton['state'] = ['disabled']
        self.stream_data()
        self.status = 0
    
    
# this method checks that the inputs are as expected. 
# Returns True if no errors have been encountered.
# The err variable is a string of all the errors encountered  
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


with tempfile.TemporaryDirectory() as dataset_dir:	#temp directory for storing dataset, gets wiped on exit
    window = MainWindow(); #window instance
    width, height = window.winfo_screenwidth()/2, window.winfo_screenheight()-200
    window.geometry('%dx%d+0+0' % (width,height))
    window.protocol("WM_DELETE_WINDOW", window.on_closing)
    window.mainloop();