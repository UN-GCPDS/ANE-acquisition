import time
import numpy as np
import matplotlib.pyplot as plt
from hackrf import HackRF
from scipy import signal as sig
import matplotlib.mlab as mlab
import scipy.integrate as integrate

class Scanner:
    def __init__(self, start=88e6, stop=108e6, sample_rate=4e6, duration=10, num_rep=1):
        self.start = start
        self.stop = stop
        self.sample_rate = sample_rate
        self.duration = duration
        self.num_rep = num_rep


        num_freqs = int((self.stop - self.start) / self.sample_rate) + 1
        time_per_freq = (self.duration) / num_freqs

        self.freq_vec = np.linspace(start, stop, num_freqs-1)
        self.samples_per_freq = int(self.sample_rate * time_per_freq)

        self.all_freqs = []
        self.all_pwr = []
        self.all_psd = []
        

    def scan(self):
        hackrf = HackRF()
        hackrf.gain = 24
        hackrf.sample_rate = self.sample_rate
        
        freq = self.start + self.sample_rate / 2

        print(f'Number of samples: {self.samples_per_freq}')

        t1 = time.time()
        
        for i in range(self.num_rep):
            while freq <= self.stop:
                print(f"Scanning frequency: {freq / 1e6} MHz")
                hackrf.center_freq = freq
                iq_samples = hackrf.read_samples(self.samples_per_freq)
                iq_samples = iq_samples - np.mean(iq_samples)

                b, a = sig.butter(4, 1000, 'high', fs=self.sample_rate)
                iq_samples = sig.filtfilt(b, a, iq_samples)

                avg_pwr = np.mean(np.abs(iq_samples)**2)

                psd, freqs = plt.psd(iq_samples, NFFT=1024, Fs=self.sample_rate / 1e6, Fc=hackrf.center_freq/1e6)
                plt.close()

                self.all_freqs.extend(freqs)  # Ajuste de frecuencia
                self.all_pwr.append(avg_pwr)
                self.all_psd.extend(psd)

                freq += self.sample_rate

        hackrf.close()

        print(f'El tiempo de escaneo fue: {time.time()-t1}')

    def plot_psd(self):
        plt.figure(figsize=(10, 6))
        plt.plot(self.all_freqs, 10*np.log10(self.all_psd))
        plt.ylabel('PWR (dB)')
        plt.xlabel('Freq (MHz)')
        plt.title('Power Spectral Density')
        plt.grid(True)
        plt.show()

    def plot_pwr(self):
        print(self.all_pwr)
        plt.figure(figsize=(10, 6))
        plt.plot(self.freq_vec, self.all_pwr)
        plt.xlabel('Frequency (MHz)')
        plt.ylabel('Average Power (W)')
        plt.title('Average Power vs Frequency')
        plt.grid(True)
        plt.show()

    def plt_Efield(self):
        efield = np.sqrt(self.all_pwr)
        print(efield)
        plt.figure(figsize=(10, 6))
        plt.plot(self.freq_vec, efield)
        plt.xlabel('Frequency (MHz)')
        plt.ylabel('Average E field (V/m) ')
        plt.title('Average E field vs Frequency')
        plt.grid(True)
        plt.show()

hackrf = Scanner()

hackrf.scan()
hackrf.plot_psd()
hackrf.plot_pwr()
hackrf.plt_Efield()