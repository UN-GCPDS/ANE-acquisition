

from __future__ import division
import matplotlib.animation as animation
from matplotlib.mlab import psd
import  matplotlib.pyplot as plt
# import pylab as pyl
import numpy as np
import sys
from rtlsdr import RtlSdr
import time
'''
Estas son las variables iniciales

NFFT -->Numero de Muestras
NUM_SAMPLES_PER_SCAN -->Numero de Muestras por escaneo 


'''
NFFT = 1024*8
NUM_SAMPLES_PER_SCAN = NFFT*16
NUM_BUFFERED_SWEEPS = 10



class Waterfall(object):
    #Creamos el plano en el cual plotearemos el waterfall
    image_buffer = -100*np.ones((NUM_BUFFERED_SWEEPS,NFFT))


    def __init__(self, sdr=None, fig=None):
        self.fig = fig if fig else plt.figure()
        self.sdr = sdr if sdr else RtlSdr()
        self.init_plot()

    def init_plot(self):
        self.ax = self.fig.add_subplot(1,1,1)
        self.image = self.ax.imshow(self.image_buffer, aspect='auto',\
                                    interpolation='nearest', vmin=-60, vmax=10)
        self.ax.set_xlabel('Current frequency (MHz)')
        self.ax.get_yaxis().set_visible(False)

    def update_plot_labels(self):
        fc = self.sdr.fc
        rs = self.sdr.rs
        freq_range = (fc - rs/2)/1e6, (fc + rs*(1 - 0.5))/1e6


        self.image.set_extent(freq_range + (0, 1))
        self.fig.canvas.draw_idle()




    def showing_current_station(self):
        self.update_plot_labels()
        tiempo= time.time()
        for frame in range(self.image_buffer.shape[0]):
            self.image_buffer = np.roll(self.image_buffer, 1, axis=0)
            samples = self.sdr.read_samples(NUM_SAMPLES_PER_SCAN)
                    
            psd_scan, f = psd(samples, NFFT=NFFT)

            self.image_buffer[0,0:NFFT] = 10*np.log10(psd_scan)

                # plot entire sweep
            self.image.set_array(self.image_buffer)

        print(f"tiempo que se demora el codigo {time.time()-tiempo}")
        plt.title(f"Espectrograma en la frecuencia {self.sdr.fc/1e6}")
        plt.savefig(f'my_plot{self.sdr.fc/1e6}.png')
        plt.show()
        return self.image
    
def main():
    sdr = RtlSdr()
    wf = Waterfall(sdr)

    wf.showing_current_station()

    # cleanup
    sdr.close()


if __name__ == '__main__':
    main()
