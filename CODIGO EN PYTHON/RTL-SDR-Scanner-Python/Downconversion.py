import numpy as np
import matplotlib.pyplot as plt
from rtlsdr import RtlSdr

# Función para obtener y calcular el PSD en una frecuencia específica


def get_psd(center_freq, sdr):
    sdr.center_freq = center_freq
    samples = sdr.read_samples(2**18)
    freqs, psd = plt.psd(samples, NFFT=1024,
                         Fs=sdr.sample_rate / 1e6, Fc=center_freq / 1e6)
    return freqs, psd


# Configuración del RTL-SDR
sdr = RtlSdr()

# Configuraciones comunes del sdr
sdr.sample_rate = 2e6  # 2.048 MS/s
sdr.gain = 'auto'

# Frecuencias de interés
freq_1 = 89.5e6
freq_2 = 90.5e6

# Obtener PSDs
freqs1, psd1 = get_psd(freq_1, sdr)
freqs2, psd2 = get_psd(freq_2, sdr)

psd1_media_dB = 10 * np.log10(np.mean(psd1))
psd2_media_dB = 10 * np.log10(np.mean(psd2))

# Cerrar el dispositivo RTL-SDR
sdr.close()

plt.gca().text(0.05, 0.95, 'PSD {:.2f} MHz: {:.2f}'.format(
    freq_1/1e6, psd1_media_dB), transform=plt.gca().transAxes)
plt.gca().text(0.05, 0.9, 'PSD {:.2f} MHz: {:.2f}'.format(
    freq_2/1e6, psd2_media_dB), transform=plt.gca().transAxes)

plt.title(f'Power Spectral Density de {freq_1/1e6} MHz y {freq_2/1e6} MHz')
plt.xlabel('Frequency (MHz)')
plt.ylabel('Power Density')
plt.grid(True)
plt.show()
