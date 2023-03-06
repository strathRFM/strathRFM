import tkinter as tk
import tkinter.ttk as ttk
import tkinter.font as tkFont
import matplotlib
import matplotlib.pyplot as plt
matplotlib.use("TkAgg")#if changing back end
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg #canvas and toolbar to use as objects

#will need to edit the toolbar later (or get rid of it)
from matplotlib.figure import Figure


#window->frames->widgets structure

class MainWindow(tk.Tk):
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        
        #instantiate frames and place in window
        frame1 = MeasurementList(self)
        frame2 = Spectrum(self)
        frame1.grid(row=0, column=0, sticky="nsew")
        frame2.grid(row=1,column=0, sticky="nsew")

        
class Spectrum(tk.Frame):
    
    def __init__(self, parent):
        tk.Frame.__init__(self,parent)
        
        self.parent = parent
        f = Figure(figsize=(5,5), dpi=100)
        a = f.add_subplot(111)
        a.plot([1,2,3,4,5,6,7,8],[1,2,3,4,5,6,7,8])	##PLACEHOLDER - just checking graph works - need to implement reading
                                                    ##data from sigmf file
        canvas = FigureCanvasTkAgg(f, self)
        canvas.draw()
        canvas.get_tk_widget().pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)
                
class MeasurementList(tk.Frame): #tree widget for listing measurements and properties
    
    ##could include a slider to flip through simultaneous measurements in a set
    
    def __init__(self, parent):
        tk.Frame.__init__(self,parent)
        self.parent = parent
        columnTitles = ("Date","Location","Device") #leave "Time" out as there is a default column that gets renamed to that
        self.tree = ttk.Treeview(self, columns = columnTitles, height = 20)
        
        #self.tree.pack(padx = 5, pady = 5)
        # can probably iterate this
        self.tree.heading('#0', text='Time')
        self.tree.heading('Date', text='Date')
        self.tree.heading('Location', text='Location')
        self.tree.heading('Device', text='Device')
        self.tree.pack()	#pack places the widget within the frame, grid places the frame within the window
        
        self.read_data()
    
    def read_data(self):	##PLACEHOLDER - when integrating with sigmf this will be a separate class to read the files -
                        ## I'm just using this to check the tree widget works
        self.tree.insert('', tk.END, iid = 0, text = "13:37:00", values = ("2023-2-8","55.8500685769559, -4.258316598153756","rtl-sdr"))
        
        #need to think about how to link the tree widget with the spectrum

window = MainWindow(); #window instance
window.mainloop();