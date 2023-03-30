from sigmf import SigMFFile, sigmffile
import matplotlib.pyplot as plt
import numpy as np
import os


# Load a dataset
#filename = 'MearnsTest/S_12-03-23_16.sigmf-data' # extension is optional
folder = 'C:\\Users\\eilid\\mengsdr\\RFSoC\\Troon spectrum data'


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


for file in sorted(os.listdir(folder)):
    if file.endswith(".sigmf-data"):
        spectrumDict = getSigmfData(folder+"\\"+file)
        freq_start = spectrumDict[b'lower_lim']
        freq_stop = spectrumDict[b'upper_lim']
        num = spectrumDict[b'samples']
        samples = np.array([spectrumDict[b'data']])

##        freq_axis = np.linspace(freq_start, freq_stop, num)
##        plt.figure()
##        plt.plot(freq_axis, samples, linewidth = 0.5)
##        plt.plot(samples)
##        plt.show()
        freq_axis = np.linspace(spectrumDict[b'lower_lim'], spectrumDict[b'upper_lim'], num = spectrumDict[b'samples'])
        plt.figure()
        plt.plot(freq_axis, spectrumDict[b'data'], linewidth = 0.5)
        plt.show()
