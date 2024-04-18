import rtlsdr
from matplotlib import pyplot as plt
from pylab import *
from rtlsdr import *
from hackrf import *


#----------------------CALCULATING THE POWER OF THE SIGNAL ------------------#
#----------------------FUNCTION TO CALCULATE THE PWR FOR A SIGNAL FROM THE RTL-SDR----------------------#

def PWR_SDR(x):
    '''
    This function calculate the PWR
    Input: x --> array numpy with iQ samples

    Output: avg_pwr --> average pwr of the signal
            max_pwr --> max pwr of the signal
            min_pwr --> min pwr of the signal
    
    '''
    avg_pwr = np.mean(np.abs(x)**2)
    max_pwr=max(abs(x**2))
    min_pwr=min(abs(x**2))
    return avg_pwr,max_pwr,min_pwr

hrf = HackRF()
hrf.sample_rate = 20e6
hrf.center_freq = 88.5e6
samples = hrf.read_samples(2e6)
print(PWR_SDR(samples))