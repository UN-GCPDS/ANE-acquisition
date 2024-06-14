import time
import numpy as np
import matplotlib.pyplot as plt
from hackrf import HackRF
from scipy import signal as sig
from matplotlib.mlab import psd

class Scanner:
    def __init__(self, start=88e6, stop=108e6, sample_rate=1e6, duration=5, num_rep=3):
        self.start = start
        self.stop = stop
        self.sample_rate = sample_rate
        self.duration = duration
        self.num_rep = num_rep


        num_freqs = int((self.stop - self.start) / self.sample_rate) + 1
        time_per_freq = (self.duration) / num_freqs

        self.samples_per_freq = int(self.sample_rate * time_per_freq)

        self.all_freqs = []
        self.all_psd = []

    def scan(self):
        hackrf = HackRF()
        hackrf.gain = '24'
        hackrf.sample_rate = self.sample_rate
        
        freq = self.start + self.sample_rate / 2

        t1 = time.time()
        
        for i in range(self.num_rep):
            while freq <= self.stop:
                print(f"Scanning frequency: {freq / 1e6} MHz")
                hackrf.center_freq = freq
                iq_samples = hackrf.read_samples(self.samples_per_freq)

                b, a = sig.butter(4, 1000, 'highpass', fs=self.sample_rate)
                iq_samples = sig.filtfilt(b, a, iq_samples)

                freqs, psd = plt.psd(iq_samples, NFFT=1024, Fs=self.sample_rate / 1e6, Fc=hackrf.center_freq / 1e6)

                self.all_freqs.extend(freqs + (freq - self.sample_rate / 2) / 1e6)  # Ajuste de frecuencia
                self.all_psd.extend(psd)

                freq += self.sample_rate

        hackrf.close()

        print(f'El tiempo de escaneo fue: {time.time()-t1}')

    def plot_psd(self):
        plt.figure(figsize=(10, 6))
        plt.plot(self.all_freqs, self.all_psd)
        plt.ylabel('PWR (dB)')
        plt.xlabel('Freq (MHz)')
        plt.title('Power Spectral Density')
        plt.grid(True)
        plt.show()

hackrf = Scanner()

hackrf.scan()
hackrf.plot_psd()

