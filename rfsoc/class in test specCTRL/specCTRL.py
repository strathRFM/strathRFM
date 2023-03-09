#import "spectrum.py"
import pickle
import time
import numpy as np
class SpecCTRL:
    def __init__(self,_config_Path = "config.pkl", # path to the configuration file writable by GUI
                 _spec_Data_Stream_Path = "data.pkl", # path of data file writable from this calss
                _status_file_path = ""):   # path of the file for specCTRL status for GUI
        
        self.config_Path = _config_Path
        self.spec_Data_Stream_Path = _spec_Data_Stream_Path
        self.status_file_path = _status_file_path
        #self.spec = spectrum()
        self.start_on_boot = True
        self.continuous_scan_enable = True
        self.full_spectrum_scan = False # enable full spectrum scan
        self.stream_data_enable = False
        self.data_file_ready = True    # if data file was read changed from GUI
        self.data_file_written = False # indicate that the data file has been written
        self.app_enable = True         # continuously check if system needs to run.
                                       # if False exit specCTRL class and continue with boot.
        self.fft_size = 4096
        #self.centre_frequency = spec.centre_frequency
        #self.decimation_factor = spec.decimation_factor
        
        
        
    def continuous_scan(self):
        # need to modify continuous scan to only progress if 
        #self.spec.continuous_scan(prog)
        print("scanning continuously.")
       
    def unpickleFile(self, file_path):
        try:
            with open(file_path, 'rb') as fo:
                dict = pickle.load(fo, encoding='bytes')
                return True, dict
        except:
            dict = {}
            return False, dict
            
    def pickleFile(self, file_path, data):
        try:
            pickle.dump(data, open(file_path, 'wb'))
            return True
        except:
            return False
        
        
    def create_config(self):
        config_file = {b'continuous_scan_enable': True,
                      b'data_file_ready':True,
                      b'start_on_boot': False,
                      b'full_spectrum_scan':True,
                      b'fft_size':4096,
                      b'app_enable':True,
                      b'stream_data_enable':False}
        res = self.pickleFile(self.config_Path, config_file)
    
    def check_config(self):
        # this function loads in the config file and updates class variables
        res, config_file = self.unpickleFile(self.config_Path)
        idx = 0
        while(res == False):
            time.sleep(4)
            idx += 1
            res, config_file = self.unpickleFile(self.config_Path)
            if(idx >10):
                break
            
        self.continuous_scan_enable = config_file[b'continuous_scan_enable'] # or False
        self.stream_data_enable = config_file[b'stream_data_enable']
        self.data_file_ready = config_file[b'data_file_ready']
        self.start_on_boot = config_file[b'start_on_boot']
        self.app_enable = config_file[b'app_enable']
        self.full_spectrum_scan = config_file[b'full_spectrum_scan']
        # check time and update if discrepancy is detected
        
        # check other spectrum parameters
        # if different than what is stored here, than update them in spectrum class
        # and here
        if(self.fft_size != config_file[b'fft_size']):
            #self.spec.set_fft_size(file["fft_size"])
            self.fft_size = config_file[b'fft_size']
        
    
    def send_spec_data(self):
        while(self.stream_data_enable):
            time.sleep(0.01)
            if(self.data_file_ready):
                data = np.add(np.random.rand(2048,1)*2,-1)
                
                # get_frame instead of random numbers
                toFile = {b'upper_lim': 2048,
                          b'lower_lim': 0,
                          b'nr_samples': len(data),
                          b'data': data}
                self.pickleFile(self.spec_Data_Stream_Path,toFile)
            self.check_config()
                
        
    def start_CTRL(self):
        while(self.app_enable):
            self.print_file()
            time.sleep(4)
            self.check_config()
            if(self.continuous_scan_enable):
                # background gather data for dataset
                print("continuous scan enabled.")
                self.continuous_scan()
            if(self.stream_data_enable):
                # send data to GUI trough stream data file.
                print("sending data to GUI.")
                self.send_spec_data()
            
            