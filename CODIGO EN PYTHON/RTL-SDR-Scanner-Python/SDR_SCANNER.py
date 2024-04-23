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
from funciones import find_highest_magnitudes,find_relative_frequency,tune_to_frequency,station_verification


'''
num_samples = Number of samples to read from the RTL-SDR device 
sample_rate = Rate which is reading a sample 
time_duration = This is the time duration of the captured signal is determined by the number of samples and the sample rate , is calculated by num_samples / sample_rate

'''
num_samples = 131072
sample_rate = 2.4e6  
time_duration = num_samples / sample_rate 

class ScannerApp(QtWidgets.QMainWindow):
    '''Se crea una clase co'''
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

        labels = ['PPM', 'Gain', 'Threshold', 'LNB LO', 'Start', 'Stop', 'Step','City']
        self.inputs = {}

        default_values = {'ppm': '0', 'gain': '25', 'threshold': '0.5', 'lnb lo': '-125000000', 'start': '88000000', 'stop': '108000000', 'step': '100000', 'city': 'CALDAS'}

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
            city=str(self.inputs['city'].text()),
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
                        radio_stations.append(current_station)
                        radio_stations=find_relative_frequency(radio_stations)

                    if peak_psd >= threshold:
                        self.result_list.addItem('{:.3f} MHz - {:.2f}'.format(freq / 1e6, peak_psd * 100))
            freq += freq_step
        return radio_stations
   
        
    def scan(self, args,plot_waterfall=False):
        sdr = RtlSdr()
        sdr.sample_rate = sample_rate = 2400000
        sdr.err_ppm = args.ppm
        sdr.gain = args.gain

        lo_frequency = args.lo

        freq = args.start
        last_detected_station = None
        min_distance = 200000  # Minimum distance between stations in Hz
        
        #Se tiene que variar el treshold de acuerdo a las potencia de la señal y la ubicacion en la cual estan
        radio_psd_threshold = 2e-08
        freq_stop=args.stop
        freq_step=args.step
        start=time.time()
        radio_stations=self.psd_scanning(sdr,freq,freq_stop,freq_step,lo_frequency,radio_psd_threshold,args.threshold)
        print(radio_stations)
        print(f"el tiempo que se demora el codigo en correr es {time.time()-start}")
        print("\nDetected radio stations:")
        sdr.close()
        #------------------------PLOTTING WATERFALL SECTION ---------------------------#
        wf = Waterfall()
        for station in radio_stations:
            print(f"Band: {station['freq'] / 1e6} MHz - PSD: {station['psd']}")
            wf.sdr.fc = station["freq"]
            if plot_waterfall:
                wf.showing_current_station()

            sdr.close()

        #---------------------------STATION VERIFICATION ---------------------------#
        directory = os.path.dirname(os.path.realpath(__file__))
        file_path = Path(directory)/"Radioemisoras_ane.csv"
        print(file_path)
        verification_dic=station_verification(station["freq"], args.city, file_path)
        print(verification_dic)
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
