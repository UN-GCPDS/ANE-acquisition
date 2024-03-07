import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from water_fall_class import Waterfall
NFFT = 1024*4
NUM_SAMPLES_PER_SCAN = NFFT*16
NUM_BUFFERED_SWEEPS = 100
NUM_SCANS_PER_SWEEP = 1

image_buffer = -100*np.ones((NUM_BUFFERED_SWEEPS,\
                                 NUM_SCANS_PER_SWEEP*NFFT))
print(image_buffer.shape)