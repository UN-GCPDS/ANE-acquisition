

from __future__ import division
import matplotlib.animation as animation
from matplotlib.mlab import psd
import  matplotlib.pyplot as plt
import pylab as pyl
import numpy as np
import sys
from rtlsdr import RtlSdr



NFFT = 1024*4
NUM_SAMPLES_PER_SCAN = NFFT*16
NUM_BUFFERED_SWEEPS = 100
NUM_SCANS_PER_SWEEP = 1


class Waterfall(object):
    keyboard_buffer = []
    shift_key_down = False
    image_buffer = -100*np.ones((NUM_BUFFERED_SWEEPS,\
                                 NUM_SCANS_PER_SWEEP*NFFT))

    def __init__(self, sdr=None, fig=None):
        self.fig = fig if fig else pyl.figure()
        self.sdr = sdr if sdr else RtlSdr()
        self.update_count=0

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
        freq_range = (fc - rs/2)/1e6, (fc + rs*(NUM_SCANS_PER_SWEEP - 0.5))/1e6


        self.image.set_extent(freq_range + (0, 1))
        self.fig.canvas.draw_idle()

    def update(self, *args):

        self.image_buffer = np.roll(self.image_buffer, 1, axis=0)
        self.update_count+=1

        if self.update_count<=100:
            for scan_num, start_ind in enumerate(range(0, NUM_SCANS_PER_SWEEP*NFFT, NFFT)):
                # estimate PSD for one scan
                samples = self.sdr.read_samples(NUM_SAMPLES_PER_SCAN)
                
                psd_scan, f = psd(samples, NFFT=NFFT)

                self.image_buffer[0, start_ind: start_ind+NFFT] = 10*np.log10(psd_scan)

            # plot entire sweep
            self.image.set_array(self.image_buffer)

            return self.image,
        else: 
            self.fig.savefig(f'./{self.sdr.fc}frecuencia.png')


    def start(self):
        self.update_plot_labels()

        
        ani = animation.FuncAnimation(self.fig, self.update, interval=10**-2,
                blit=True)
        # ani=ani.save('./test.gif', writer='imagemagick')
        # fig.savefig('./test.png') 


        pyl.show()
        return
    
def main():
    sdr = RtlSdr()
    wf = Waterfall(sdr)

    # some defaults
    sdr.rs = 2.4e6
    sdr.fc = 90.7e6
    wf.start()

    # cleanup
    sdr.close()


if __name__ == '__main__':
    main()
