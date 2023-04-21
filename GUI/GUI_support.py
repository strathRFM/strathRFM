#Custom frame builds to support GUI
import tkinter as tk
import tkinter.ttk as ttk
import tkinter.font as tkFont
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk #canvas and toolbar to use as objects
from matplotlib.figure import Figure

class borderFigure(tk.Frame):	#figure with borders around its frame for aesthetics
    def __init__(self,parent, figsize, dpi, highlightbackground, highlightthickness):
        super().__init__(parent, highlightbackground=highlightbackground, highlightthickness=highlightthickness)
        self.highlightbackground=highlightbackground
        self.highlightthickness=highlightthickness
        self.parent = parent
        self.f = Figure(figsize=figsize, dpi=dpi)
        self.fig = self.f.add_subplot(111)
        self.fig.plot([1,2,3,4,5,6,7,8],[1,2,3,4,5,6,7,8])
        self.canvas = FigureCanvasTkAgg(self.f, self)
        self.canvas.draw()
        toolbar = NavigationToolbar2Tk( self.canvas, self )
        self.canvas.get_tk_widget().pack()
        
class figureAndDialog(tk.Frame):		#figure with dialog for setting frequency in 2nd figure - to do: add support
    def __init__(self,parent):
        super().__init__(parent, highlightbackground="black", highlightthickness=2)
        self.parent = parent
        self.f = Figure(figsize=(9,4), dpi=100)
        self.fig = self.f.add_subplot(111)
        self.fig.plot([1,2,3,4,5,6,7,8],[1,2,3,4,5,6,7,8])
        self.canvas = FigureCanvasTkAgg(self.f, self)
        self.canvas.draw()
        #self.canvas.get_tk_widget().grid(row=0,column=0)
        toolbarFrame = tk.Frame(self)
        toolbarFrame.grid(row=1,column=0,columnspan = 3)
        toolbar = NavigationToolbar2Tk(self.canvas, toolbarFrame)
        #toolbar = NavigationToolbar2Tk( self.canvas, self )
        self.canvas.get_tk_widget().grid(row = 0, column = 0,columnspan = 3)
        self.labelText=tk.StringVar(self)
        self.labelText.set("Select Frequency:")
        self.label1=tk.Label(self, textvariable=self.labelText, height=4)
        #self.label1.grid(row=0,column=1)
        self.label1.grid(row = 2, column = 0)

        self.box=tk.StringVar(self)
        self.freq=tk.Entry(self,textvariable=self.box,width=50)
        #self.freq.grid(row=1,column=1)
        self.freq.grid(row = 2, column = 1)
        self.button = tk.Button(self, 
                   text="Analyse", 
                   command=None)
        
        self.button.grid(row = 2, column = 2)
        
        self.grid_columnconfigure(0,weight=1)
        self.grid_columnconfigure(1,weight=1)
        self.grid_columnconfigure(2,weight=1)
        self.grid_rowconfigure(0,weight=1)
        self.grid_rowconfigure(1,weight=1)
        
        
class threeDborderfigure(tk.Frame):
     def __init__(self,parent, figsize, dpi, highlightbackground, highlightthickness):
        super().__init__(parent, highlightbackground=highlightbackground, highlightthickness=highlightthickness)
        self.highlightbackground=highlightbackground
        self.highlightthickness=highlightthickness
        self.parent = parent
        self.f = Figure(figsize=figsize, dpi=dpi)
        self.fig = self.f.add_subplot(111, projection = '3d')
        self.fig.plot([1,2,3,4,5,6,7,8],[1,2,3,4,5,6,7,8])
        self.canvas = FigureCanvasTkAgg(self.f, self)
        self.canvas.draw()
        toolbar = NavigationToolbar2Tk( self.canvas, self )
        self.canvas.get_tk_widget().pack()