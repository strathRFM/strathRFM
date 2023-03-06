#!/usr/bin/env python
# coding: utf-8

# In[158]:


from sigmf import SigMFFile, sigmffile
from matplotlib import cbook
from matplotlib import cm
from matplotlib.colors import LightSource
import matplotlib.pyplot as plt
#from mpl_toolkits.mplot3d import axes3d
import numpy as np
import tarfile
  
# unzips the compressed file and puts it into destination
def unzipTar(filename = '', destination = '.'):
    file = tarfile.open(filename)
    # extracting file
    file.extractall(destination)
    file.close()

# plot a singple sigMF data
def sigmfPlot(filename):
#filename = 'Falkirk.sigmf-data' # extension is optional
    signal = sigmffile.fromfile(filename)

    # Get some metadata and all annotations
    sample_rate = signal.get_global_field(SigMFFile.SAMPLE_RATE_KEY)
    annotations = signal.get_annotations()

    for adx, annotation in enumerate(annotations):
        annotation_start_idx = annotation[SigMFFile.START_INDEX_KEY]
        annotation_length = annotation[SigMFFile.LENGTH_INDEX_KEY]
        annotation_comment = annotation.get(SigMFFile.COMMENT_KEY, "[annotation {}]".format(adx))

        # Get capture info associated with the start of annotation
        capture = signal.get_capture_info(annotation_start_idx)
        freq_center = capture.get(SigMFFile.FREQUENCY_KEY, 0)

        # Get frequency edges of annotation (default to edges of capture)
        freq_start = annotation.get(SigMFFile.FLO_KEY)
        freq_stop = annotation.get(SigMFFile.FHI_KEY)

        # Get the samples corresponding to annotation
        samples = signal.read_samples(annotation_start_idx, annotation_length)

        freq_axis = np.linspace(freq_start, freq_stop, num = annotation_length)
        plt.figure()
        plt.plot(freq_axis, samples, linewidth = 0.5)
        plt.show()
        
# returns a dict with sigmf data.
def getSigmfData(filename):
    signal = sigmffile.fromfile(filename)

    # Get some metadata and all annotations
    sample_rate = signal.get_global_field(SigMFFile.SAMPLE_RATE_KEY)
    annotations = signal.get_annotations()

    for adx, annotation in enumerate(annotations):
        annotation_start_idx = annotation[SigMFFile.START_INDEX_KEY]
        annotation_length = annotation[SigMFFile.LENGTH_INDEX_KEY]
        annotation_comment = annotation.get(SigMFFile.COMMENT_KEY, "[annotation {}]".format(adx))

        # Get capture info associated with the start of annotation
        capture = signal.get_capture_info(annotation_start_idx)
        freq_center = capture.get(SigMFFile.FREQUENCY_KEY, 0)

        # Get frequency edges of annotation (default to edges of capture)
        freq_start = annotation.get(SigMFFile.FLO_KEY)
        freq_stop = annotation.get(SigMFFile.FHI_KEY)

        # Get the samples corresponding to annotation
        samples = signal.read_samples(annotation_start_idx, annotation_length)

        
        dict = { b'lower_lim': freq_start, b'upper_lim': freq_stop ,b'samples': annotation_length,b'data': samples}
    return dict
    
# plots a spectrum dictionary
def plotSpectrumDict(spectrumDict):
    freq_axis = np.linspace(spectrumDict[b'lower_lim'], spectrumDict[b'upper_lim'], num = spectrumDict[b'samples'])
    plt.figure()
    plt.plot(freq_axis, spectrumDict[b'data'], linewidth = 0.5)
    plt.show()

#  3d plots a range of datapoints within a single day.
: # e.g. spectrum_data/S_01-03-23, 'hill or 'wire', stime = start time, etime = end time  
def plotDay(filepath, mode = 'hill', stime = 0,etime = 23)
    # will plot from hr 0 to 23
    
    
    file = filepath + '_' + "{:02d}".format(stime)
    spectrumDict = getSigmfData(file)
    low_lim = spectrumDict[b'lower_lim']
    up_lim = spectrumDict[b'upper_lim']
    num = spectrumDict[b'samples']
    data = np.array([spectrumDict[b'data']])
    for i in range(stime+1,etime+1):
        file = filepath + '_' + "{:02d}".format(i)
        spectrumDict = getSigmfData(file)
        npData = spectrumDict[b'data']
        data = np.concatenate((data,[npData]),axis=0)

    # Load and format data
    #dem = cbook.get_sample_data('jacksboro_fault_dem.npz', np_load=True)
    
    print("data shape = "+str(data.shape))
    z = data
    nrows, ncols = z.shape
    x = np.linspace(low_lim, up_lim, ncols)
    y = np.linspace(stime, etime, nrows)
    x, y = np.meshgrid(x, y)

    #region = np.s_[5:50, 5:50]
    #x, y, z = x[region], y[region], z[region]
    # interactive plots
    get_ipython().run_line_magic('matplotlib', 'qt')
    # normal plots
    #%matplotlib inline 
    # Set up plot
    
    fig, ax = plt.subplots(subplot_kw=dict(projection='3d'))
    plt.rcParams['figure.figsize'] = [12, 12]
    plt.rcParams['figure.dpi'] = 100 # 200 e.g. is really fine, but slower
    plt.title(filepath + " from hours "+str(stime)+ " to " +str(etime))
    ls = LightSource(270, 45)

    ax.set_xlabel("Frequency [Hz]")
    ax.set_ylabel("time [Hr]")
    ax.set_zlabel("Magnnitude [dBFS]")
    
    # To use a custom hillshading mode, override the built-in shading and pass
    # in the rgb colors of the shaded surface calculated from "shade".
    rgb = ls.shade(z, cmap=cm.gist_earth, vert_exag=0.1, blend_mode='soft')
    if(mode == 'hill'):
        
        surf = ax.plot_surface(x, y, z, rstride=1, cstride=1, facecolors=rgb,
                               linewidth=0, antialiased=False, shade=False)


    if(mode == 'wire'):
        surf = ax.plot_surface(x, y, z, rstride=1, cstride=1, facecolors=rgb,
                               linewidth=0.1, antialiased=False, shade=False)
        surf.set_facecolor((0,0,0,0))
        
    plt.show()


# In[24]:


unzipTar('spectrum_data.tar.gz')

spectrum = getSigmfData('spectrum_data/S_01-03-23_22')

#sigmfPlot("S_25-02-23_12")


# In[103]:


plotDay('spectrum_data/S_26-02-23')


# In[162]:



plotDay('spectrum_data/S_28-02-23', stime = 4, etime = 8)
#sigmfPlot("spectrum_data/S_25-02-23_12")


# In[ ]:




