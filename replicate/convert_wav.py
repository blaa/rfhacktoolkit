#!/usr/bin/env python3

# Public domain
# Hacked during experiments - beware.
# Author: Tomasz bla Fortuna

import sys
import wave
import struct

TRESHOLD_WIDTH = 0.2

def read(wfile):
    samples = []
    stereo = (wfile.getnchannels() == 2)
    for i in range(wfile.getnframes()):
        frame = wfile.readframes(1)
        if stereo:
            left, right = struct.unpack('hh', frame)
            left, right = left/32768.0, right/32768.0
            sample = (left + right) / 2.0
        else:
            sample = struct.unpack('h', frame)
            sample /= 32768.0
        samples.append(sample)
    return samples

def analyze(samples, sampling):
    "Estimate what is 0, and what is 1 - no clock recovery"
    average = sum(samples) / len(samples)

    # Get sorted 80% of the samples - cutting edges
    to_cut = int(0.1 * len(samples))
    sorted_samples = sorted(samples[to_cut:-to_cut])

    # Average 10% highest and 10% lowest to get high/low level estimate
    to_avg = int(0.1 * len(sorted_samples))
    high_samples = sorted_samples[-to_avg:]
    low_samples = sorted_samples[:to_avg]
    high = sum(high_samples) / len(high_samples)
    low = sum(low_samples) / len(low_samples)
    medium = (high + low) / 2.0
    border = TRESHOLD_WIDTH * (high-low)
    high_treshold = medium + border
    low_treshold = medium - border

    print("Average level", average)
    print("HIGH / LOW:", high, low)
    print("MEDIUM:", medium)
    print("HIGH/LOW TRESHOLD:", high_treshold, low_treshold)
    print("HIGH", sorted_samples[-5:])
    print("LOW", sorted_samples[:5])

    return {
        'h': high_treshold,
        'l': low_treshold
    }

def convert(samples, sampling, cfg, data_filename):
    "Convert to time data"
    f_output = open(data_filename, 'w')
    samp_output = wave.open(data_filename + '_output.wav', 'w')
    samp_output.setparams((2, 2, sampling, 0, 'NONE', 'not compressed'))

    cur_state = 0

    def get_state(sample):
        if sample > cfg['h']:
            return 1
        elif sample < cfg['l']:
            return 0
        else:
            return cur_state

    cur_state = get_state(samples[0])

    # Point in time when bit was changed
    state_time = 0

    time_pos = 0
    for sample in samples:
        new_state = get_state(sample)
        if new_state != cur_state:
            if state_time == 0:
                # In first bit change ignore usleep
                time_in_prev_state = 0
            else:
                time_in_prev_state = int((time_pos - state_time) * 10**9)
            print("NANOSLEEP", time_in_prev_state)
            print("SET", new_state)
            f_output.write("N%d\n" % time_in_prev_state)
            f_output.write("S%d\n" % new_state)
            cur_state = new_state
            state_time = time_pos


        data = struct.pack('hh', 32765 * cur_state, 32765 * cur_state)
        print("WRITE", cur_state, data)
        samp_output.writeframes(data)

        time_pos += 1.0 / sampling

    f_output.close()
    samp_output.close()

def main():
    if len(sys.argv) != 3:
        print("%s input.wav output.data" % sys.argv[0])
        sys.exit(1)
    fname = sys.argv[1]
    data_name = sys.argv[2]
    wfile = wave.open(fname)
    print(wfile)
    channels = wfile.getnchannels()
    samp_width = wfile.getsampwidth()
    sampling = wfile.getframerate()
    frames = wfile.getnframes()
    print("Channels", channels)
    print("Samp width", samp_width)
    print("Sampling", sampling)
    print("Frames", frames)
    length = float(frames) / sampling
    print("Length", length, "[s]")

    samples = read(wfile)

    cfg = analyze(samples, sampling)
    convert(samples, sampling, cfg, data_name)

if __name__ == "__main__":
    main()
