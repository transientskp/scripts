#!/usr/bin/env python
"""
Quick & dirty estimate of size of visibility data given a certain number of
stations and observation length.
"""
import sys
import scipy
import scipy.misc

def subband_size(time, num_baselines, num_channels=256, timestep=1.0066328048706055):
    data_col = 4 * 64 * num_channels # 4 pols, each with complex64
    uvw_col = 3 * 64 # 3 coords, each float64
    time_col = 1 * 64 # float64
    per_row = data_col + uvw_col + time_col

    timesteps = time / timestep
    rows = timesteps * num_baselines

    return rows * per_row

def bits_to_MB(bits):
    return bits / (8.0 * 1024**2)

def num_baselines(num_stations):
    return scipy.misc.comb(num_stations, 2, exact=1) + num_stations

def total_size(subband_size, num_subbands=244):
    return num_subbands * subband_size

if __name__ == "__main__":
    time = float(sys.argv[1])
    num_stations = int(sys.argv[2])
    subband = subband_size(time, num_baselines(num_stations))
    print "Each subband is %f MB" % bits_to_MB(subband)
    print "Total size is then %f MB" % bits_to_MB(total_size(subband))
