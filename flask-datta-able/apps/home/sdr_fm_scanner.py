import sys
import time
import argparse
import numpy as np
import os
import json
import matplotlib.pyplot as plt
from rtlsdr import RtlSdr
from scipy import signal as sig
from matplotlib.mlab import psd
from pathlib import Path
import pandas as pd
import multiprocessing
import threading
from apps.home.funciones import find_highest_magnitudes,find_relative_frequency,tune_to_frequency,station_verification
from apps.home.water_fall_class import Waterfall

'''
num_samples = Number of samples to read from the RTL-SDR device 
sample_rate = Rate which is reading a sample 
time_duration = This is the time duration of the captured signal is determined by the number of samples and the sample rate , is calculated by num_samples / sample_rate

'''
num_samples = 131072
sample_rate = 2.4e6  
time_duration = num_samples / sample_rate 


def read_samples(sdr, freq):
    f_offset = 25000
    sample_rate = 2400000
    sdr.center_freq = freq - f_offset
    time.sleep(0.01) # originally, 0.06, but too slow
    iq_samples = sdr.read_samples(2**15) #originally 1221376, but too slow, the lower this is though the lower the PSD integrity is...btw must be powers of 2...
    iq_samples = iq_samples[0:600000]
    fc1 = np.exp(-1.0j * 2.0 * np.pi * f_offset / sample_rate * np.arange(len(iq_samples)))
    iq_samples = iq_samples * fc1
    return iq_samples

def psd_scanning(sdr,freq,freq_stop,freq_step,lo_frequency,radio_psd_threshold,threshold):
    '''Este metodo realiza un escaneo  '''
    radio_stations = []
    threshold=threshold*10**-6
    
    for i in range(freq,freq_stop,freq_step):
        print(f"Scanning frequency: {freq / 1e6} MHz")
        # tune_to_frequency(sdr, freq, lo_frequency)
        iq_samples =read_samples(sdr, freq)
        iq_samples = sig.decimate(iq_samples, 24)
        f, psd = sig.welch(iq_samples, fs=sample_rate / 24, nperseg=1024)
        peak_indices, frequencies = find_highest_magnitudes(psd, num_peaks=1, sample_rate=sample_rate / 24, fft_size=1024)
        print(f"lasfrecuencias {frequencies}")
        if peak_indices:
                peak_index = peak_indices[0]
                peak_frequency = frequencies[0]
                peak_psd = psd[peak_index]
                print(f"Peak frequency: {peak_frequency} Hz, PSD: {peak_psd}")
                # Group nearby frequencies as one station
                if peak_psd >= threshold:  # Check if the PSD value is above the radio station threshold          
                    print(f"Strong signal found at {freq / 1e6} MHz, PSD: {peak_psd}")  # Print the strong signal as it is found
                    current_station={'freq': freq, 'psd': peak_psd, 'band': (freq / 1e6),"array":psd}
                    radio_stations.append(current_station)
                    radio_stations=find_relative_frequency(radio_stations)
        freq += freq_step
    return radio_stations

def scan(args,plot_waterfall=False):
<<<<<<< HEAD
    print(args)
=======
>>>>>>> dev-1
    sdr = RtlSdr()
    sdr.sample_rate = 2400000
    sdr.err_ppm = args["ppm"]
    sdr.gain = args["gain"]
    lo_frequency = args["lnb_lo"]
    freq = args["start"]
    last_detected_station = None
    min_distance = 200000  # Minimum distance between stations in Hz
    
    #Se tiene que variar el treshold de acuerdo a las potencia de la señal y la ubicacion en la cual estan
    radio_psd_threshold = 3e-08
    freq_stop=args["stop"]
    freq_step=args["step"]
    start=time.time()
    radio_stations=psd_scanning(sdr,freq,freq_stop,freq_step,lo_frequency,radio_psd_threshold,args["threshold"])
    print(f"el tiempo que se demora el codigo en correr es {time.time()-start}")
<<<<<<< HEAD
    #print("\nDetected radio stations:")
=======
    print("\nDetected radio stations:")
>>>>>>> dev-1
    # sdr.close()
    # #------------------------PLOTTING WATERFALL SECTION ---------------------------#
    # wf = Waterfall()
    for station in radio_stations:
        print(f"Band: {station['freq'] / 1e6} MHz - PSD: {station['psd']}")
        # wf.sdr.fc = station["freq"]
        # if plot_waterfall:
        #     wf.showing_current_station()
        # sdr.close()
    #---------------------------STATION VERIFICATION ---------------------------#
    directory = os.path.dirname(os.path.realpath(__file__))
    file_path = Path(directory)/"Radioemisoras_ane.csv"
    # print(file_path)
    # verification_dic=station_verification(station["freq"], args["city"], file_path)
    return radio_stations


<<<<<<< HEAD
if __name__ == '__main__':
    args={'ppm': 0, 'gain': 15, 'threshold': 0.15, 'lnb_lo': -125000000, 'start': 88000000, 'stop': 108000000, 'step': 100000, 'city': 'CALDAS'}
    lista_frecuencias=scan(args=args)
=======
# if __name__ == '__main__':
#     args={'ppm': 0, 'gain': 15, 'threshold': 0.15, 'lnb_lo': -125000000, 'start': 88000000, 'stop': 108000000, 'step': 100000, 'city': 'CALDAS'}
#     lista_frecuencias=scan(args=args)
>>>>>>> dev-1
