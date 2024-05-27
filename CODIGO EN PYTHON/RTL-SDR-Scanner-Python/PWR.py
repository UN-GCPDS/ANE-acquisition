import numpy as np
import matplotlib.pyplot as plt
from matplotlib.pyplot import psd
from scipy import signal as sig
from rtlsdr import RtlSdr

sdr = RtlSdr()


def tune_to_frequency(radio, true_frequency, lo_frequency):
    shifted_frequency = true_frequency + lo_frequency
    sdr.center_freq = shifted_frequency
    print(f"Tuned to {true_frequency /
                      1e6} MHz (shifted to {shifted_frequency / 1e6} MHz)")


def psd_graph(iq_samples):
    # use matplotlib to estimate and plot the PSD
    psd(iq_samples, NFFT=1024, Fs=sdr.sample_rate/1e6, Fc=freq/1e6)
    plt.ylim(-55, -10)
    plt.xlim((freq-1e6)/1e6, (freq+1e6)/1e6)
    plt.xlabel('Frequency (MHz)')
    plt.ylabel('Relative power (dB)')
    plt.show()


# configure device
sdr.sample_rate = 2.4e6  # Ancho de banda de 2 MHz
sdr.gain = 25
start = 88e6
stop = 108e6
step = 0.1e6
lo_frequency = -125e6
freq = start

frequencies = []
max_pwr_list = []
min_pwr_list = []
avg_pwr_list = []

while freq <= stop:
    print(f"Scanning frequency: {freq / 1e6} MHz")
    tune_to_frequency(sdr, freq, lo_frequency)
    iq_samples = sdr.read_samples(2**18)
    iq_samples = sig.decimate(iq_samples, 24)
    max_pwr = np.max(np.abs(iq_samples)**2)
    min_pwr = np.min(np.abs(iq_samples)**2)
    avg_pwr = np.mean(np.abs(iq_samples)**2)

    frequencies.append(freq/1e6)
    max_pwr_list.append(max_pwr)
    min_pwr_list.append(min_pwr)
    avg_pwr_list.append(avg_pwr)
    freq += step

plt.figure(figsize=(10, 6))
plt.plot(frequencies[1:], max_pwr_list[1:], marker='o', linestyle='-')
plt.xlabel('Frequency (MHz)')
plt.ylabel('Average Power (W)')
plt.title('Average Power vs Frequency')
plt.grid(True)
plt.show()

sdr.close()
