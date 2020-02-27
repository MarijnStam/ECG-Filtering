# Copyright (c) 2016, Diarmaid O Cualain; Marijn Stam
# All rights reserved.

# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:

# * Redistributions of source code must retain the above copyright notice, this
#   list of conditions and the following disclaimer.

# * Redistributions in binary form must reproduce the above copyright notice,
#   this list of conditions and the following disclaimer in the documentation
#   and/or other materials provided with the distribution.

# * Neither the name of ecg_simulation nor the names of its
#   contributors may be used to endorse or promote products derived from
#   this software without specific prior written permission.

# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.


import matplotlib.pyplot as plt
import scipy.signal as signal
import scipy.fftpack as fourier
import numpy as np
import filters
import signal_tools
import neurokit2 as nk
from termcolor import colored
import sys


# ---------------------------Global variables--------------------------------------------
# ---------------------------------------------------------------------------------------
def main():

    # Filter requirements.
    order = 5       # Filter order
    sample_rate = 5000    # sample rate, Hz

    # The rest between two hearbeats, heartbeats will be simulated in the form of an ECG to add artifacts to the respiratory signal.
    samples_rest = 10

    # Simulated Beats per minute rate
    # For a health, athletic, person, 60 is resting, 180 is intensive exercising
    bpm = 60
    bps = bpm / 60

    # Bit resolution for simulation of ADC
    adc_bit_resolution = 1024

    # Simulated period of time in seconds that the ecg is captured in
    capture_length = 20


    # ---------------------------Start of all scripting logic--------------------------------
    # ---------------------------------------------------------------------------------------

    # The Filter class holds all our filters, we can pass our data to a filter in this class and we get the filtered result.
    filterInterface = filters.Filters(sample_rate, capture_length)
    signalInterface = signal_tools.SignalTools(sample_rate, capture_length)

    # The "Daubechies" wavelet is a rough approximation to a real,
    # single, heart beat ("pqrst") signal
    pqrst = signal.wavelets.daub(10)

    # Add the gap after the pqrst when the heart is resting. 
    zero_array = np.zeros(samples_rest, dtype=float)
    pqrst_full = np.concatenate([pqrst,zero_array])

    # Caculate the number of beats in capture time period 
    # Round the number to simplify things
    num_heart_beats = int(capture_length * bps)

    # Concatonate together the number of heart beats needed
    ecg_template = np.tile(pqrst_full , num_heart_beats)


    # Create sine waves for respiratory signal (.2Hz) and for mains hum (50Hz)
    # nk_respiratory is a more actual respiratory signal simulation based on 
    # the Neurokit2 library, the respiratory rate is amount of breath cycles per minute.
    nk_respiratory = nk.rsp_simulate(duration=capture_length, sampling_rate=sample_rate, respiratory_rate=15)
    sine_respiratory = signalInterface.sine_generator(0.2)
    sine_mains = signalInterface.sine_generator(50, 0.01)

    num_samples = sample_rate * capture_length
    # Add random (gaussian distributed) noise 
    noise = np.random.normal(0, 0.05, num_samples)

    respiratory_noisy =  (nk_respiratory + sine_mains + noise) 

    #Apply each filter individually (NOT SEQUENTIALLY)
    # respiratory_filtered_high = filterInterface.high_pass(respiratory_noisy, cutoff=.5, order=3)
    respiratory_filtered_low = filterInterface.low_pass(respiratory_noisy, cutoff=1, order=3)
    respiratory_filtered_median = filterInterface.median_filter(respiratory_noisy, 101)

    plt.show()

    # plt.figure("Results")
    # plt.title("Original signal compared to filtered results")
    # plt.plot(nk_respiratory, label="Original data")
    # plt.plot(respiratory_filtered_low["filtered_data"], label="Low passed")
    # plt.plot(respiratory_filtered_median, label="Median filter")
    # plt.legend(loc='best')
    # plt.show()

    print(colored('\nDone', 'green'))

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print(colored('\nDone, interrupted', 'green'))    
        sys.exit(0)