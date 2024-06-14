import numpy as np
import hackrf
from scipy.signal import resample

class FrequencyScaling:
    def _init_(self, samp_rate=2e6, center_freq=100e6, scaled_samp_rate=500e3):
        self.samp_rate = samp_rate
        self.center_freq = center_freq
        self.scaled_samp_rate = scaled_samp_rate
        self.device = hackrf.HackRF()
        self.device.open()
        self.device.set_sample_rate(self.samp_rate)
        self.device.set_center_freq(self.center_freq)
        self.device.set_lna_gain(40)
        self.device.set_vga_gain(20)

    def frequency_scaling(self, samples):
        # Resample the data to the new sample rate
        num_samples = int(len(samples) * self.scaled_samp_rate / self.samp_rate)
        resampled_samples = resample(samples, num_samples)
        return resampled_samples

    def start(self):
        try:
            self.device.start_rx_mode()
            self.device.set_sample_block_callback(self.sample_callback)
        except Exception as e:
            print(f"Error: {e}")

    def sample_callback(self, samples, num_samples):
        # Convert the byte samples to complex numbers
        complex_samples = np.frombuffer(samples, dtype=np.complex64)
        # Perform frequency scaling
        scaled_samples = self.frequency_scaling(complex_samples)
        # Process the scaled_samples as needed, here we just print their length
        print(f"Processed {len(scaled_samples)} scaled samples")

    def stop(self):
        self.device.stop_rx_mode()
        self.device.close()
   

