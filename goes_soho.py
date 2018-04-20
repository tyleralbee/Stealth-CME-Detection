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

def goesSoho(output_path='/Users/tyleralbee/Desktop/StealthCME'):
    soho = pd.read_csv('/Users/tyleralbee/Desktop/Historical CME Data (SOHO).csv', index_col=0)
    print(soho.head())

    goes_data = readsav('/Users/tyleralbee/Desktop/GoesEventsMegsAEra.sav')


    #TODO:
    #1. Add new column to SOHO catalog named "Stealth?"
    sLength = len(soho['Time'])  # length of the SOHO catalog
    soho['Stealth?'] = pd.Series(np.nan, index=soho.index)  # add new column to the catalog

    csv_filename = output_path + 'stealthy_soho_{0}.csv'.format(Time.now().iso)
    # soho.to_csv(csv_filename, header=True, index=False, mode='w')

    csv_filename2 = output_path + 'stealthy_soho_2{0}.csv'.format(Time.now().iso)

    #2. Set up loop through SOHO catalog
    for i in range(0, int(sLength/500)):
        #3. For each row, pull date and time from row
        soho_row = soho.iloc[i]
        date = soho_row.name
        time = soho_row['Time']
        timeObj = pd.to_datetime(date + 'T' + time)

        #4. Convert that date/time to a sunpy.time.TimeRange (will need to decide how wide of a time window)
        time_range = TimeRange(timeObj - timedelta(hours=12), timeObj + timedelta(hours=12))
        #5. Send TimeRange to sunpy.instr.goes.get_goes_event_list(timerange, goes_class_filter=None)
        flares = sunpy.instr.goes.get_goes_event_list(time_range, goes_class_filter=None)
        print(flares)

        #6. If that returns an empty list, add 'yes' to row['Stealth?']

        if (len(flares) == 0):
            soho_row['Stealth?'] = 'yes'
            soho.iloc[i] = soho_row
            #7. Else, add 'no' to row['Stealth?']
        else:
            soho_row['Stealth?'] = 'no'
            soho.iloc[i] = soho_row

    soho.to_csv(csv_filename2, header=True, index=False, mode='w')


if __name__ == "__main__":
    print("goesSoho.py is being run directly")
    goesSoho()

else:
    print("goesSoho.py is being imported into another module")
