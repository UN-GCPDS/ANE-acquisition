import numpy as np
from pyhackrf2 import HackRF
import time
from gnuradio import analog
import matplotlib.pyplot as plt

# Datos de ejemplo: una señal senoidal modulada en frecuencia
sample_rate = 20e6
center_freq = 90e6
duration = 0.001  # Duración de la transmisión en segundos
t = np.arange(0, duration, 1/sample_rate)

signal = np.exp(1j * 2.0 * np.pi * 2e3 * t)  # Señal de prueba: tono a 1 kHz

demod = signal.real*np.cos(2*np.pi*2e3*t)+signal.imag*np.sin(2*np.pi*2e3*t)

plt.psd(signal, 1024, 4e3, 0)
plt.psd(demod, 1024, 4e3, 0)
plt.title('Espectros')
plt.show()
plt.plot(demod)
plt.title('Demodulada')
plt.show()

# Convertir la señal a bytes
signal_bytes = signal.astype(np.complex64).tobytes()

# Crear el objeto HackRF
hackrf = HackRF()
hackrf.sample_rate = sample_rate
hackrf.center_freq = center_freq
hackrf.txvga_gain = 20  # Ganancia de transmisión (ajustable)

# Establecer el buffer con la señal
#hackrf.buffer = samples

# Iniciar la transmisión
# hackrf.start_tx()
# time.sleep(duration+1)

# # # Detener la transmisión
# hackrf.stop_tx()









