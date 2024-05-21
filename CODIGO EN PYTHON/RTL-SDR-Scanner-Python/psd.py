import rtlsdr
from matplotlib import pyplot as plt
from pylab import *
from rtlsdr import *
from hackrf import *


sdr = RtlSdr()

# configure device
sdr.sample_rate = 1e6
sdr.center_freq = 88.3e6
sdr.gain = 4

samples = sdr.read_samples(256*1024)
sdr.close()
#----------------------CALCULATING THE POWER OF THE SIGNAL ------------------#
#----------------------FUNCTION TO CALCULATE THE PWR FOR A SIGNAL FROM THE RTL-SDR----------------------#

def pwr_rtlsdr(x):
    '''
    This function calculate the PWR
    Input: x --> array numpy with iQ samples

    Output: avg_pwr --> average pwr of the signal
            max_pwr --> max pwr of the signal
            min_pwr --> min pwr of the signal
    
    '''
    avg_pwr = np.mean(np.abs(array)**2)
    max_pwr=max(abs(array**2))
    min_pwr=min(abs(array**2))
    return avg_pwr,max_pwr,min_pwr

hrf = HackRF()
hrf.sample_rate = 20e6
hrf.center_freq = 88.5e6
samples = hrf.read_samples(2e6)