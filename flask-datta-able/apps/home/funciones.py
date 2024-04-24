
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
# from water_fall_class import Waterfall
from pathlib import Path
import pandas as pd
import multiprocessing
import threading
from scipy import signal 
def find_relative_frequency(radio):
    '''
    Selects frequencies where the Power Spectral Density (PSD) is higher 
    and filters out closely spaced frequencies with lower PSD.

    Argument:
        radio -- (list of dicts): A list of dictionaries, each containing information about a frequency.
                               Each dictionary has the keys 'freq' (frequency), 'psd' (Power Spectral Density),
                               'band' (frequency band), and 'array'.

    Returns:
        radio --(list of dicts): The filtered list of dictionaries, 
                                where each dictionary contains information about a frequency that has passed the filtering criteria.
    '''
    try:
        current=radio[-1]
        last=radio[-2]
        diff_freq=abs(float(current["freq"])-float(last["freq"]))
        diff_psd=float(current["psd"])-float(last["psd"])
        print(current["psd"],last["psd"],diff_psd)
        if diff_freq == 1e5:
            min_psd=min(float(current["psd"]),float(last["psd"]))
            if min_psd == float(current["psd"]):
                radio.pop(-1)
                return radio
            else:
                radio.pop(-2)
                return radio
        else:
            return radio
    except IndexError as e:
        return radio

def tune_to_frequency(radio, true_frequency, lo_frequency):
    """
    Tunes the SDR frequency by adding an offset to the true frequency

    Argument:
        radio --(list of dicts): A list of dictionaries, each containing information about a frequency.
                               Each dictionary has the keys 'freq' (frequency), 'psd' (Power Spectral Density),
                               'band' (frequency band), and 'array', providing details of each frequency.

        true_frequency --(int): The actual frequency to be tuned.

        lo_frequency --(int): The offset frequency to be added to the true frequency.

    Returns:
        None: This function adjusts the frequency in-place within the 'radio' list; it does not return anything.
    """
    shifted_frequency = true_frequency + lo_frequency
    radio.center_freq = shifted_frequency
    print(f"Tuned to {true_frequency / 1e6} MHz (shifted to {shifted_frequency / 1e6} MHz)")


def find_highest_magnitudes(data, num_peaks=8, sample_rate=2.048e6, fft_size=1024):
    '''
    Identifies the indices and frequencies of the highest magnitude peaks within a dataset,
    typically from an FFT analysis.

    Argument:
        data --(array-like): The dataset to analyze.
        num_peaks --(int): The number of highest peaks to identify. Defaults to 8.
        sample_rate --(float, optional): The sample rate of the dataset. Defaults to 2.048e6.
        fft_size --(int, optional): The FFT size used to generate the dataset. Defaults to 1024.

    Returns:
        peak_indice --(array): The indices of the peaks within the dataset and the corresponding frequencies.
        frequencies --(array): Current frequency tuned

    '''
    if len(data) < num_peaks:
        print("Not enough data points to find the desired number of peaks.")
        return [], []

    peak_indices = np.argpartition(data, -num_peaks)[-num_peaks:]
    peak_indices = peak_indices[np.argsort(-data[peak_indices])]
    bin_width = sample_rate / fft_size
    frequencies = peak_indices * bin_width
    return peak_indices, frequencies

def station_verification(radio, state, file_path):
    """
    Verifies the presence of radio stations in a database for a specific city by comparing
    given frequencies in Hertz against those registered in the FM band. This function now
    dynamically reads from a specified CSV file path to obtain the database of radio stations.

    Parameters:
    - radio (list of int): List of radio frequencies in Hertz to verify.
    - state (str): Name of the state where the radio stations are to be verified.
    - file_path (str): The file path to the CSV file containing the radio station database.

    Returns:
    - tuple of (np.ndarray, np.ndarray):
        - The first element is a NumPy array containing the frequencies (in MHz) of the radio stations
          that are not registered in the database.
        - The second element is a NumPy array containing the frequencies (in MHz) of the radio stations
          that are registered in the database.
    """
    df = pd.read_csv(file_path, delimiter=';', on_bad_lines='warn')
    df = df[(df['DEPARTAMENTO'] == state) & (df['BANDA'] == 'FM')]
    df['FRECUENCIA'] = df['FRECUENCIA'].str.replace(' MHz', '').astype(float)
    df = df[['FRECUENCIA']]
    df_array = df.values
    df_array = df_array.flatten()

    radio = np.array(radio)
    freq_array = radio / 1e6

    not_registered_stations = np.setdiff1d(freq_array, df_array)
    registered_stations = np.intersect1d(freq_array, df_array)

    print(f'Las emisoras que no están en la base de datos son: {not_registered_stations}\n'
          f'y las emisoras que si están son: {registered_stations}')
    dic={"registered_stations":registered_stations,"not_registered_stations":not_registered_stations}
    return dic



#------------------------------------------FUNCIONES DEMODULACION FM ---------------------------#
def downsample(x, M, p=0):  
    if not isinstance(M, int):
        raise TypeError("M must be an int")
    x = x[0:int(np.floor(len(x) / M)) * M]
    x = x.reshape((int(np.floor(len(x) / M)), M))
    y = x[:,p]
    return y

def fm_discrim(x):
    X = np.real(x)
    Y = np.imag(x)
    b = np.array([1, -1])
    dY = signal.lfilter(b, 1, Y)
    dX = signal.lfilter(b, 1, X)
    discriminated = (X * dY - Y * dX) / (X**2 + Y**2 + 1e-10)
    return discriminated

def fm_audio(samples, fs=2.4e6, fc=92.7e6, fc1=200e3, fc2=12e3, d1=10, d2=5, plot=False):
    lpf_b1 = signal.firwin(64, fc1/(float(fs)/2))
    lpf_b2 = signal.firwin(64, fc2/(float(fs)/d1/2))
    
    # 1st filtering
    samples_filtered_1 = signal.lfilter(lpf_b1, 1, samples)
    # 1st decimation
    samples_decimated_1 = downsample(samples_filtered_1, d1)
    # phase discrimination
    samples_discriminated = fm_discrim(samples_decimated_1)
    # 2nd filtering
    samples_filtered_2 = signal.lfilter(lpf_b2, 1, samples_discriminated)
    # 2nd decimation
    audio = downsample(samples_filtered_2, d2)
    
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
    
def fm_audio(samples, fs=2.4e6, fc=92.7e6, fc1=200e3, fc2=12e3, d1=10, d2=5, plot=False):
    lpf_b1 = signal.firwin(64, fc1/(float(fs)/2))
    lpf_b2 = signal.firwin(64, fc2/(float(fs)/d1/2))
    
    # 1st filtering
    samples_filtered_1 = signal.lfilter(lpf_b1, 1, samples)
    # 1st decimation
    samples_decimated_1 = downsample(samples_filtered_1, d1)
    # phase discrimination
    samples_discriminated = fm_discrim(samples_decimated_1)
    # 2nd filtering
    samples_filtered_2 = signal.lfilter(lpf_b2, 1, samples_discriminated)
    # 2nd decimation
    audio = downsample(samples_filtered_2, d2)
    
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