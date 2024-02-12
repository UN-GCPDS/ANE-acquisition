from pylab import *
from rtlsdr import *
import matplotlib.pyplot as plt
sdr = RtlSdr()

# configure device
sdr.sample_rate = 2.4e6
sdr.center_freq = 95e6
sdr.gain = 4

# Read samples
samples = sdr.read_samples(256*1024)


# Decimate the samples
for x in range(0,100,10):
    if x==0:
        x=1
    decimated_samples = samples[::x]
    plt.psd(decimated_samples, NFFT=1024, Fs=sdr.sample_rate/x/1e6, Fc=sdr.center_freq/1e6)
    plt.title(f"decimacion{x}")
    plt.xlabel('Frequency (MHz)')
    plt.ylabel('Relative power (dB)')
    plt.show()

sdr.close()

# psd(decimated_samples, NFFT=1024, Fs=sdr.sample_rate/x/1e6, Fc=sdr.center_freq/1e6)
# xlabel('Frequency (MHz)')
# ylabel('Relative power (dB)')
# show() 
