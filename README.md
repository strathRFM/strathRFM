![screenshot](logo.png?raw=true)
## strath Radio Frequency Mapping

# Description:
strathRFM is a system that can generate datasets of the RF spectrum and map it using the easy to use GUI.

The currently supported devices are: rtl-sdr, rfsoc 2x2, rfsoc 4x2, ZCU111

bla bla bla and bla

# install
## Linux: 

copy and panste use python command

## rfsoc:
Please also see [rfsoc_sam](https://github.com/strath-sdr/rfsoc_sam), [SigMF](https://github.com/sigmf/SigMF) and [GeoJSON](https://geojson.org) for detailed info of libraries used.

This project requires the sigmf and geojson libraries to be installed on the device. To do so, power on the RFSoC device, connect an ethernet cable and 
finally connect to jupyterLab using a browser of your choice (192/168/3/1 password: xilinx). Once connected open a new terminal and run the following commands
```
pip install sigmf geojson
```
This will install the libraries. To install strathRFM the following commands can be pasted or typed into the console and run. This will download all the 
necessary files onto the correct location that are required to be.
```
mkdir /home/xilinx/jupyter_notebooks/strathRFM
mkdir /home/xilinx/jupyter_notebooks/strathRFM/spectrum_data
cd /home/xilinx/jupyter_notebooks/strathRFM/spectrum_data
wget https://github.com/strathRFM/strathRFM/raw/main/rfsoc/strathRFM/Notebook_CTRL.ipynb
wget https://github.com/strathRFM/strathRFM/raw/main/rfsoc/strathRFM/spectrum.py
wget https://github.com/strathRFM/strathRFM/raw/main/rfsoc/strathRFM/specCTRL.py
wget https://github.com/strathRFM/strathRFM/raw/main/rfsoc/strathRFM/spectrumWidgets.py
cd /boot
rm boot.py
wget https://github.com/strathRFM/strathRFM/raw/main/rfsoc/Other/boot.py
```
Once complete, the **specCTRL.py** can be run from the terminal as follows:
```
python /home/xilinx/jupyter_notebooks/strathRFM/specCTRL.py
```
This will initialise the strathRFM data generation algorithm on the RFSoC in idle mode. By navigating to StrathRFM (jupyter_notebooks/strathRFM) and opening the **Notebook_CTRL.ipynb** file, the spectrum can be set up and tested or dataset generation can be initialiased. Alternatively, the same can be achieved using the included GUI for data analisys and data generation. if permission issues are encountered change folder permissions of strathRFM using the following commands
```
cd home/xilinx/jupyter_notebooks/
chmod -R 777 strathRFM
```




## windows:

download exe or compile source code in the GUI folder

# Live View RFSoC

For more immersive live spectrum analyser experience, the samba interface must be adapted to update as soon as possible. To do so the samba configuration file must be changed. This can be achieved trough the Jupyter Notebooks terminal within the JupyterLab as follows:
* First lets open the samba configuration file:
```
sudo vi /etc/samba/smb.conf
```
* This will open the editor now you can navigate down and under globals section and press insert which will allow the file editing, insert the following command
```
oplocks = False
```
To save the changes first prest 'ESC' and 'ZZ' Z twice. At this point it will exit vim and the RFSoC can be restarted using
```
sudo reboot now
```
Once the system has restarted the changes have taken effect and the samba drive will be updated in real time.

## RTL-SDR:

To use the RTL-SDR in Python the following library is needed: pyrtlsdr. The library can be installed using the following pip command:
```
pip install pyrtlsdr
```
Once downloaded the python package requires some dependices called librtlsdr, to work correctly. The package can be accessed from here https://github.com/librtlsdr/librtlsdr/releases. 
We used **rtlsdr-bin-w64_dlldep.zip** package.

![image](https://user-images.githubusercontent.com/99476167/229078556-f01f6f8b-6f58-440d-9356-2a92506e1988.png)

Extract the zip and save it within a working directory. We commonly used our C drive. The next step is to find the Python program files within your computer system. The file location can be found by using the following file path:

**C:\Users\44750\AppData\Local\Programs\Python\Python39\Lib\site-packages\rtlsdr**

Locate the file 'librtlsdr.py' and modify as shown below:

![image](https://user-images.githubusercontent.com/99476167/229480270-fe2a1ea1-52e6-4349-bbe3-5dd770f18e2a.png)

Save the file and run a basic script with the RTL-SDR to check the driver was installed correctly.
