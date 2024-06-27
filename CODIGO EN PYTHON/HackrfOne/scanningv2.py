import time
import numpy as np
import matplotlib.pyplot as plt
from pyhackrf2 import HackRF
from scipy import signal as sig
from gcpds.filters import frequency as flt
from scipy.integrate import simps

class scanning():
    def __init__(self, device=HackRF(), bandwidth=20e6, samples_limit=5e5, vga_gain=16, lna_gain=0, amp_status=False):
        self.hackrf = device
        self.hackrf.filter_bandwidth = bandwidth
        self.hackrf.sample_count_limit = samples_limit
        self.hackrf.vga_gain = vga_gain     # Baseband gain
        self.hackrf.lna_gain = lna_gain     # IF gain
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

        return i, q
    
    i_samples_list = []
    q_samples_list = []
    
    def wide_scan(self, start=88e6, stops=108e6, sample_rate=20e6, duration=0.1):
        self.start = start
        self.stops = stops
        self.sample_rate = sample_rate
        self.duration = duration
        self.freq = start
        
        
        while self.freq < self.stops:
            print(f"Scanning frequency: {(self.freq + self.sample_rate/2) / 1e6} MHz con un sample rate de: {self.sample_rate/1e6}M")
            i, q = self.scan(self.freq, self.freq+self.sample_rate, self.sample_rate, self.duration)

            self.freq += self.sample_rate
        
        return i, q
    
    def decimate(self, i, q, decimate):
        i = np.array(i)
        q = np.array(q)

        i = i[::decimate]
        q = q[::decimate]
        
        iq_samples = i + 1j*q

        return i, q, iq_samples
    
    def power(self, iq_samples, interest_freq):
        psd, f = plt.psd(iq_samples, NFFT=2024, Fs=hackrf.sample_rate/1e6, Fc=(hackrf.start + hackrf.stop) / 2 / 1e6)
        plt.show()

        psd_linear = 10**(psd/10) 
        
        # Frecuencias de interés (en MHz)
        f_low = interest_freq-0.15
        f_high = interest_freq+0.15

        # Filtrar los índices de las frecuencias dentro del rango de interés
        indices = np.where((f >= f_low) & (f <= f_high))

        # Extraer las frecuencias y la PSD en ese rango
        f_range = f[indices]
        psd_range_linear = psd_linear[indices]

        # Integrar la PSD sobre el rango de frecuencias para obtener la potencia total en el rango
        # La función simps realiza la integración numérica usando el método de Simpson
        power = simps(psd_range_linear)

        print(f'La potencia en el rango de {f_low} MHz a {f_high} MHz es {power/1e3:.2f}mW')

        return power
        
    
    def concat(self, i_samples, q_samples):
        i_samples = np.array(i_samples).flatten()
        q_samples = np.array(q_samples).flatten()
        
        return i_samples, q_samples


hackrf = scanning()

i, q = hackrf.scan(start=88e6, stop=108e6, sample_rate=20e6, duration=1)

#i = np.array(i).flatten()
#q = np.array(q).flatten()

plt.psd(i + 1j*q, 1024, hackrf.sample_rate/1e6, (hackrf.start+hackrf.stop)/2/1e6)
#plt.ylim(-90, -20)
plt.show()

#hackrf.power(iq_samples, interest_freq=105.7)




