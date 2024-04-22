
import sys
import time
import argparse
import numpy as np
import os
import json
import matplotlib.pyplot as plt
from PyQt5 import QtWidgets
from PyQt5.QtCore import pyqtSlot
from rtlsdr import RtlSdr
from scipy import signal as sig
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QGridLayout
from matplotlib.mlab import psd
from water_fall_class import Waterfall
from pathlib import Path
import pandas as pd
import multiprocessing
import threading

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