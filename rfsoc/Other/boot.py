#! /usr/bin/env python3

# example #1 - WiFi connection at boot
#from pynq.lib import Wifi
#
#port = Wifi()
#port.connect('your_ssid', 'your_password', auto=True)

# example #2 - Change hostname
#import subprocess
#subprocess.call('pynq_hostname.sh aNewHostName'.split())

# example #3 - blink LEDs (PYNQ-Z1, PYNQ-Z2, ZCU104)
#from pynq import Overlay
#from time import sleep
#
#ol = Overlay('base.bit')
#leds = ol.leds
#
#for _ in range(8):
#    leds[0:4].off()
#    sleep(0.2)
#    leds[0:4].on()
#    sleep(0.2)

#! /usr/bin/env python3.6
#   Copyright (c) 2021, Xilinx, Inc.
#   All rights reserved.
# 
#   Redistribution and use in source and binary forms, with or without 
#   modification, are permitted provided that the following conditions are met:
#
#   1.  Redistributions of source code must retain the above copyright notice, 
#       this list of conditions and the following disclaimer.
#
#   2.  Redistributions in binary form must reproduce the above copyright 
#       notice, this list of conditions and the following disclaimer in the 
#       documentation and/or other materials provided with the distribution.
#
#   3.  Neither the name of the copyright holder nor the names of its 
#       contributors may be used to endorse or promote products derived from 
#       this software without specific prior written permission.
#
#   THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
#   AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, 
#   THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR 
#   PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR 
#   CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, 
#   EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, 
#   PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS;
#   OR BUSINESS INTERRUPTION). HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, 
#   WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR 
#   OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF 
#   ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.


from time import sleep
from pynq.overlays.base import BaseOverlay
import pickle
import subprocess


specCTRL_path = '/home/xilinx/jupyter_notebooks/strathRFM/specCTRL.py'
config_path = '/home/xilinx/jupyter_notebooks/strathRFM/config.pkl'


def unpickleFile():
    idx = 0
    res = False
    while(res == False):
        try:
            with open(config_path, 'rb') as fo:
                dict = pickle.load(fo, encoding='bytes')
                res = True
        except:
            idx += 1
            if(idx >10):
                break
            sleep(0.001)
            dict = {}
            res =  False
    return res, dict

def pickleFile(data):
    idx = 0
    res = False
    while(res == False):
        try:
            pickle.dump(data, open(config_path, 'wb'))
            res = True
        except:
            idx += 1
            if(idx >10):
                break
            sleep(0.001)
            res = False
    return res

def blink8():
    for _ in range(8):
        base.leds[0:4].off()
        sleep(0.2)
        base.leds[0:4].on()
        sleep(0.2)
        
def blink8_alt():
    base.leds[0:4].off()
    for _ in range(4):
        sleep(0.2)
        for _ in range(2):
            base.leds[0:4].on()
            sleep(0.1)
            base.leds[0:4].off()
            sleep(0.1)

def walk8():
    base.leds[0:4].off()
    for _ in range(4):
        for i in range(0,4):
            base.leds[i].on()
            sleep(0.1)
            base.leds[i].off()
        
###############################################################################
#                               Boot Proces                                   #
###############################################################################     

base = BaseOverlay('base.bit')

base.init_gpio()
base.init_dp()
base.init_rf_clks()    

    
base.leds[0].on()
sleep(0.5)
res, f = unpickleFile()
f[b'status'] = "Booting RFSoC..."
pickleFile(f)

base.leds[1].on()
sleep(0.5)
if res:
    base.leds[2].on()
    sleep(0.5)
    if f[b'start_on_boot']:
        f[b'status'] = "Initialising specCTRL..."
        pickleFile(f)
        base.leds[3].on()
        sleep(0.5)
        walk8()
        if f[b'continuous_scan_enable']:
            f[b'status'] = "continuous scan..."
        else:
            f[b'status'] = "idle mode..."
        pickleFile(f)
        base.leds[0:4].off()
        # initialise specCTRL
        try:
            process = subprocess.Popen(['python', '/home/xilinx/jupyter_notebooks/strathRFM/specCTRL.py'], stdout=subprocess.PIPE, universal_newlines=True)
            with open('/home/xilinx/jupyter_notebooks/strathRFM/log.txt', 'w') as fil:
                while True:
                    output = process.stdout.readline()
                    fil.write(str(output.strip())+"\n")
                    # Do something else
                    return_code = process.poll()
                    if return_code is not None:
                        fil.write(str('RETURN CODE', return_code))
                        # Process has finished, read rest of the output
                        for output in process.stdout.readlines():
                            fil.write(str(output.strip())+"\n")
                        break
        #os.system('cd /home/xilinx/jupyter_notebooks/strathRFM/')
        #os.system('sudo python /home/xilinx/jupyter_notebooks/strathRFM/specCTRL.py')
        except:
            f[b'status'] = "specCTRL execution failed."

        pickleFile(f)
        # reconfiguring overlay
        base = BaseOverlay('base.bit')
        base.init_gpio()
        base.init_dp()
        base.init_rf_clks()
    else:
        blink8()
else:
    blink8_alt()
blink8()
base.leds[0:4].on()

#exec(open('/home/xilinx/jupyter_notebooks/spectrum.py').read())
