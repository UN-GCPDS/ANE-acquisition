import time
import numpy as np
import matplotlib.pyplot as plt
from hackrf import HackRF
from scipy import signal as sig
from gcpds.filters import frequency as flt

class scanning():
    def __init__(self, device=HackRF(), bandwidth=20e6, samples_limit=5e5, vga_gain=16, lna_gain=16, amp_status=False):
        self.hackrf = device
        self.hackrf.filter_bandwidth = bandwidth
        self.hackrf.sample_count_limit = samples_limit
        self.hackrf.vga_gain = vga_gain
        self.hackrf.lna_gain = lna_gain
        self.hackrf.amplifier_on = amp_status

    def scan(self, start=88e6, stop=108e6, sample_rate=20e6, duration=0.1):
        self.start = start
        self.stop = stop
        self.sample_rate = sample_rate
        self.duration = duration

        if (stop - start) > sample_rate:
            raise ValueError("El rango de frecuencias no se puede manejar Sen un solo ensamblaje con la tasa de muestreo proporcionada.")

        self.hackrf.sample_rate = self.sample_rate
        self.hackrf.center_freq = (self.start + self.stop) / 2
        
        num_samples = int(self.sample_rate * self.duration)
        
        iq_samples = self.hackrf.read_samples(num_samples) #Aquí se genera el error
        
        high100 = flt.GenericButterHighPass(f0=0.01, N=1)
        iq_samples = high100(iq_samples, fs=250)
        
        i, q = np.real(iq_samples), np.imag(iq_samples)

        return i, q, iq_samples
    
    def wide_scan(self, start=88e6, stops=108e6, sample_rate=20e6, duration=0.1):
        self.start = start
        self.stops = stops
        self.sample_rate = sample_rate
        self.duration = duration
        self.freq = start
        i_samples_list = []
        q_samples_list = []
        
        while self.freq < self.stops:
            print(f"Scanning frequency: {(self.freq + self.sample_rate/2) / 1e6} MHz con un sample rate de: {self.sample_rate/1e6}M")
            i, q, iq_samples = self.scan(self.freq, self.freq+self.sample_rate, self.sample_rate, self.duration)
            i_samples_list.append(i)
            q_samples_list.append(q)

            plt.psd(iq_samples, 2048, self.sample_rate/1e6, self.freq/1e6+self.sample_rate/2/1e6)
            plt.show()

            self.freq += self.sample_rate
        
        return i_samples_list, q_samples_list
    
    # def concat(self, i_samples, q_samples):
    #     i_samples = np.array(i_samples).flatten()
    #     q_samples = np.array(q_samples).flatten()
        
    #     return i_samples, q_samples


hackrf = scanning()

# i1, q1, iq_samples1 = hackrf.scan(88e6, 108e6, 20e6)
# i2, q2, iq_samples2 = hackrf.scan(89e6, 109e6, 20e6)

# plt.figure(figsize=(10, 5))
# plt.subplot(2, 1, 1) 
# plt.psd(iq_samples1, 1024, hackrf.sample_rate/1e6, 98)
# plt.subplot(2, 1, 2)
# plt.psd(iq_samples2, 1024, hackrf.sample_rate/1e6, 99)
# plt.grid(True)
# plt.show()

# i, q, iq_samples = hackrf.scan(98e6,108e6, 10e6)

# plt.psd(iq_samples, 1024, hackrf.sample_rate/1e6, (hackrf.start/1e6 + hackrf.stop/1e6) / 2)
# plt.grid(True)
# plt.show()

i_samples_list, q_samples_list = hackrf.wide_scan(start=88e6, stops=108e6, sample_rate=20e6, duration=0.1)

#i_samples, q_samples = hackrf.concat(i_samples_list, q_samples_list)

#psd, freq  = plt.psd(i_samples + 1j*q_samples, 1024, 10, 98)
# plt.close()
# plt.plot(freq, 10*np.log10(psd))
# plt.grid(True)
# plt.show()




