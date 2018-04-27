# Standard modules
import os
import itertools
from collections import OrderedDict
import numpy as np
import matplotlib as mpl
import sunpy

mpl.use('TkAgg') #used to be mpl.use('macosx')
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as dates
import astropy.units as u
from astropy.time import Time
from sunpy.instr import goes
from sunpy.time import TimeRange
from datetime import datetime, timedelta

import progressbar
from scipy.io.idl import readsav
from sunpy.util.metadata import MetaDict
from automatic_fit_light_curve import automatic_fit_light_curve
import math
import sys

# Custom modules
from jpm_time_conversions import metatimes_to_seconds_since_start, datetimeindex_to_human
from jpm_logger import JpmLogger

__author__ = 'Tyler J Albee & Shawn A Polson'
__contact__ = 'tyal7988@colorado.edu'

def detectStealthCMEsInSOHO(output_path='/Users/shawnpolson/Pictures/stealth_cmes_real_window/'):
    soho = pd.read_csv('/Users/shawnpolson/Documents/School/Spring 2018/Data Mining/StealthCMEs/savesets/Historical CME Data (SOHO).csv')
    print(soho.head())

    #goes_data = readsav('/Users/tyleralbee/Desktop/GoesEventsMegsAEra.sav')

    #1. Add new column to SOHO catalog named "Stealth?"
    sLength = len(soho['Time'])  # number of rows in the SOHO catalog
    soho['Stealth?'] = pd.Series(np.nan, index=soho.index)  # add the new column to the catalog

    csv_filename = output_path + 'stealth_soho_catalog_best_window_cont_{0}.csv'.format(Time.now().iso)
    soho.to_csv(csv_filename, header=True, index=False, mode='w')

    # Start a progress bar
    widgets = [progressbar.Percentage(), progressbar.Bar(), progressbar.Timer(), ' ', progressbar.AdaptiveETA()]

    progress_bar_sliding_window = progressbar.ProgressBar(
        widgets=[progressbar.FormatLabel('Stealth CME Search ')] + widgets,
        max_value=int(sLength)).start()

    #2. Set up loop through SOHO catalog
    for i in range(0, int(sLength)):
        #3. For each row, pull date and time from row
        soho_row = soho.iloc[i]
        date = soho_row['Date']
        time = soho_row['Time']
        timeObj = pd.to_datetime(date + 'T' + time)

        #4. Convert that date/time to a sunpy.time.TimeRange (will need to decide how wide of a time window)
            # From a CME researcher: "an event is likely correlated if the CME SOHO/LASCO start time is between 2 hours before
            # and 4 hours after the dimming start time and within 45 degrees of the dimming location
            # (I convert dimming central coordinate to PA and compare that with CME PA)”.
            # TODO: check angles
        time_range = TimeRange(timeObj - timedelta(hours=4), timeObj + timedelta(hours=2))  # per the above comment
        #5. Send TimeRange to sunpy.instr.goes.get_goes_event_list(timerange, goes_class_filter=None)
        flares = sunpy.instr.goes.get_goes_event_list(time_range, goes_class_filter=None)
        #print(flares)

        #6. If that returns an empty list, add 'yes' to row['Stealth?']
        if (len(flares) == 0):
            soho_row['Stealth?'] = 'yes'
            soho.iloc[i] = soho_row
        #7. Else, add 'no' to row['Stealth?']
        else:
            soho_row['Stealth?'] = 'no'
            soho.iloc[i] = soho_row

        csv_filename = output_path + 'stealth_soho_catalog_best_window_cont_{0}.csv'.format(Time.now().iso)
        soho.to_csv(csv_filename, header=True, index=False, mode='w')
        progress_bar_sliding_window.update(i)  # advance progress bar

    csv_filename = output_path + 'stealth_soho_catalog_best_window_cont_{0}.csv'.format(Time.now().iso)
    soho.to_csv(csv_filename, header=True, index=False, mode='w')
    print("Done!")


if __name__ == "__main__":
    print("DetectStealthCMEsInSOHO.py is being run directly")
    detectStealthCMEsInSOHO()

else:
    print("DetectStealthCMEsInSOHO.py is being imported into another module")
