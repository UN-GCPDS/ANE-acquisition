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
num_samples = Numero de muestras para leer del RTL-SDR 
sample_rate = tiempo de muestreo
time_duration = tiempo de duracion de captura de la señal se estima como  num_samples / sample_rate

'''
num_samples = 131072
sample_rate = 2.4e6  
time_duration = num_samples / sample_rate 


def read_samples(sdr, freq):
    f_offset = 25000
    sample_rate = 2400000
    sdr.center_freq = freq - f_offset
<<<<<<< HEAD
    time.sleep(0.01) 
    iq_samples = sdr.read_samples(2**15) 
=======
    time.sleep(0.01) # 
    iq_samples = sdr.read_samples(2**17) #Numero de muestras
>>>>>>> bd1823a57bf3ee7664bddfabd0b3382dc9ae26bb
    iq_samples = iq_samples[0:600000]
    fc1 = np.exp(-1.0j * 2.0 * np.pi * f_offset / sample_rate * np.arange(len(iq_samples)))
    iq_samples = iq_samples * fc1
    return iq_samples

def psd_scanning(sdr,freq,freq_stop,freq_step,lo_frequency,radio_psd_threshold,threshold):
    '''
    Este metodo realiza un escaneo para determinar las frecuencias presentes en un rango de frecuencias utilizando decimacion
    , estimando psd por medio del metodo de welch y 
    
    '''
    radio_stations = []
    threshold=threshold*10**-6
    
    for i in range(freq,freq_stop,freq_step):
        print(f"Scanning frequency: {freq / 1e6} MHz")
        #----------SE LEE LAS MUESTRAS DEL SDR ---------------------#
        iq_samples = read_samples(sdr, freq)
        #----------SE PROCEDE A REALIZAR DECIMACION DE LA SEÑAL --------------------#
        iq_samples = sig.decimate(iq_samples, 24)
        
        f, psd = sig.welch(iq_samples, fs=sample_rate / 24, nperseg=1024)
        peak_indices, frequencies = find_highest_magnitudes(psd, num_peaks=1, sample_rate=sample_rate / 24, fft_size=1024)
        if peak_indices:
                peak_index = peak_indices[0]
                peak_frequency = frequencies[0]
                peak_psd = psd[peak_index]
                print(f"Peak frequency: {peak_frequency} Hz, PSD: {peak_psd}")
                if peak_psd >= threshold:  # Miramos si el psd esta por encima del umbral          
                    print(f"Strong signal found at {freq / 1e6} MHz, PSD: {peak_psd}")  # entregamos la señal con el psd mas alto
                    current_station={'freq': freq, 'psd': peak_psd, 'band': (freq / 1e6),"array":psd}
                    radio_stations.append(current_station)
                    radio_stations=find_relative_frequency(radio_stations)
        freq += freq_step
    return radio_stations

def scan(args,plot_waterfall=False):
    print(args)
    sdr = RtlSdr()
    sdr.sample_rate = 2400000
    sdr.err_ppm = args["ppm"]
    sdr.gain = args["gain"]
    lo_frequency = args["lnb_lo"]
    freq = args["start"]
    last_detected_station = None
    min_distance = 200000  # Distancia minima entre estaciones
    
    #Se tiene que variar el treshold de acuerdo a las potencia de la señal y la ubicacion en la cual estan
    radio_psd_threshold = 3e-08
    freq_stop=args["stop"]
    freq_step=args["step"]
    start=time.time()
    radio_stations=psd_scanning(sdr,freq,freq_stop,freq_step,lo_frequency,radio_psd_threshold,args["threshold"])
    print(f"el tiempo que se demora el codigo en correr es {time.time()-start}")
    print("\nDetected radio stations:")
    # #------------------------PLOTTING WATERFALL SECTION ---------------------------#
    for station in radio_stations:
        print(f"Band: {station['freq'] / 1e6} MHz - PSD: {station['psd']}")
    #---------------------------STATION VERIFICATION ---------------------------#

    directory = os.path.dirname(os.path.realpath(__file__))
    file_path = Path(directory)/"Radioemisoras_ane.csv"
    return radio_stations

