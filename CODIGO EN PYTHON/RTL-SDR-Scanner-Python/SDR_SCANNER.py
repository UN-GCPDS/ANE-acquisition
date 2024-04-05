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
import multiprocessing
import threading


'''
num_samples = Number of samples to read from the RTL-SDR device 
sample_rate = Rate which is reading a sample 
time_duration = This is the time duration of the captured signal is determined by the number of samples and the sample rate , is calculated by num_samples / sample_rate

'''
num_samples = 131072
sample_rate = 2.4e6  
time_duration = num_samples / sample_rate 

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

    return not_registered_stations, registered_stations
class ScannerApp(QtWidgets.QMainWindow):
    def __init__(self):
        super(ScannerApp, self).__init__()

        self.init_ui()
        self.show()

    def init_ui(self):
        self.setWindowTitle('RTL-SDR Scanner')
        self.resize(400, 300)

        central_widget = QtWidgets.QWidget()
        self.setCentralWidget(central_widget)

        grid = QtWidgets.QGridLayout(central_widget)

        labels = ['PPM', 'Gain', 'Threshold', 'LNB LO', 'Start', 'Stop', 'Step']
        self.inputs = {}

        default_values = {'ppm': '0', 'gain': '25', 'threshold': '0.5', 'lnb lo': '-125000000', 'start': '88000000', 'stop': '108000000', 'step': '100000'}

        for i, label_text in enumerate(labels):
            label = QtWidgets.QLabel(label_text)
            input = QtWidgets.QLineEdit()
            input.setText(default_values[label_text.lower()])
            grid.addWidget(label, i, 0)
            grid.addWidget(input, i, 1)

            self.inputs[label_text.lower()] = input

        self.scan_button = QtWidgets.QPushButton('Start Scan')
        self.scan_button.clicked.connect(self.start_scan)
        grid.addWidget(self.scan_button, len(labels), 0, 1, 2)

        self.result_list = QtWidgets.QListWidget()
        grid.addWidget(self.result_list, 0, 2, len(labels), 1)

    @pyqtSlot()
    def start_scan(self):
        args = self.get_args()
        lista_frecuencias=self.scan(args)
    
    def get_args(self):
        return argparse.Namespace(
            ppm=int(self.inputs['ppm'].text()),
            gain=int(self.inputs['gain'].text()),
            threshold=float(self.inputs['threshold'].text()),
            lo=int(self.inputs['lnb lo'].text()),
            start=int(self.inputs['start'].text()),
            stop=int(self.inputs['stop'].text()),
            step=int(self.inputs['step'].text()),
        )
    def psd_scanning(self,sdr,freq,freq_stop,freq_step,lo_frequency,radio_psd_threshold,threshold):
        '''Este metodo realiza un escaneo  '''

        radio_stations = []
        for i in range(freq,freq_stop,freq_step):
            print(f"Scanning frequency: {freq / 1e6} MHz")
            tune_to_frequency(sdr, freq, lo_frequency)
            iq_samples = self.read_samples(sdr, freq)
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
                    if peak_psd >= radio_psd_threshold:  # Check if the PSD value is above the radio station threshold
                        
                        print(f"Strong signal found at {freq / 1e6} MHz, PSD: {peak_psd}")  # Print the strong signal as it is found
                        current_station={'freq': freq, 'psd': peak_psd, 'band': (freq / 1e6),"array":psd}
                        #addition=find_relative_frequency(current_station,radio_stations[-1])
                       #print(addition)
                        radio_stations.append(current_station)
                        radio_stations=find_relative_frequency(radio_stations)
                        last_detected_station = radio_stations[-1]
                        print(last_detected_station)

                    if peak_psd >= threshold:
                        self.result_list.addItem('{:.3f} MHz - {:.2f}'.format(freq / 1e6, peak_psd * 100))
            # freq += freq_step

        return radio_stations
    # def psd_parallel_scanner(self,sdr,freq,lo_frequency,radio_psd_threshold,threshold):
    #     '''Este metodo realiza un escaneo  '''
    #     print(f"Scanning frequency: {freq / 1e6} MHz")
    #     tune_to_frequency(sdr, freq, lo_frequency)
    #     iq_samples = self.read_samples(sdr, freq)
    #     iq_samples = sig.decimate(iq_samples, 24)

    #     f, psd = sig.welch(iq_samples, fs=sample_rate / 24, nperseg=1024)

    #     peak_indices, frequencies = find_highest_magnitudes(psd, num_peaks=1, sample_rate=sample_rate / 24, fft_size=1024)
    #     print(f"lasfrecuencias {frequencies}")
    #     if peak_indices:
    #         peak_index = peak_indices[0]
    #         peak_frequency = frequencies[0]
    #         peak_psd = psd[peak_index]
    #         print(f"Peak frequency: {peak_frequency} Hz, PSD: {peak_psd}")

    #         # Group nearby frequencies as one station
    #         if peak_psd >= radio_psd_threshold:  # Check if the PSD value is above the radio station threshold
                        
    #             print(f"Strong signal found at {freq / 1e6} MHz, PSD: {peak_psd}")  # Print the strong signal as it is found
    #             current_station={'freq': freq, 'psd': peak_psd, 'band': (freq / 1e6),"array":psd}
    #             #addition=find_relative_frequency(current_station,radio_stations[-1])
    #             #print(addition)
    #             radio_stations.append(current_station)
    #             radio_stations=find_relative_frequency(radio_stations)
    #             last_detected_station = radio_stations[-1]
    #             print(last_detected_station)
    #             if peak_psd >= threshold:
    #                 self.result_list.addItem('{:.3f} MHz - {:.2f}'.format(freq / 1e6, peak_psd * 100))
    #         # freq += freq_step

    #     return current_station
        
    def scan(self, args):
        sdr = RtlSdr()
        sdr.sample_rate = sample_rate = 2400000
        sdr.err_ppm = args.ppm
        sdr.gain = args.gain

        lo_frequency = args.lo

        freq = args.start
        last_detected_station = None
        min_distance = 200000  # Minimum distance between stations in Hz
        
        #Se tiene que variar el treshold de acuerdo a las potencia de la señal y la ubicacion en la cual estan
        radio_psd_threshold = 2.5e-07
        freq_stop=args.stop
        freq_step=args.step
        list_frequencies=[freq+x*1e5 for x in range(int((freq_stop-freq)/1e5)+1)]
        start=time.time()
        # pool = multiprocessing.Pool(3)
        # radio_stations = pool.map(self.psd_parallel_scanner, args=(sdr,list_frequencies,lo_frequency,radio_psd_threshold,args.threshold))


        radio_stations=self.psd_scanning(sdr,freq,freq_stop,freq_step,lo_frequency,radio_psd_threshold,args.threshold)
        print(radio_stations)
        print(f"el tiempo que se demora el codigo en correr es {time.time()-start}")
        print("\nDetected radio stations:")
        sdr.close()
        wf = Waterfall()
        for station in radio_stations:
            print(f"Band: {station['freq'] / 1e6} MHz - PSD: {station['psd']}")
            sdr.fc = station["freq"]
            wf.showing_current_station()

            sdr.close()
        return radio_stations

    @staticmethod
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


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = ScannerApp()
    sys.exit(app.exec_())
