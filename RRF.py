import matplotlib.pyplot as plt
from rtlsdr import RtlSdr
from scipy import signal
from time import sleep
import numpy as np
from scipy.io import wavfile
import sounddevice
 
sdr = RtlSdr()
 
# configure device
Freq = 95.1e6 #mhz
Fs = 1140000
F_offset = 250000
Fc = Freq - F_offset
sdr.sample_rate = Fs
sdr.center_freq = Fc
sdr.gain = 'auto'
samples = sdr.read_samples(8192000)
print(samples)
print(samples.shape)
print(np.max(samples))
#continue
#sdr.close()
figure = plt.figure(figsize=(30,10))
rows = 2
cols = 2
 
x1 = np.array(samples).astype("complex64")
fc1 = np.exp(-1.0j*2.0*np.pi* F_offset/Fs*np.arange(len(x1))) 
x2 = x1 * fc1
ax1 = figure.add_subplot(rows,cols,1)
ax1.specgram(x2, NFFT=2048, Fs=Fs)  
ax1.set_title("x2")  
ax1.set_xlabel("Time (s)")  
ax1.set_ylabel("Frequency (Hz)")  
ax1.set_ylim(-Fs/2, Fs/2)  
ax1.set_xlim(0,len(x2)/Fs)  
ax1.ticklabel_format(style='plain', axis='y' )  
 
bandwidth = 200000#khz broadcast radio.
n_taps = 64
# Use Remez algorithm to design filter coefficients
lpf = signal.remez(n_taps, [0, bandwidth, bandwidth+(Fs/2-bandwidth)/4, Fs/2], [1,0], Hz=Fs)  
x3 = signal.lfilter(lpf, 1.0, x2)
dec_rate = int(Fs / bandwidth)
x4 = x3[0::dec_rate]
Fs_y = Fs/dec_rate
f_bw = 200000 
dec_rate = int(Fs / f_bw)  
x4 = signal.decimate(x2, dec_rate) 
# Calculate the new sampling rate
# Fs_y = Fs/dec_rate  
ax2 = figure.add_subplot(rows,cols,2)
ax2.scatter(np.real(x4[0:50000]), np.imag(x4[0:50000]), color="red", alpha=0.05)  
ax2.set_title("x4")  
ax2.set_xlabel("Real")
ax2.set_xlim(-1.1,1.1)  
ax2.set_ylabel("Imag")  
ax2.set_ylim(-1.1,1.1)   
 
y5 = x4[1:] * np.conj(x4[:-1])
x5 = np.angle(y5)
ax3  = figure.add_subplot(rows,cols,3)
ax3.psd(x5, NFFT=2048, Fs=Fs_y, color="blue")  
ax3.set_title("x5")  
ax3.axvspan(0,             15000,         color="red", alpha=0.2)  
ax3.axvspan(19000-500,     19000+500,     color="green", alpha=0.4)  
ax3.axvspan(19000*2-15000, 19000*2+15000, color="orange", alpha=0.2)  
ax3.axvspan(19000*3-1500,  19000*3+1500,  color="blue", alpha=0.2)  
ax3.ticklabel_format(style='plain', axis='y' )  
plt.show()
 
 
# The de-emphasis filter
# Given a signal 'x5' (in a numpy array) with sampling rate Fs_y
d = Fs_y * 75e-6   # Calculate the # of samples to hit the -3dB point  
x = np.exp(-1/d)   # Calculate the decay between each sample  
b = [1-x]          # Create the filter coefficients  
a = [1,-x]  
x6 = signal.lfilter(b,a,x5)  
audio_freq = 48100.0 
dec_audio = int(Fs_y/audio_freq)  
Fs_audio = Fs_y / dec_audio
x7 = signal.decimate(x6, dec_audio) 
 
sounddevice.play(x7,Fs_audio) 
x7 *= 10000 / np.max(np.abs(x7))  
 
#sounddevice.play(x7,Fs_audio)
x7.astype("int16").tofile("wbfm-mono.raw")  #Raw file.
wavfile.write('wav.wav',int(Fs_audio), x7.astype("int16"))
print('playing...')
sounddevice.play(x7.astype("int16"),Fs_audio,blocking=True)