# Standard modules
import os
import itertools
from collections import OrderedDict
from datetime import timedelta

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
import sys

# Custom modules
from jpm_logger import JpmLogger
from jpm_number_printing import latex_float
# from get_goes_flare_events import get_goes_flare_events  # TODO: Uncomment once sunpy method implemented
from determine_preflare_irradiance import determine_preflare_irradiance
from light_curve_peak_match_subtract import light_curve_peak_match_subtract
from automatic_fit_light_curve import automatic_fit_light_curve
from determine_dimming_depth import determine_dimming_depth
from determine_dimming_slope import determine_dimming_slope
from determine_dimming_duration import determine_dimming_duration

__author__ = 'Shawn Polson and Tyler Albee'
__contact__ = 'shpo9723@colorado.edu'


def characterizeStealthCMEs(output_path='/Users/shawnpolson/Documents/School/Spring 2018/Data Mining/StealthCMEs/PyCharm/JEDI Catalog/',
                            eve_data='/Users/shawnpolson/Documents/School/Spring 2018/Data Mining/StealthCMEs/savesets/eve_selected_lines.csv',
                            soho_catalog_with_stealth_column='/Users/shawnpolson/Desktop/stealth_soho_catalog_best_window.csv',
                            verbose=True):

    """Wrapper code for generating the dimming depth, duration, and slope for stealth CME events.

    Inputs:
        output_path [str]:                                      Where to output everything
        eve_data [str]:                                         The preprocessed SDO EVE data
        soho_catalog_with_stealth_column [str]:                 The SOHO catalog with the much anticipated "Stealth?" column
        verbose [bool]:                                         Set to log the processing messages to disk and console. Default is False.

    Outputs:
        No direct return, but writes a (csv? sql table? hdf5?) to disk with the dimming paramerization results.
        Subroutines also optionally save processing plots to disk in output_path.

    Optional Outputs:
        None

    Example:
        characterize_stealth_cmes(verbose=True)

    """
    # Prepare the logger for verbose
    if verbose:
        logger = JpmLogger(filename='characterizing stealth cmes', path=output_path, console=True)
        logger.info("Starting CME characterization pipeline.")
    else:
        logger = None

