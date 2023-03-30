from sigmf import SigMFFile, sigmffile
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import os


# Load a dataset
#filename = 'MearnsTest/S_12-03-23_16.sigmf-data' # extension is optional
folder = 'MearnsTest'


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

i = 0
n = 0
for file in sorted(os.listdir(folder)):
    if file.endswith(".sigmf-data"):
        n = n + 1
    
for file in sorted(os.listdir(folder)):
    if file.endswith(".sigmf-data"):
        spectrumDict = getSigmfData(folder+"\\"+file)
        freq_start = spectrumDict[b'lower_lim']
        freq_stop = spectrumDict[b'upper_lim']
        num = spectrumDict[b'samples']
        samples = spectrumDict[b'data']

##        freq_axis = np.linspace(freq_start, freq_stop, num)
##        plt.figure()
##        plt.plot(freq_axis, samples, linewidth = 0.5)
##        plt.plot(samples)
##        plt.show()
##        freq_axis = np.linspace(spectrumDict[b'lower_lim'], spectrumDict[b'upper_lim'], num = spectrumDict[b'samples'])
##        plt.figure()
##        plt.plot(freq_axis, spectrumDict[b'data'], linewidth = 0.5)
##        plt.show()
        if i == 0:
            #avg = samples/len(sorted(os.listdir(folder)))
            allSamples = np.zeros((len(samples), n))
            print(allSamples.shape)
        #else:
            #avg = avg + samples/len(sorted(os.listdir(folder)))
            
        allSamples[:, i] = samples
        avg = np.mean(allSamples, axis = 1)
        mins = np.min(allSamples, axis = 1)
        i = i + 1
        
        

print(samples.shape)
print(avg.shape)


freq_axis = np.linspace(freq_start, freq_stop, num)
df = pd.DataFrame(avg)
ma = df.ewm(span = 40).mean()
p = np.poly1d(np.polyfit(freq_axis, ma[0], 16))
fitted_line = p(freq_axis)
fitted_w_offset = fitted_line + 4

plt.figure()
plt.plot(freq_axis, allSamples[:,0], linewidth = 0.5)
plt.plot(freq_axis, ma, linewidth = 0.5)
plt.plot(freq_axis, fitted_w_offset, linewidth = 0.5)
#plt.plot(freq_axis, mins, linewidth = 0.5)
plt.show()
