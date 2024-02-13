from pylab import *
from rtlsdr import *
import matplotlib.pyplot as plt

sdr = RtlSdr()

# configure device
sdr.sample_rate = 2.4e6
sdr.center_freq = 95e6
sdr.gain = 4

# Read samples
samples = sdr.read_samples(256 * 1024)

# Lista para almacenar las desviaciones estándar
std_dev_list = []

# Decimate the samples and calculate standard deviation
for x in range(1, 1000, 2):
    if x == 0:
        x = 1
    decimated_samples = samples[::x]
    
    # Calcular la desviación estándar y agregarla a la lista
    std_dev = np.std(decimated_samples)
    std_dev_list.append(std_dev)

    #plt.psd(decimated_samples, NFFT=1024, Fs=sdr.sample_rate/1e6, Fc=sdr.center_freq/1e6)
    #plt.title(f"Decimación {x}")
    #plt.xlabel('Frequency (MHz)')
    #plt.ylabel('Relative power (dB)')
    #mmjjplt.show()

# Graficar la desviación estándar en función del número de decimación
plt.plot(range(1, 1000, 2), std_dev_list, marker='o')
plt.title('Desviación Estándar vs Número de Decimación')
plt.xlabel('Número de Decimación')
plt.ylabel('Desviación Estándar')
plt.show()

sdr.close()