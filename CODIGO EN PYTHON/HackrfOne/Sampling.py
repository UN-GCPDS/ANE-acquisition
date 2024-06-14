import numpy as np
from hackrf import HackRF
import scipy.signal as signal
import sounddevice as sd

# Configuración de la frecuencia de muestreo y la frecuencia de la señal FM
sample_rate = 2.048e6  # 2.048 MHz
center_freq = 100.1e6  # Frecuencia central en Hz (por ejemplo, 100.1 MHz para una estación FM)

# Configuración de HackRF One
hackrf = HackRF()
hackrf.sample_rate = sample_rate
hackrf.center_freq = center_freq
hackrf.gain = 20

# Captura de muestras de la señal
def rx_callback(samples, ctx=None):
    # Convertir a numpy array
    samples = np.array(samples).astype(np.complex64)
    
    # Desplazar la señal a la banda base
    freq_trans = np.exp(-1j * 2.0 * np.pi * 250e3 / sample_rate * np.arange(len(samples)))
    baseband_signal = samples * freq_trans
    
    # Filtro paso bajo
    nyquist_rate = sample_rate / 2
    cutoff_hz = 100e3
    numtaps = 101
    fir_coeff = signal.firwin(numtaps, cutoff_hz / nyquist_rate)
    filtered_signal = signal.lfilter(fir_coeff, 1.0, baseband_signal)
    
    # Demodulación FM
    angle_diff = np.angle(filtered_signal[1:] * np.conj(filtered_signal[:-1]))
    demodulated_signal = np.concatenate(([0], angle_diff)) * (sample_rate / (2.0 * np.pi * 75e3))
    
    # Decimación para la salida de audio
    audio_signal = signal.decimate(demodulated_signal, 10)
    
    # Reproducir la señal de audio
    sd.play(audio_signal, sample_rate / 10)
    sd.wait()

hackrf.start_rx(rx_callback)

# Ejecutar captura durante 10 segundos
import time
time.sleep(10)

hackrf.stop_rx()
hackrf.close()