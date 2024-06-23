import matplotlib.pyplot as plt
import scipy.signal as signal
import numpy as np
from hackrf import HackRF
from gcpds.filters import frequency as flt
from scipy.io.wavfile import write

# Inicializa el dispositivo HackRF
hackrf = HackRF()

# Configuración de parámetros del HackRF
hack_sample_rate = 2.4e6  # Tasa de muestreo en Hz
hack_center_freq = 105.7e6  # Frecuencia central en Hz

# Asigna la frecuencia central y la tasa de muestreo al HackRF
hackrf.center_freq = hack_center_freq
hackrf.sample_rate = hack_sample_rate

# Lee 9.6 millones de muestras de la señal desde el HackRF
samples_hack = hackrf.read_samples(9.6e6)

# Aplica un filtro paso alto de Butterworth para eliminar bajas frecuencias
high100 = flt.GenericButterHighPass(f0=0.01, N=1)
samples_hack = high100(samples_hack, fs=250)
samples_hack = samples_hack - np.mean(samples_hack)  # Elimina la componente DC

# Función para decimar una señal
def downsample(x, M, p=0):  
    if not isinstance(M, int):
        raise TypeError("M must be an int")
    x = x[0:int(np.floor(len(x) / M)) * M]  # Ajusta la longitud de la señal
    x = x.reshape((int(np.floor(len(x) / M)), M))  # Reorganiza la señal en segmentos
    y = x[:, p]  # Selecciona el p-ésimo elemento de cada segmento
    return y

# Función para discriminar FM
def fm_discrim(x):
    X = np.real(x)  # Parte real de la señal
    Y = np.imag(x)  # Parte imaginaria de la señal
    b = np.array([1, -1])
    dY = signal.lfilter(b, 1, Y)  # Derivada de la parte imaginaria
    dX = signal.lfilter(b, 1, X)  # Derivada de la parte real
    discriminated = (X * dY - Y * dX) / (X**2 + Y**2 + 1e-10)  # Cálculo del discriminador de frecuencia
    return discriminated

# Función principal para procesar la señal FM y extraer el audio
def fm_audio(samples, fs=2.4e6, fc=105.7e6, fc1=200e3, fc2=12e3, d1=10, d2=5, plot=False):
    lpf_b1 = signal.firwin(64, fc1 / (float(fs) / 2))  # Filtro paso bajo
    lpf_b2 = signal.firwin(64, fc2 / (float(fs) / d1 / 2))  # Segundo filtro paso bajo
    
    # Primer filtrado y decimación
    samples_filtered_1 = signal.lfilter(lpf_b1, 1, samples)
    samples_decimated_1 = downsample(samples_filtered_1, d1)
    
    # Discriminación de fase
    samples_discriminated = fm_discrim(samples_decimated_1)
    
    # Segundo filtrado y decimación
    samples_filtered_2 = signal.lfilter(lpf_b2, 1, samples_discriminated)
    audio = downsample(samples_filtered_2, d2)
    
    # Si se solicita, grafica los pasos intermedios
    if plot:
        fig, ((ax0, ax1, ax2), (ax3, ax4, ax5)) = plt.subplots(2, 3, figsize=(15, 10))

        ax0.psd(samples, NFFT=1024, Fs=fs/1e6, Fc=fc/1e6)
        ax0.set_title("samples")
        ax0.set_xlabel('Frequency (MHz)')
        ax0.set_ylabel('Relative power (dB)')
        
        ax1.psd(samples_filtered_1, NFFT=1024, Fs=fs/1e6, Fc=fc/1e6)
        ax1.set_title("samples_filtered_1")
        ax1.set_xlabel('Frequency (MHz)')
        ax1.set_ylabel('Relative power (dB)')

        ax2.psd(samples_decimated_1, NFFT=1024, Fs=fs/d1/1e6, Fc=fc/1e6)
        ax2.title.set_text('samples_decimated_1')
        ax1.set_xlabel('Frequency (MHz)')
        ax1.set_ylabel('Relative power (dB)')

        ax3.psd(samples_discriminated, NFFT=1024, Fs=fs/d1, Fc=0)
        ax3.title.set_text('samples_discriminated')

        ax4.psd(samples_filtered_2, NFFT=1024, Fs=fs/d1, Fc=0)
        ax4.title.set_text('samples_filtered_2')
        
        ax5.psd(audio, NFFT=1024, Fs=fs/d1/d2, Fc=0)
        ax5.title.set_text('audio')

        plt.show()
        
        return audio, fig, (ax0, ax1, ax2, ax3, ax4, ax5)
    else:
        return audio

# Procesa la señal capturada para extraer el audio
audio_hack = fm_audio(samples_hack, hack_sample_rate, hack_center_freq, plot=False)

# Ajuste y normalización del audio
audio_hack = np.array(audio_hack)
audio_hack = audio_hack[400:]  # Remueve las primeras 400 muestras para evitar transitorios
audio_hack = 2 * ((audio_hack - np.min(audio_hack)) / (np.max(audio_hack) - np.min(audio_hack))) - 1  # Normaliza el audio entre -1 y 1

# Grafica la señal de audio
plt.plot(audio_hack)
plt.grid(True)
plt.show()

# Guarda el audio procesado en un archivo WAV
write('output_audio.wav', 48000, audio_hack.astype(np.float32))
