![screenshot](logo.png?raw=true)
## strath Radio Frequency Mapping

# Description:
strathRFM is a system that can generate datasets of the RF spectrum and map it using the easy to use GUI.

The currently supported devices are: rtl-sdr, rfsoc 2x2, rfsoc 4x2, ZC1111

bla bla bla and bla

## install
# Linux: 

copy and panste use python command

# rfsoc:

to install strathRFM you can open a new terminal in JupyterLab and paste in the following commands and hit enter

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
doing so the rfsoc will create the necessary folders and download the files from github. Once complete, you can navigate to StrathRFM and run the Provided notebook 
or alternatively use the provided GUI to control strathRFM.





# windows:

download exe or compile source code in the GUI folder

# RTL-SDR:

To use the RTL-SDR in Python the following library is needed: pyrtlsdr. The library can be installed using the following pip command:

**pip install pyrtlsdr**

Once downloaded the python package requires some dependices called librtlsdr, to work correctly. The package can be accessed from here https://github.com/librtlsdr/librtlsdr/releases. 
We used **rtlsdr-bin-w64_dlldep.zip** package.

![image](https://user-images.githubusercontent.com/99476167/229078556-f01f6f8b-6f58-440d-9356-2a92506e1988.png)

Extract the zip and save it within a working directory. We commonly used our C drive. The next step is to find the Python program files within your computer system. The file location can be found by using the following file path:

**C:\Users\44750\AppData\Local\Programs\Python\Python39\Lib\site-packages\rtlsdr**

Locate the file 'librtlsdr.py' and modify as shown below:

![image](https://user-images.githubusercontent.com/99476167/229480270-fe2a1ea1-52e6-4349-bbe3-5dd770f18e2a.png)

Save the file and run a basic script with the RTL-SDR to check the driver was installed correctly.
