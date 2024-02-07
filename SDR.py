import numpy as np
import matplotlib.pyplot as plt
from pylab import *
from rtlsdr import *

def capture_samples(sdr, sample_rate, frequency, num_samples):
    sdr.sample_rate = sample_rate
    sdr.center_freq = frequency
    samples = sdr.read_samples(num_samples)
    return samples

def energy_detection(samples, threshold):
    energy = np.sum(np.abs(samples) ** 2)
    return energy > threshold

if 1 == 1:
    # Configure your SDR device
    sdr = RtlSdr()
    sample_rate = 2.048e6  # 2.048 MHz sample rate
    frequency = 95.1e6  # 100 MHz center frequency
    num_samples = 1024  # Number of samples to capture

    # Set a threshold (you need to adjust this based on your environment)
    detection_threshold = 1e8

    try:
        # Capture samples from the SDR
        samples = capture_samples(sdr, sample_rate, frequency, num_samples)

        # Perform energy detection
        signal_detected = energy_detection(samples, detection_threshold)

        # Display the result
        if signal_detected:
            print("Signal detected!")
        else:
            print("No signal detected.")

        # Optionally, plot the real part of the captured samples
        plt.plot(np.real(samples))
        plt.title('Captured Samples')
        plt.show()

    finally:
        # Close the SDR device
        sdr.close()