#---------Load data sets------------------------------------------------------------------------------------------------

    # Get SOHO catalog with the "Stealth?" column
    stealth_soho_catalog = pd.read_csv(soho_catalog_with_stealth_column)

    # Get EVE level 2 extracted emission lines data
    # Load up the actual irradiance data into a pandas DataFrame
    # Declare that column 0 is the index then convert it to datetime
    eve_lines = pd.read_csv(eve_data, index_col=0)
    eve_lines.index = pd.to_datetime(eve_lines.index)
    print(eve_lines.info)

    if verbose:
        logger.info('Loaded EVE data')

    # Define the columns of the JEDI catalog
    jedi_row = pd.DataFrame([OrderedDict([
                             ('Event #', np.nan),
                             ('Start Time', np.nan),
                             ('End Time', np.nan),
                             ('GOES Flare Class', np.nan),
                             ('Pre-Flare Start Time', np.nan),
                             ('Pre-Flare End Time', np.nan),
                             ('Flare Interrupt', np.nan)])])
    jedi_row = jedi_row.join(pd.DataFrame(columns=eve_lines.columns + ' Pre-Flare Irradiance [W/m2]'))
    jedi_row = jedi_row.join(pd.DataFrame(columns=eve_lines.columns + ' Slope Start Time'))
    jedi_row = jedi_row.join(pd.DataFrame(columns=eve_lines.columns + ' Slope End Time'))
    jedi_row = jedi_row.join(pd.DataFrame(columns=eve_lines.columns + ' Slope Min [%/s]'))
    jedi_row = jedi_row.join(pd.DataFrame(columns=eve_lines.columns + ' Slope Max [%/s]'))
    jedi_row = jedi_row.join(pd.DataFrame(columns=eve_lines.columns + ' Slope Mean [%/s]'))
    jedi_row = jedi_row.join(pd.DataFrame(columns=eve_lines.columns + ' Slope Uncertainty [%/s]'))
    jedi_row = jedi_row.join(pd.DataFrame(columns=eve_lines.columns + ' Depth Time'))
    jedi_row = jedi_row.join(pd.DataFrame(columns=eve_lines.columns + ' Depth [%]'))
    jedi_row = jedi_row.join(pd.DataFrame(columns=eve_lines.columns + ' Depth Uncertainty [%]'))
    jedi_row = jedi_row.join(pd.DataFrame(columns=eve_lines.columns + ' Duration Start Time'))
    jedi_row = jedi_row.join(pd.DataFrame(columns=eve_lines.columns + ' Duration End Time'))
    jedi_row = jedi_row.join(pd.DataFrame(columns=eve_lines.columns + ' Duration [s]'))
    jedi_row = jedi_row.join(pd.DataFrame(columns=eve_lines.columns + ' Fitting Gamma'))
    jedi_row = jedi_row.join(pd.DataFrame(columns=eve_lines.columns + ' Fitting Score'))

    ion_tuples = list(itertools.permutations(eve_lines.columns.values, 2))
    ion_permutations = pd.Index([' by '.join(ion_tuples[i]) for i in range(len(ion_tuples))])

    jedi_row = jedi_row.join(pd.DataFrame(columns=ion_permutations + ' Slope Start Time'))
    jedi_row = jedi_row.join(pd.DataFrame(columns=ion_permutations + ' Slope End Time'))
    jedi_row = jedi_row.join(pd.DataFrame(columns=ion_permutations + ' Slope Min [%/s]'))
    jedi_row = jedi_row.join(pd.DataFrame(columns=ion_permutations + ' Slope Max [%/s]'))
    jedi_row = jedi_row.join(pd.DataFrame(columns=ion_permutations + ' Slope Mean [%/s]'))
    jedi_row = jedi_row.join(pd.DataFrame(columns=ion_permutations + ' Slope Uncertainty [%/s]'))
    jedi_row = jedi_row.join(pd.DataFrame(columns=ion_permutations + ' Depth Time'))
    jedi_row = jedi_row.join(pd.DataFrame(columns=ion_permutations + ' Depth [%]'))
    jedi_row = jedi_row.join(pd.DataFrame(columns=ion_permutations + ' Depth Uncertainty [%]'))
    jedi_row = jedi_row.join(pd.DataFrame(columns=ion_permutations + ' Duration Start Time'))
    jedi_row = jedi_row.join(pd.DataFrame(columns=ion_permutations + ' Duration End Time'))
    jedi_row = jedi_row.join(pd.DataFrame(columns=ion_permutations + ' Duration [s]'))
    jedi_row = jedi_row.join(pd.DataFrame(columns=ion_permutations + ' Correction Time Shift [s]'))
    jedi_row = jedi_row.join(pd.DataFrame(columns=ion_permutations + ' Correction Scale Factor'))
    jedi_row = jedi_row.join(pd.DataFrame(columns=ion_permutations + ' Fitting Gamma'))
    jedi_row = jedi_row.join(pd.DataFrame(columns=ion_permutations + ' Fitting Score'))

    csv_filename = output_path + 'stealth_cme_characterization_{0}.csv'.format(Time.now().iso)
    jedi_row.to_csv(csv_filename, header=True, index=False, mode='w')

    if verbose:
        logger.info('Created Stealth CME Characterization table definition.')

    # Start a progress bar
    widgets = [progressbar.Percentage(), progressbar.Bar(), progressbar.Timer(), ' ', progressbar.AdaptiveETA()]

    # Prepare a hold-over pre-flare irradiance value,
    # which will normally have one element for each of the 39 emission lines
    preflare_irradiance = np.nan

    # Start loop through all flares
    for t in range(0, len(stealth_soho_catalog)):

        #----------Check if this row is a stealth CME-------------------------------------------------------------------

        soho_row = stealth_soho_catalog.iloc[i]
        if not soho_row['Stealth?'] == 'yes':
            continue  # Don't characterize the CME in this row because it's not a stealth CME

        #----------Clip dataset to stealth CME event window-------------------------------------------------------------

        date = soho_row['Date']
        time = soho_row['Time']
        dateTime = pd.to_datetime(date + 'T' + time)

        # Get only rows in our dimming window
        startTime = dateTime - timedelta(hours=1.5)  #These values may be adjusted
        endTime = dateTime + timedelta(hours=4)      #These values may be adjusted
        eve_lines_event = eve_lines.loc[(eve_lines.index >= startTime) & (eve_lines.index <= endTime)]  # this syntax is more forgiving than "eve_lines[startTime:endTime]"
        #print(eve_lines_event.head)

        if verbose:
            logger.info('Sliced rows in dimming window time range: ' + startTime + ' -> ' + endTime)
            logger.info("Event {0} EVE data clipped to dimming window.".format(t))

        # Fill the event information into the JEDI row
        jedi_row['Event #'] = t
        jedi_row['Start Time'] = startTime
        jedi_row['End Time'] = endTime
        if verbose:
            logger.info("Event {0} details stored to JEDI row.".format(t))

        #---------Convert irradiance values to percentages--------------------------------------------------------------

        # Convert irradiance units to percent
        # (in place, don't care about absolute units from this point forward)
        # Note: "preflare_irradiance" is pandas series with columns for each line and just one irradiance (float) per column
        preflare_irradiance = eve_lines_event.iloc[0]
        eve_lines_event_percentages = (eve_lines_event - preflare_irradiance) / preflare_irradiance * 100.0

        if verbose:
            logger.info("Event {0} irradiance converted from absolute to percent units.".format(1))

        #---------Fit light curves to reduce noise----------------------------------------------------------------------

        # Fit the light curves to reduce influence of noise on the parameterizations to come later
        uncertainty = np.ones(len(eve_lines_event_percentages)) * 0.002545  # got this line from James's code

        progress_bar_fitting = progressbar.ProgressBar(widgets=[progressbar.FormatLabel('Light curve fitting: ')] + widgets,
                                                       max_value=len(eve_lines_event_percentages.columns)).start()
        for i, column in enumerate(eve_lines_event_percentages):
            if eve_lines_event_percentages[column].isnull().all().all():
                if verbose:
                    logger.info(
                        'Event {0} {1} fitting skipped because all irradiances are NaN.'.format(t, column))
            else:
                eve_line_event_percentages = pd.DataFrame(eve_lines_event_percentages[column])
                eve_line_event_percentages.columns = ['irradiance']
                eve_line_event_percentages['uncertainty'] = uncertainty

                fitting_path = output_path + 'Fitting/'
                if not os.path.exists(fitting_path):
                    os.makedirs(fitting_path)

                plt.close('all')
                light_curve_fit, best_fit_gamma, best_fit_score = automatic_fit_light_curve(eve_line_event_percentages,
                                                                                            plots_save_path='{0} Event {1} {2} '.format(
                                                                                                fitting_path, t,
                                                                                                column),
                                                                                            verbose=verbose, logger=logger)
                eve_lines_event_percentages[column] = light_curve_fit
                jedi_row[column + ' Fitting Gamma'] = best_fit_gamma
                jedi_row[column + ' Fitting Score'] = best_fit_score

                if verbose:
                    logger.info('Event {0} {1} light curves fitted.'.format(t, column))
                progress_bar_fitting.update(i)

        progress_bar_fitting.finish()

        if verbose:
            logger.info('Light curves fitted')

        #---------Determine dimming characteristics---------------------------------------------------------------------

        eve_lines_event = eve_lines_event_percentages  # use the same variable name as James for consistency
        eve_lines_event.to_csv(output_path + 'eve_lines_event_percents_fitted.csv')

        # Parameterize the light curves for dimming
        for column in eve_lines_event:

            # Null out all parameters
            depth_percent, depth_time = np.nan, np.nan
            slope_start_time, slope_end_time = np.nan, np.nan
            slope_min, slope_max, slope_mean = np.nan, np.nan, np.nan
            duration_seconds, duration_start_time, duration_end_time = np.nan, np.nan, np.nan

            # Determine whether to do the parameterizations or not
            if eve_lines_event[column].isnull().all().all():
                if verbose:
                    logger.info(
                        'Event {0} {1} parameterization skipped because all irradiances are NaN.'.format(t, column))
            else:
                eve_line_event = pd.DataFrame(eve_lines_event[column])
                eve_line_event.columns = ['irradiance']

                # Determine dimming depth (if any)
                depth_path = output_path + 'Depth/'
                if not os.path.exists(depth_path):
                    os.makedirs(depth_path)

                plt.close('all')
                # Call to "determine_dimming_depth()"
                depth_percent, depth_time = determine_dimming_depth(eve_line_event,
                                                                    plot_path_filename='{0} Event {1} {2} Depth.png'.format(
                                                                        depth_path, t, column),
                                                                    verbose=verbose, logger=logger)

                jedi_row[column + ' Depth [%]'] = depth_percent
                jedi_row[column + ' Depth Time'] = depth_time

                # Determine dimming slope (if any)
                slope_path = output_path + 'Slope/'
                if not os.path.exists(slope_path):
                    os.makedirs(slope_path)

                slope_start_time = startTime
                slope_end_time = depth_time

                if (pd.isnull(slope_start_time)) or (pd.isnull(slope_end_time)):
                    if verbose:
                        logger.warning('Cannot compute slope or duration because slope bounding times NaN.')
                else:
                    plt.close('all')
                    # Call to "determine_dimming_slope()"
                    slope_min, slope_max, slope_mean = determine_dimming_slope(eve_line_event,
                                                                               earliest_allowed_time=slope_start_time,
                                                                               latest_allowed_time=slope_end_time,
                                                                               plot_path_filename='{0} Event {1} {2} Slope.png'.format(
                                                                                   slope_path, t, column),
                                                                               verbose=verbose, logger=logger)

                    jedi_row[column + ' Slope Min [%/s]'] = slope_min
                    jedi_row[column + ' Slope Max [%/s]'] = slope_max
                    jedi_row[column + ' Slope Mean [%/s]'] = slope_mean
                    jedi_row[column + ' Slope Start Time'] = slope_start_time
                    jedi_row[column + ' Slope End Time'] = slope_end_time

                    # Determine dimming duration (if any)
                    duration_path = output_path + 'Duration/'
                    if not os.path.exists(duration_path):
                        os.makedirs(duration_path)

                    plt.close('all')
                    # Call to "determine_dimming_duration()"
                    duration_seconds, duration_start_time, duration_end_time = determine_dimming_duration(eve_line_event,
                                                                                                          earliest_allowed_time=slope_start_time,
                                                                                                          plot_path_filename='{0} Event {1} {2} Duration.png'.format(
                                                                                                              duration_path,
                                                                                                              t,
                                                                                                              column),
                                                                                                          verbose=verbose,
                                                                                                          logger=logger)

                    jedi_row[column + ' Duration [s]'] = duration_seconds
                    jedi_row[column + ' Duration Start Time'] = duration_start_time
                    jedi_row[column + ' Duration End Time'] = duration_end_time

                if verbose:
                    logger.info("Event {0} {1} parameterizations complete.".format(t, column))

                #----------Plot everything------------------------------------------------------------------------------

                # Produce a summary plot for each light curve
                plt.style.use('jpm-transparent-light')

                ax = eve_line_event['irradiance'].plot(color='black')
                plt.axhline(linestyle='dashed', color='grey')
                start_date = eve_line_event.index.values[0]
                start_date_string = pd.to_datetime(str(start_date))
                plt.xlabel(start_date_string.strftime('%Y-%m-%d %H:%M:%S'))
                plt.ylabel('Irradiance [%]')
                fmtr = dates.DateFormatter("%H:%M:%S")
                ax.xaxis.set_major_formatter(fmtr)
                ax.xaxis.set_major_locator(dates.HourLocator())
                plt.title('Event {0} {1} nm Parameters'.format(t, column))

                if not np.isnan(depth_percent):
                    plt.annotate('', xy=(depth_time, -depth_percent), xycoords='data',
                                 xytext=(depth_time, 0), textcoords='data',
                                 arrowprops=dict(facecolor='limegreen', edgecolor='limegreen', linewidth=2))
                    mid_depth = -depth_percent / 2.0
                    plt.annotate('{0:.2f} %'.format(depth_percent), xy=(depth_time, mid_depth), xycoords='data',
                                 ha='right', va='center', rotation=90, size=18, color='limegreen')

                if not np.isnan(slope_mean):
                    if pd.isnull(slope_start_time) or pd.isnull(slope_end_time):
                        import pdb
                        pdb.set_trace()
                    p = plt.plot(eve_line_event[slope_start_time:slope_end_time]['irradiance'], c='tomato')

                    inverse_str = '$^{-1}$'
                    plt.annotate('slope_min={0} % s{1}'.format(latex_float(slope_min), inverse_str),
                                 xy=(0.98, 0.12), xycoords='axes fraction', ha='right',
                                 size=12, color=p[0].get_color())
                    plt.annotate('slope_max={0} % s{1}'.format(latex_float(slope_max), inverse_str),
                                 xy=(0.98, 0.08), xycoords='axes fraction', ha='right',
                                 size=12, color=p[0].get_color())
                    plt.annotate('slope_mean={0} % s{1}'.format(latex_float(slope_mean), inverse_str),
                                 xy=(0.98, 0.04), xycoords='axes fraction', ha='right',
                                 size=12, color=p[0].get_color())

                if not np.isnan(duration_seconds):
                    plt.annotate('', xy=(duration_start_time, 0), xycoords='data',
                                 xytext=(duration_end_time, 0), textcoords='data',
                                 arrowprops=dict(facecolor='dodgerblue', edgecolor='dodgerblue', linewidth=5,
                                                 arrowstyle='<->'))
                    mid_time = duration_start_time + (duration_end_time - duration_start_time) / 2
                    plt.annotate(str(duration_seconds) + ' s', xy=(mid_time, 0), xycoords='data', ha='center', va='bottom',
                                 size=18, color='dodgerblue')

                summary_path = output_path + 'Summary Plots/'
                if not os.path.exists(summary_path):
                    os.makedirs(summary_path)
                summary_filename = '{0} Event {1} {2} Parameter Summary.png'.format(summary_path, t, column)
                plt.savefig(summary_filename)
                if verbose:
                    logger.info("Summary plot saved to %s" % summary_filename)


        #---------Output results----------------------------------------------------------------------------------------

        # Write to the JEDI catalog on disk
        jedi_row.to_csv(csv_filename, header=False, index=False, mode='a')
        if verbose:
            logger.info('Event {0} JEDI row written to {1}.'.format(t, csv_filename))


if __name__ == '__main__':
    characterizeStealthCMEs(verbose=True)
