import uhd
import numpy as np
usrp = uhd.usrp.MultiUSRP("type=b200")
samples = 0.8*np.random.randn(10000) + 0.8j*np.random.randn(10000) # create random signal
duration = 5*60 # seconds
center_freq = 88.300e6
sample_rate = 200e3
gain = 60 # [dB] start low then work your way up
usrp.send_waveform(samples, duration, center_freq, sample_rate, [0], gain)
# download uhd driver