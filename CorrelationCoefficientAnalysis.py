# Standard modules
import os
import itertools
from collections import OrderedDict
import numpy as np
import matplotlib as mpl
mpl.use('TkAgg') #used to be mpl.use('macosx')
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as dates
import astropy.units as u
from astropy.time import Time
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


def correlationCoefficientScan(output_path='/Users/tyleralbee/Desktop/StealthCME', verbose=True):

    eve_lines = pd.read_csv('/Users/tyleralbee/Desktop/StealthCME/eve_selected_lines.csv', index_col=0)
    eve_lines.index = pd.to_datetime(eve_lines.index)
    wholeDfLength = eve_lines.__len__()

    cme_event = pd.read_csv('/Users/tyleralbee/Desktop/StealthCME/eve_lines_event_percents_fitted.csv', index_col=0)
    cme_event.index = pd.to_datetime(cme_event.index)
    cmeEventLength = cme_event.__len__()

    if verbose:
        logger = JpmLogger(filename='do_correlation_coefficient_scan', path=output_path, console=True)
        logger.info("Starting Stealth CME search pipeline!")
    else:
        logger = None

    if verbose:
        logger.info('Loaded EVE and CME data')

    # Define the columns of the output catalog
    output_table = pd.DataFrame(columns=['Event #', 'Start Time', 'End Time', 'Correlation Coefficient'])
    csv_filename = output_path + 'cc_output_{0}.csv'.format(Time.now().iso)
    output_table.to_csv(csv_filename, header=True, index=False, mode='w')

    if verbose:
        #logger.info('Created output row definition.')
        logger.info('Created output table definition.')

    # Start a progress bar
    widgets = [progressbar.Percentage(), progressbar.Bar(), progressbar.Timer(), ' ', progressbar.AdaptiveETA()]

    startRow = 0
    endRow = cmeEventLength
    numSlices = int(wholeDfLength/cmeEventLength)

    progress_bar_sliding_window = progressbar.ProgressBar(widgets=[progressbar.FormatLabel('Correlation Coefficient Analysis ')] + widgets,
                                                   max_value=numSlices).start()

    # ----------Loop through data set using a sliding time window-------------------------------------------------------

    for i in range(1, numSlices):

        # ----------Clip dataset to time slice window-------------------------------------------------------------------

        event_time_slice = eve_lines.iloc[startRow:endRow]

        # ---------Convert irradiance values to percentages-------------------------------------------------------------

        preflare_irradiance = event_time_slice.iloc[0]
        event_time_slice_percentages = (event_time_slice - preflare_irradiance) / preflare_irradiance * 100.0

        if verbose:
            logger.info("Event {0} irradiance converted from absolute to percent units.".format(i))

        # ---------Fit light curves to reduce noise---------------------------------------------------------------------

        uncertainty = np.ones(len(event_time_slice_percentages)) * 0.002545  # got this line from James's code

        progress_bar_fitting = progressbar.ProgressBar(
            widgets=[progressbar.FormatLabel('Light curve fitting: ')] + widgets,
            max_value=len(event_time_slice_percentages.columns)).start()

        for j, column in enumerate(event_time_slice_percentages):
            if event_time_slice_percentages[column].isnull().all().all():
                if verbose:
                    logger.info(
                        'Event {0} {1} fitting skipped because all irradiances are NaN.'.format(j, column))
            else:
                eve_line_event_percentages = pd.DataFrame(event_time_slice_percentages[column])
                eve_line_event_percentages.columns = ['irradiance']
                eve_line_event_percentages['uncertainty'] = uncertainty

                fitting_path = output_path + 'Fitting/'
                if not os.path.exists(fitting_path):
                    os.makedirs(fitting_path)

                plt.close('all')
                light_curve_fit, best_fit_gamma, best_fit_score = automatic_fit_light_curve(
                                                                    eve_line_event_percentages,
                                                                    plots_save_path='{0} Event {1} {2} '.format(
                                                                        fitting_path, j, column), verbose=verbose,
                                                                    logger=logger)
                event_time_slice_percentages[column] = light_curve_fit
                event_time_slice_fitted = event_time_slice_percentages  # Keep our variable names explicit

                if verbose:
                    logger.info('Event {0} {1} light curves fitted.'.format(j, column))
                progress_bar_fitting.update(j)

        progress_bar_fitting.finish()

        if verbose:
            logger.info("Event {0} Light curves fitted".format(i))

        # ---------Compute Correlation Coefficients---------------------------------------------------------------------

        totalCorrelationCoefficient = 0.0
        ds1 = event_time_slice_fitted
        ds2 = cme_event

        # Gather stats for correlation
        for k, column in enumerate(ds1):
            dsColumn1 = ds1[column]
            dsColumn2 = ds2[column]

            dsColumn1.reset_index(drop=True, inplace=True) # prevent NaNs from appearing in join
            dsColumn2.reset_index(drop=True, inplace=True) # prevent NaNs from appearing in join

            n = int(dsColumn1.count())  # TODO: assert that both columns have same count?
            meanA = float(dsColumn1.mean())
            meanB = float(dsColumn2.mean())
            stdA = float(dsColumn1.std(ddof=0))
            stdB = float(dsColumn2.std(ddof=0))

            # Generate correlation output
            dsJoined = pd.DataFrame({'a': dsColumn1, 'b': dsColumn2})  # Avoids ambiguity when attr names are the same
            numerator = 0.0  # Stores summation of (a_i - meanA)(b_i - meanB)
            denominator = n * stdA * stdB

            for index, row in dsJoined.iterrows():
                a = row['a']
                b = row['b']
                numerator = numerator + (a - meanA) * (b - meanB)

            correlationCoefficient = numerator / denominator
            totalCorrelationCoefficient = totalCorrelationCoefficient + correlationCoefficient

        # ---------Output Results---------------------------------------------------------------------------------------

        eventStartTime = event_time_slice.iloc[0].name
        eventEndTime = event_time_slice.iloc[-1].name

        if not math.isnan(totalCorrelationCoefficient):
            output_table.loc[i] = [i, eventStartTime, eventEndTime, totalCorrelationCoefficient]
            csv_filename = output_path + 'cc_output_{0}.csv'.format(Time.now().iso)
            output_table.to_csv(csv_filename, header=True, index=False, mode='w')

        startRow = startRow + 60  # advance time window by 1 hour
        endRow = endRow + 60      # advance time window by 1 hour
        progress_bar_sliding_window.update(i)  # advance progress bar





