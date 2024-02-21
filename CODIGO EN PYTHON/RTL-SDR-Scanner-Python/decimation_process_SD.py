from pylab import *
from rtlsdr import *
import matplotlib.pyplot as plt
from scipy import signal as sig
import numpy as np

sdr = RtlSdr()

# configure device
sdr.sample_rate = 2.4e6
sdr.center_freq = 95e6
sdr.gain = 4

# Read samples
samples = sdr.read_samples(256*1024)

# Lista para almacenar las desviaciones estándar
std_dev_list = []

for x in range(0, 100, 10):
    if x==0:
        x=1
    decimated_samples = sig.decimate(samples, x)

    # Crear índices para la interpolación
    original_indices = np.arange(0, len(samples), 1)
    interpolation_indices = np.arange(0, len(samples), 1/x)[:len(decimated_samples)]

    # Interpolar para restaurar la frecuencia de muestreo original
    restored_samples = np.interp(original_indices, interpolation_indices, decimated_samples)

    # Calcular la desviación estándar y agregarla a la lista
    std_dev = np.std(restored_samples)
    std_dev_list.append(std_dev)

    # Visualizar el espectro de potencia de las muestras originales y restauradas
    #frequencies, original_psd = plt.psd(samples, NFFT=2048, Fs=sdr.sample_rate/1e6, Fc=sdr.center_freq/1e6)
    #restored_psd = plt.psd(restored_samples, NFFT=2048, Fs=sdr.sample_rate/1e6, Fc=sdr.center_freq/1e6)

    #plt.title(f"Decimación x{x} y Restauración con np.interp")
    #plt.xlabel('Frecuencia (MHz)')
    #plt.ylabel('Potencia Relativa (dB)')
    #plt.legend(['Original', 'Restaurada'])
    #plt.show()

# Graficar la desviación estándar en función del número de decimación
plt.plot(range(1, 100, 10), std_dev_list, marker='o')
plt.title('Desviación Estándar vs Número de Decimación')
plt.xlabel('Número de Decimación')
plt.ylabel('Desviación Estándar')
plt.show()

sdr.close()


