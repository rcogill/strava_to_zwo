'''
Usage: python strava_to_zwo.py --in_file FILENAME.json --ftp FTP_VALUE

This script generates a Zwift structured workout that aims to
replicate the efforts of a real-world activity as recorded in Strava.

The input provided to this script is a JSON-formatted Strava activity,
and the output is a Zwift structured workout file (.zwo).
'''

import json
import numpy as np
from scipy.signal import medfilt
from scipy import interpolate
from sklearn.cluster import KMeans
import click

#-----------------------------------------

def load_ride_data(activity_file):
    '''This function generates a dictionary containing data from
    a Strava sctivity from a given JSON-formatted activity file.

    Inputs:
    - activity_file : The name of a JSON-formatted Strava activity file
    Returns: A dictionary containing data from the activity
    '''
    f = open(activity_file, 'r')
    ride_json = f.read()
    f.close()

    ride = json.loads(ride_json)

    for k in ride:
        ride[k] = [x if x != None else 0 for x in ride[k]]

    return ride

#-----------------------------------------

def resample_ride_data(ride, min_p=100.0):
    '''This function resamples power data for an activity at a
    rate of one sample-per-second.

    Inputs:
    - ride : A dictionary containing data from the activity
    Returns: A list containing power data sampled at one second intervals
    '''
    interp_watt = interpolate.interp1d(ride['time'], ride['watts'])

    max_t = max(ride['time'])
    new_t = range(0, max_t)
    new_p = interp_watt(new_t)

    new_p = np.maximum(min_p, new_p)

    return new_p

#-----------------------------------------

def get_quantized_power(sm_p, n_clusters=7):
    '''This function produces a quantized approximation of the
    power throughout the activity. The number of distinct power
    levels to use is specified by n_clusters.

    Inputs:
    - sm_p : A list containing smoothed power data sampled at one second intervals
    - n_clusters : The number of distinct power levels to quantize to
    Returns: A list containing quantized power data sampled at one second intervals
    '''

    kmeans = KMeans(n_clusters=n_clusters, random_state=0)\
     .fit(sm_p.reshape(-1, 1))
    q_p = [float(kmeans.cluster_centers_[i])\
     for i in kmeans.predict(sm_p.reshape(-1, 1))]

    return q_p

#-----------------------------------------

def get_power_segents(q_p):
    '''This function generates a representation of the quantized
    power outputs of an activity as a sequence of (duration, power)
    tuples.

    Inputs:
    - q_p : A list containing quantized power data sampled at one second intervals
    Returns: A list of tuples representing the quantized power sequence
    '''

    segments = []

    start = 0
    this_val = q_p[0]
    for i in range(1, len(q_p)):
        if q_p[i] != this_val:
            segments.append((i-start, float(this_val)))
            # Reset new start values
            start = i
            this_val = q_p[i]
    segments.append((len(q_p)-1-start, float(this_val)))

    return segments

#-----------------------------------------

def get_intervals(segments, min_duration=30):
    '''This function merges consecutive, short intervals
    to reduce rapid switching among power levels. The minimum
    allowable duration of an interval is set by 'min_duration'.

    Inputs:
    - segments : A list of tuples representing the quantized power sequence
    Returns: A list of tuples representing the quantized power sequence,
      where short intervals have been merged
    '''

    dur = 0
    last_p = 0.0
    intervals = []
    for i in range(0, len(segments)):
        if max(dur, segments[i][0]) < min_duration:
            last_p = (float(dur)/(dur+segments[i][0]))*last_p\
             + (float(segments[i][0])/(dur+segments[i][0]))*segments[i][1]
            dur += segments[i][0]
        else:
            last_p = (float(dur)/(dur+segments[i][0]))*last_p\
             + (float(segments[i][0])/(dur+segments[i][0]))*segments[i][1]
            dur += segments[i][0]
            intervals.append((dur, int(last_p)))
            dur = 0
            last_p = 0.0

    return intervals

#-----------------------------------------

def generate_zwo_file(intervals, ftp, zwo_file):
    '''This function generates an XML-formatted .zwo file
    from a given list of intervals.

    Inputs:
    - intervals : A list of tuples containing a sequence of power intervals
    - ftp : The user's function threshold power, in watts
    - zwo_file : The name of the .zwo file that will be written
    Returns: True if successful
    '''

    f = open(zwo_file, 'w')

    f.write('<?xml version="1.0" ?>\n')
    f.write('<workout_file>\n')
    f.write('  <workout>\n')
    for this_int in intervals:
        f.write('    <SteadyState Duration="%d" Power="%0.2f">'\
         %(this_int[0], float(this_int[1])/ftp))
        f.write('</SteadyState>\n')
    f.write('  </workout>\n')
    f.write('</workout_file>\n')

    f.close()

    return True

#-----------------------------------------

@click.command()
@click.option('--in_file', default=None,\
 help='Input JSON file containing Strava activity data')
@click.option('--ftp', default=None,\
 help='Your functional threshold power, in Watts')
def main(in_file, ftp):
    '''This function performs all steps required to construct a
    .zwo file from the input activity.

    Inputs:
    - in_file : The name of a JSON-formatted Strava activity file
    - ftp : The user's function threshold power, in watts
    Returns: True if successful
    '''

    # Load power data from an activity
    try:
        ride = load_ride_data(in_file)
        new_p = resample_ride_data(ride)
    except:
        print('Need to provide a valid JSON-formatted Strava activity')
        exit()

    # Smoothing and quantizing power data
    sm_p = medfilt(new_p, 21)
    q_p = get_quantized_power(sm_p)

    # Generating intervals
    seg = get_power_segents(q_p)
    intervals = get_intervals(seg)

    # Writing ZWO file
    if '.' in in_file:
        zwo_file = '.'.join(in_file.split('.')[:-1]) + '.zwo'
    else:
        zwo_file = in_file + '.zwo'
    if ftp is None:
        print('No FTP provided, using default FTP of 300W')
        ftp = 300.0
    else:
        try:
            ftp = float(ftp)
        except ValueError:
            print('FTP must be a numerical value, using default FTP of 300W')
            ftp = 300.0
    generate_zwo_file(intervals, ftp, zwo_file)

    print('Created Zwift structured workout file \'%s\''%(zwo_file))

    return True

#+++++++++++++++++++++++++++++++++++++++++++++

if __name__ == '__main__':
    main()
