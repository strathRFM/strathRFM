![screenshot](logo.png?raw=true)
# strath Radio Frequency Mapping

# Motivation:

Project Motivation: The Radio Frequency (RF) Spectrum has been under increasing pressure in recent years due to a demand for data capacity and bandwidth increasing. The spectrum is a limited resource due to the fact a given space in the spectrum can only be utilised by  one user at a time to prevent inter-channel interference (ICI). Spectrum allocation across the world is primary organised by a countries government, where portions of the spectrum are allocated for specific uses e.g. military or portions can be auctioned. This process allows no ICI to take place but means the spectrum allocation is inefficient due to the users not always utilising the allocated spectrum. This means the allocated space has become static.

# Description:
strathRFM is a system that can generate datasets of the RF spectrum and map it using the easy to use GUI.The currently supported devices are: rtl-sdr, rfsoc 2x2, rfsoc 4x2, ZCU111
# Acknowledgements:
We would like to thank the University's [strathSDR](https://github.com/strath-sdr) team for continuous support duing the progress of the project, [AMD xilinx](https://www.xilinx.com/) for sponsoring the project by providing the RFSoC devices.

# Dataset:
Two Datasets have been generated usind the RFSoC device. The spectrum has been recorded in two different locations, Troon and Dennistoun (Scotland), for a time span of 1000 hrs each (6 weeks). Additional test sample data can be also downloaded for the RTL-SDR, all data they can be downloaded for futher study or compariosn. Please visit [sigMF](https://github.com/sigmf/SigMF) for file format documentation and permissions.

## RTL-SDR:
The RTL-SDR connects with a host PC via USB 2.0, When the device is connected is uses Sweep class in the PC to capture spectrum data hourly. The data is then passed to the GUI to be viewed and analysed.

## RFSoC
The RFSoC device uses a spectrum analyser to capture data within the range of 0-2 GHz. The analyser interacts with a spectrum class which allows for a continuous data scan to take place. The spectrum control class controls the spectrum class using the configuration file that can be accessed and edited from various locations. The boot process enables the RFSoC to boot up and initialise the algorithm in the required mode without the need of external input.
### JupyterLab - JupyterNotebooks
The JupyerLab notebooks widget can be used directly on the board to set up and control the functioning of the device, or alternatively from a PC using Jupyter Notebooks with "Samba" connection.
<p align="center">
  <img src="./rfsoc/other/jupyter.png" width="50%" height="50%" />
</p>

## GUI
The Graphical User Interface (GUI) is used to visualise data from the RTL-SDR and RFSoC automatically, where users can select data to be analysed and mapped using the spectrum view and map view functionality. Devices can be set up to generate  dataset using the GUI. While the spectrum can be inspected in real time using the RFSoC live view functionality.


# install


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
mkdir /home/xilinx/jupyter_notebooks/strathRFM/other
cd /home/xilinx/jupyter_notebooks/strathRFM
wget https://github.com/strathRFM/strathRFM/raw/main/rfsoc/Notebook_CTRL.ipynb
wget https://github.com/strathRFM/strathRFM/raw/main/rfsoc/spectrum.py
wget https://github.com/strathRFM/strathRFM/raw/main/rfsoc/specCTRL.py
wget https://github.com/strathRFM/strathRFM/raw/main/rfsoc/spectrumWidgets.py
cd other
wget https://github.com/strathRFM/strathRFM/raw/main/rfsoc/other/logo.png
wget https://github.com/strathRFM/strathRFM/raw/main/rfsoc/other/jupyter.png
cd /boot
rm boot.py
wget https://github.com/strathRFM/strathRFM/raw/main/rfsoc/other/boot.py
```
Once complete, the **specCTRL.py** can be run from the terminal as follows:
```
python /home/xilinx/jupyter_notebooks/strathRFM/specCTRL.py
```
This will initialise the strathRFM data generation algorithm on the RFSoC in idle mode. By navigating to StrathRFM (jupyter_notebooks/strathRFM) and opening the **Notebook_CTRL.ipynb** file, the spectrum can be set up and tested or dataset generation can be initialiased. Alternatively, the same can be achieved using the included GUI for data analisys and data generation. 




## windows:

download exe or compile source code in the GUI folder

### Live View RFSoC

For more immersive live spectrum analyser experience, the samba interface must be adapted to update as soon as possible. To do so the samba configuration file must be changed. This can be achieved trough the Jupyter Notebooks terminal within the JupyterLab as follows:
First lets open the samba configuration file:
```
sudo vi /etc/samba/smb.conf
```
This will open the editor now you can navigate down and under globals section and press insert which will allow the file editing, insert the following command
```
oplocks = False
```
To save the changes first press 'ESC' button and 'ZZ' shift+z twice. At this point it will exit vim and the RFSoC can be restarted using
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

## Linux: 
Please follow the instructions shown in the windows section to install required libraries on the device. Once installed, using Linux terminal navigate to the desired location and files can be downloaded using th "wget" command. Once the system is downloaded, the following command can be used.
```
cd <desired directory>

wget https://github.com/strathRFM/strathRFM/raw/main/GUI/analysis.py
wget https://github.com/strathRFM/strathRFM/raw/main/GUI/GUI_tabs.py
wget https://github.com/strathRFM/strathRFM/raw/main/GUI/readData.py
wget https://github.com/strathRFM/strathRFM/raw/main/GUI/SweepClass.py
wget https://github.com/strathRFM/strathRFM/raw/main/GUI/tkconfig.py

python <dsired directoy>/GUI.tabs.py
```



# Troubleshooting
## RFSoC
### Permissions
if permission issues are encountered change folder permissions of strathRFM using the following commands
```
cd /home/xilinx/jupyter_notebooks/
chmod -R 777 strathRFM
```
### Undefined modules
This error can occur if the working path is not automatically specified in the system paths. python code:
```
sys.path.append('/home/xilinx/jupyter_notebooks/strathRFM')
```
alternatively vim can be used from the terminal  (CHECK IF THIS CAN BE DONE)
```
sudo vi /etc/sys.path
```
and paste the path into the end of the file
```
/home/xilinx/jupyter_notebooks/strathRFM
```
By pressing ZZ the file willl be saved and exited.





## Authors:
Project group members:
[Ashleigh](https://github.com/ashleighreid),
[Eilidh](https://github.com/eilidhrh),
[Jakub](https://github.com/Shullat),
[Robert](https://github.com/Inczert) and
[Martin](https://github.com/martin-dimov).


