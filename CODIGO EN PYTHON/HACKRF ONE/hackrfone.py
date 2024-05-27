#-------------SE IMPORTAN LIBRERIAS NECESARIAS PARA EL PROCESAMIENTO DE LAS SEÑALES----------------------------#
from pyhackrf2 import HackRF
from pylab import *
import numpy as np
from scipy import signal as sig
import matplotlib.pyplot as plt

'''
Nuestra Frecuencia objetivo es 90.5 MHz. Para esto tomamos dos capturas de señal:
1.) 
Fc = 91.0 MHz
Fs = 2.0 MHz
El ancho de banda de la captura será de (90 MHz - 92 MHz)

2.) 
Fc = 90.0 MHz
Fs = 2.0 MHz
El ancho de banda de la captura será de (89 MHz - 91 MHz)

Compararemos el PSD en la superposición de los dos conjuntos (90 MHz - 91 MHz)
y verificaremos si el SDR nos da un resultado estable a pesar de que el downsampling en teoría
solo procesa la mitad de la señal.
'''
#Una funcion que va a recibir frecuencia inferior y frecuencia superior, va a recibir el samplerate y el tiempo (Cuadrar con 95 y luego probar con frecuencias mas altas)

#-----------------LLAMAMOS AL OBJETO DEL HACKRF-----------------------#
hackrf = HackRF()

#-----------------PARAMETROS CAPTURA DE LA SEÑAL----------------------#
hackrf.sample_rate = 2e6
hackrf.center_freq = 91.0e6
samples1 = hackrf.read_samples(2e6)
freq1, psd_values1 = psd(samples1, NFFT=1024, Fs=hackrf.sample_rate/1e6, Fc=hackrf.center_freq/1e6)

hackrf.close()

#-----------------CAPTURA CON DIFERENTE FRECUENCIA CENTRAL-----------------#
hackrf = HackRF()
hackrf.sample_rate = 2e6
hackrf.center_freq = 90.0e6
samples2 = hackrf.read_samples(2e6)
freq2, psd_values2 = psd(samples2, NFFT=1024, Fs=hackrf.sample_rate/1e6, Fc=hackrf.center_freq/1e6)
hackrf.close()

#-----------------CALCULAMOS LAS MEDIAS DE LOS VALORES PSD-----------------#
mean_psd1 = 10 * np.log10(np.mean(psd_values1))
mean_psd2 = 10 * np.log10(np.mean(psd_values2))

#-----------------GRAFICAMOS LA PSD DE AMBAS CAPTURAS Y SUS MEDIAS-----------------#

plt.plot(freq1/1e6 + 91.0, 10*np.log10(psd_values1), label='Frecuencia 91.0 MHz',color ="blue")
plt.plot(freq2/1e6 + 90.0, 10*np.log10(psd_values2), label='Frecuencia 90.0 MHz',color="orange")
plt.legend(loc="upper right")

plt.text(0.05, 0.95, f'Media PSD 91.0 MHz: {mean_psd1:.2f} dB/Hz', transform=plt.gca().transAxes )
plt.text(0.05, 0.9, f'Media PSD 90.0 MHz: {mean_psd2:.2f} dB/Hz', transform=plt.gca().transAxes)

plt.title('Superposición de PSDs de dos señales capturadas con HackRF')
plt.xlabel('Frequency (MHz)')
plt.ylabel('Power Spectral Density (dB/Hz)')
plt.grid(True)
plt.show()
