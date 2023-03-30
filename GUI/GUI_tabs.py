import tkinter as tk
import tkinter.ttk as ttk
import tkinter.font as tkFont
import tkintermapview
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
matplotlib.use("TkAgg")#if changing back end
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg #canvas and toolbar to use as objects

#will need to edit the toolbar later (or get rid of it)
from matplotlib.figure import Figure
import SweepClassEilidh as sw
from readData import getSigmfData
import os
#window->frames->widgets structure

class MainWindow(tk.Tk):
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        
        
        tabControl = ttk.Notebook(self)
        
        
        #instantiate frames and place in window
        self.tab1 = MeasurementTab(self)
        self.tab2 = MapTab (self)
        self.tab3 = LiveViewTab(self)
        self.tab4 = AnalysisTab(self)
        
        #need to look into how to make tabs deatachable
        
        
        tabControl.add(self.tab1, text ='Measurements')
        #tabControl.add(self.frame2, text ='Tab 2')
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
        
#         self.frame1.grid(row=0, column=0, sticky="nsew")
#         self.frame2.grid(row=1,column=0, sticky="nsew")
#         self.frame3.grid(row=0, column=1, sticky="nsew")
#         self.frame4.grid(row=1, column=1, sticky="nsew")
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
        
    
    def refresh_spectrum(self,data,freq_start,freq_stop,num_samples):
        self.tab1.Spectrum.refresh(data,freq_start,freq_stop,num_samples)
        
    def refresh_map(self,latitude,longitude):
        self.tab2.map.refresh_coordinates(latitude,longitude)
        
        
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
        
      

class AnaylsisTab(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self,parent)
        self.parent = parent
        

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
                    newMeasurement = Measurement(samples,metadata,self.idMeasurements)
                    self.tree.insert('', tk.END, iid = newMeasurement.id,
                                     text = newMeasurement.time,
                                     values = (newMeasurement.date,str(newMeasurement.latitude)+', '+str(newMeasurement.longitude),
                                                newMeasurement.device),
                                     tags = newMeasurement.id)
                    self.tree.tag_bind(newMeasurement.id, '<Button-1>',
                                       self.make_lambda(newMeasurement.id,newMeasurement.latitude,newMeasurement.longitude))
                    self.measurements.append(newMeasurement)
                    self.idMeasurements=self.idMeasurements+1
                                         
        
        
    def make_lambda(self, idd, lat, long):
        return lambda event: self.parent.parent.callback(idd,lat,long)#workaround for lambda function getting overwritten in loops
        
    def clearMeasurement(self):
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
        sweepRun.writeMeta(location) #change to desired postcode
        
        #will add a dialog here specifying for how long to measure - need to update sweepclass to accocunt for this
        #add indiciation that measuring is happening and option to interrupt
        
        
class AnalysisTab(tk.Frame):
    def __init__(self, parent):
        #placeholder - things to put: bandwidth, occupied%,unoccupied%,  ??
        tk.Frame.__init__(self,parent)
        self.parent = parent
        self.bandwidth = 2
        self.occupied = 0
        self.unoccupied = 100
        self.text = tk.Text(self,height=100,width=100)
        text1 = "Placeholder"
        self.text.insert(tk.END,text1)
        self.text.pack()
        
                

class Measurement(object): 	#store info for linking between treeview/map/analysis
    def __init__(self, samples, metadata,id):
    #will need to add failsafes for formatting etc
        self.freq_start = samples[b'lower_lim']
        self.freq_stop = samples[b'upper_lim']
        self.id = id
        self.num_samples = samples[b'samples']
        self.data = samples[b'data']
        self.device = metadata['device']
        self.coord = metadata['geolocation']['coordinates']
        self.datetime = metadata['datetime']
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
        self.mapwidget.set_position(55.86152790155066, -4.246978736010148)
        self.mapwidget.pack()
        
    def refresh_coordinates(self,lat,long):
        self.mapwidget.set_position(lat, long)
        self.mapwidget.pack()
        

class LiveViewTab(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self,parent)
        self.parent = parent
        #to be completed
        
        
            


window = MainWindow(); #window instance
width, height = window.winfo_screenwidth()/2, window.winfo_screenheight()-200
window.geometry('%dx%d+0+0' % (width,height))
window.mainloop();