# def convertIrradiancesToPercents(event_time_slice):
#     preflare_irradiance = event_time_slice.iloc[0]
#     event_time_slice_percentages = (event_time_slice - preflare_irradiance) / preflare_irradiance * 100.0
#     event_time_slice = event_time_slice_percentages
#
#
# def fitLightCurves(eve_lines_event_time_slice):
#     print("Nothing")

# def computeCorrelationCoefficient(eve_lines_event_time_slice, cme_event):
#     totalCorrelationCoefficient = 0
#     ds1 = eve_lines_event_time_slice
#     ds2 = cme_event
#
#     # Gather stats for correlation
#     for i, column in enumerate(ds1):
#         dsColumn1 = ds1[column]
#         dsColumn2 = ds2[column]
#         n = int(dsColumn1.count())  # TODO: assert that both columns have same count?
#         meanA = float(dsColumn1.mean())
#         meanB = float(dsColumn2.mean())
#         stdA = float(dsColumn1.std(ddof=0))
#         stdB = float(dsColumn2.std(ddof=0))
#
#         # Generate correlation output
#         dsJoined = pd.concat([dsColumn1, dsColumn2], axis=1)
#         dsJoined.columns = ['a', 'b']  # Avoids ambiguity when both attribute names are the same
#         numerator = 0.0  # Stores summation of (a_i - meanA)(b_i - meanB)
#         denominator = n * stdA * stdB
#
#         for index, row in dsJoined.iterrows():
#             a = row['a']
#             b = row['b']
#             numerator = numerator + (a - meanA) * (b - meanB)
#
#         correlationCoefficient = numerator / denominator
#         totalCorrelationCoefficient = totalCorrelationCoefficient + correlationCoefficient
#
#     print(totalCorrelationCoefficient)



if __name__ == "__main__":
    print("CorrelationCoefficientAnalysis.py is being run directly")
    correlationCoefficientScan(verbose=True)

else:
    print("CorrelationCoefficientAnalysis.py is being imported into another module")
