from pylab import *
from rtlsdr import *

# Activar modo interactivo de Matplotlib
ion()

# Inicializar el dispositivo RTL-SDR
sdr = RtlSdr()
sdr.sample_rate = 2.4e6
sdr.center_freq = 99.7e6
sdr.gain = 4

# Configurar la figura y el eje para el gráfico en vivo
fig, ax = subplots()
line, = ax.plot([], [])
ax.set_xlim(0, sdr.sample_rate / 2e6)
ax.set_ylim(-100, 10)
ax.set_xlabel('Frequency (MHz)')
ax.set_ylabel('Relative power (dB)')

# Capturar y actualizar en vivo
try:
    while True:
        samples = sdr.read_samples(256 * 1024)
        psd(samples, NFFT=1024, Fs=sdr.sample_rate / 1e6, Fc=sdr.center_freq / 1e6)
        line.set_ydata(10 * log10(psd(samples, NFFT=1024)))
        pause(0.01)  # Hacer una pausa para actualizar el gráfico
except KeyboardInterrupt:
    pass
finally:
    # Cerrar el dispositivo RTL-SDR al finalizar
    sdr.close()


