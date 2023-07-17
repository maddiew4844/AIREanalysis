#!/usr/bin/env python

""" Airthings graph

Python script to analyze and display airthings data from the AIRE study. This script 1. Pulls airthigns data from all
participants recorded in the Qualtrics AIRE data log, 2. calculates summary statistics for desired environmental
variables, 3. creates creates Excel summary statistics file, and creates graphical displays of the results.

This script requires that ???? be installed within the environment.

Author: Madeleine Wallace
Last updated: 07/13/23
"""

import pandas as pd
import os
import matplotlib.pyplot as plt

import requests
import zipfile
import io, os
import sys
import re
import pandas
import logging
from colorama import init, Fore, Style
from datetime import datetime, timedelta
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# Initialize colorama
init()

class ColoredFormatter(logging.Formatter):
    COLORS = {
        'DEBUG': Style.DIM + Fore.BLUE,
        'INFO': Style.NORMAL + Fore.GREEN,
        'WARNING': Style.NORMAL + Fore.YELLOW,
        'ERROR': Style.NORMAL + Fore.RED,
        'CRITICAL': Style.BRIGHT + Fore.RED
    }

    def format(self, record):
        levelname = record.levelname
        msg = super().format(record)
        color = self.COLORS.get(levelname, '')
        return color + msg + Style.RESET_ALL

def main():
    """The main function 1. sets up logging, 2. downloads the data log from Qualtrics, 3. parses out the participant
    groupNO, airthings_id, and date times for each period, 4. pulls airthings data via the API 5.
    """

    logger = setup_logging()  # Set up error logger.

    # data_log_loc = surveyExportPrep(logger)
    data_log_loc = "/Users/maddiewallace/PycharmProjects/AIREanalysis/MyQualtricsDownload2/AIRE_data_log.csv"

    # Create a list of all unique participant IDs in order.
    part_id_list, data_log_df, part_id_dict = create_part_id_list(data_log_loc)

    # Initialize dictionary to store the participant IDs as keys, their date_dict, group_assignment, and data.
    participant_data = {}

    # Cycle through all the participants, filling the participant_data dictionary with the groupNO, date dict, airthings
    # device ID, and airthings data.
    for part_id in part_id_list:

        date_dict, GroupNO, airthings_id = pull_group_and_dates(data_log_df, part_id_dict, part_id)

        # Convert visits dates to datetime objects and adds the start date for the intervention and follow-up periods.
        date_dict = convert_visit_date(date_dict, part_id)

        # Convert the GroupNO distinctions from 1, 2, or 3 to A, B, or C
        GroupNO = convert_GroupNO(GroupNO)

        # Authorize and Airthings devices via API
        access_token = airthings_auth()
        airthings_devices = get_airthings_devices(access_token)

        # Create a dictionary of all Space Pro SNs from the current device names.
        SN_dict = create_SN_dict(airthings_devices)

        # Pull the airthings data for the requested participant for the requested time frame.
        data_df = pull_airthings_data(part_id, access_token, airthings_id, SN_dict, date_dict, logger)

        # Fill participant_data dictionary with all the info from the participant.
        participant_data = fill_participant_data(participant_data, part_id, date_dict, GroupNO, airthings_id, data_df)

        # Set of simple sample data to use for development.
        participant_data = {
            'A001': {
                'date_dict': {
                    '1': datetime(2023, 3, 23, 14, 45),
                    '2': datetime(2023, 4, 7, 10, 10),
                    '3': datetime(2023, 4, 24, 16, 0),
                    '4': datetime(2023, 7, 11, 12, 50, 10),
                    '2B': datetime(2023, 4, 7, 10, 11),
                    '3B': datetime(2023, 4, 24, 16, 1)
                },
                'GroupNO': 'A',
                'airthings_id': 'A01',
                'data': pandas.DataFrame({
                    'time': pd.to_datetime(
                        ['2023-03-23 19:00:00', '2023-03-23 23:00:00', '2023-03-24 21:00:00', '2023-03-25 22:00:00',
                         '2023-03-25 23:00:00']),
                    'co2': [753.0, 757.0, 742.0, np.nan, 750.0],
                    'humidity': [35.0, 36.0, 37.0, 37.0, np.nan],
                    'light': [23, 29, np.nan, 16, 13],
                    'pressure': [np.nan, 1003.6, 1002.5, 1002.4, 1002.2],
                    'sla': [54.0, 48.0, np.nan, 49.0, 49.0],
                    'temp': [22.2, 22.1, 22.0, np.nan, 21.9],
                    'voc': [49.0, 49.0, np.nan, 53.0, 59.0],
                    'pm25': [10, 15, 8, np.nan, 22],
                    'pm1': [30, 10, 8, np.nan, 50]
                }),
            },
            'A002': {
                'date_dict': {
                    '1': datetime(2023, 3, 27, 15, 0),
                    '2': datetime(2023, 4, 14, 14, 0),
                    '3': datetime(2023, 4, 28, 9, 0),
                    '4': datetime(2023, 7, 11, 12, 50, 11),
                    '2B': datetime(2023, 4, 14, 14, 1),
                    '3B': datetime(2023, 4, 28, 9, 1)
                },
                'GroupNO': 'A',
                'airthings_id': 'A02',
                'data': pandas.DataFrame({
                    'time': pd.to_datetime(
                        ['2023-03-23 19:00:00', '2023-03-23 20:00:00', '2023-03-23 21:00:00', '2023-03-23 22:00:00',
                         '2023-03-24 19:00:00']),
                    'co2': [802.0, 789.0, 772.0, 942.0, 965.0],
                    'humidity': [30.0, 31.0, 31.0, 32.0, 35.0],
                    'light': [39, 35, 28, 14, 31],
                    'pressure': [1015.3, 1015.0, 1014.6, 1015.3, 1015.2],
                    'sla': [44.0, 49.0, 51.0, 54.0, 43.0],
                    'temp': [22.5, 22.3, 22.2, 22.1, 22.1],
                    'voc': [46.0, 57.0, 48.0, 50.0, 56.0],
                    'pm25': [12, 9, 18, 6, 20],
                    'pm1': [90, 10, 20, np.nan, 80]
                }),
            },
            'A003': {
                'date_dict': {
                    '1': datetime(2023, 3, 28, 13, 0),
                    '2': datetime(2023, 4, 10, 12, 0),
                    '3': datetime(2023, 4, 28, 14, 0),
                    '4': datetime(2023, 7, 11, 12, 50, 12),
                    '2B': datetime(2023, 4, 10, 12, 1),
                    '3B': datetime(2023, 4, 28, 14, 1)
                },
                'GroupNO': 'B',
                'airthings_id': 'A03',
                'data': pandas.DataFrame({
                    'time': pd.to_datetime(
                        ['2023-03-28 17:00:00', '2023-03-29 18:00:00', '2023-03-29 19:00:00', '2023-03-30 20:00:00',
                         '2023-03-31 21:00:00']),
                    'co2': [725.0, 708.0, 654.0, 650.0, 638.0],
                    'humidity': [32.0, 33.0, 34.0, 34.0, 34.0],
                    'light': [42, 41, 44, 36, 35],
                    'pressure': [1016.1, 1015.8, 1015.2, 1015.0, 1015.0],
                    'sla': [51.0, 42.0, 41.0, 42.0, 42.0],
                    'temp': [20.6, 19.5, 19.6, 19.5, 19.5],
                    'voc': [46.0, 54.0, 68.0, 59.0, 55.0],
                    'pm25': [5, 7, 6, 3, 9],
                    'pm1': [60, 100, 8, np.nan, 25]
                }),
            },
            'A004': {
                'date_dict': {
                    '1': datetime(2023, 3, 28, 13, 0),
                    '2': datetime(2023, 4, 10, 12, 0),
                    '3': datetime(2023, 4, 28, 14, 0),
                    '4': datetime(2023, 7, 11, 12, 50, 12),
                    '2B': datetime(2023, 4, 10, 12, 1),
                    '3B': datetime(2023, 4, 28, 14, 1)
                },
                'GroupNO': 'C',
                'airthings_id': 'A03',
                'data': pandas.DataFrame({
                    'time': pd.to_datetime(
                        ['2023-03-28 17:00:00', '2023-03-28 18:00:00', '2023-03-28 19:00:00', '2023-03-28 20:00:00',
                         '2023-03-28 21:00:00']),
                    'co2': [750.0, 730.0, 650.0, 650.0, 700.0],
                    'humidity': [32.0, 33.0, 34.0, 34.0, 34.0],
                    'light': [42, 41, 44, 36, 35],
                    'pressure': [1016.1, 1015.8, 1015.2, 1015.0, 1015.0],
                    'sla': [51.0, 42.0, 41.0, 42.0, 42.0],
                    'temp': [20.6, 19.5, 19.6, 19.5, 19.5],
                    'voc': [46.0, 54.0, 68.0, 59.0, 55.0],
                    'pm25': [5, 7, 15, 3, 12],
                    'pm1': [30, 10, 8, np.nan, 50]
                }),
            },
            'A005': {
                'date_dict': {
                    '1': datetime(2023, 3, 28, 13, 0),
                    '2': datetime(2023, 4, 10, 12, 0),
                    '3': datetime(2023, 4, 28, 14, 0),
                    '4': datetime(2023, 7, 11, 12, 50, 12),
                    '2B': datetime(2023, 4, 10, 12, 1),
                    '3B': datetime(2023, 4, 28, 14, 1)
                },
                'GroupNO': 'C',
                'airthings_id': 'A03',
                'data': pandas.DataFrame({
                    'time': pd.to_datetime(
                        ['2023-03-28 17:00:00', '2023-03-28 18:00:00', '2023-03-28 19:00:00', '2023-03-28 20:00:00',
                         '2023-03-28 21:00:00']),
                    'co2': [725.0, 708.0, 654.0, 650.0, 638.0],
                    'humidity': [32.0, 33.0, 34.0, 34.0, 34.0],
                    'light': [42, 41, 44, 36, 35],
                    'pressure': [1016.1, 1015.8, 1015.2, 1015.0, 1015.0],
                    'sla': [51.0, 42.0, 41.0, 42.0, 42.0],
                    'temp': [20.6, 19.5, 19.6, 19.5, 19.5],
                    'voc': [46.0, 54.0, 68.0, 59.0, 55.0],
                    'pm25': [5, 7, 6, 3, 9],
                    'pm1': [30, 35, 90, np.nan, 80]
                }),
            },
            'A006': {
                'date_dict': {
                    '1': datetime(2023, 3, 23, 14, 45),
                    '2': datetime(2023, 4, 7, 10, 10),
                    '3': datetime(2023, 4, 24, 16, 0),
                    '4': datetime(2023, 7, 11, 12, 50, 10),
                    '2B': datetime(2023, 4, 7, 10, 11),
                    '3B': datetime(2023, 4, 24, 16, 1)
                },
                'GroupNO': 'B',
                'airthings_id': 'A01',
                'data': pandas.DataFrame({
                    'time': pd.to_datetime(
                        ['2023-03-23 19:00:00', '2023-03-24 20:00:00', '2023-03-25 21:00:00', '2023-03-25 22:00:00',
                         '2023-03-26 23:00:00']),
                    'co2': [753.0, 757.0, 742.0, 751.0, 750.0],
                    'humidity': [35.0, 36.0, 37.0, 37.0, 37.0],
                    'light': [23, 29, 22, 16, 13],
                    'pressure': [1004.4, 1003.6, 1002.5, 1002.4, 1002.2],
                    'sla': [54.0, 48.0, 48.0, 49.0, 49.0],
                    'temp': [22.2, 22.1, 22.0, 22.0, 21.9],
                    'voc': [49.0, 49.0, 55.0, 53.0, 59.0],
                    'pm25': [10, 15, 8, 5, 22],
                    'pm1': [70, 20, 70, np.nan, 50]
                }),
            },

        }

    # Define the pastel color palette
    colors = sns.color_palette('pastel')[1:5]
    # Define legend elements
    legend_elements = [plt.bar(0, 0, color=color, label=label) for label, color in
                       zip(['Group A', 'Group B', 'Group C', 'Overall'], colors)]

    #Create 3 lists, containing all participant IDs for participants of each educational group.
    educational_groups = group_lists(participant_data)

    # Location to save graphs.
    graph_location = "/Users/maddiewallace/PycharmProjects/AIREanalysis/graph_outputs"

    # List of all the environmental variables that we wish to examine.
    # Choices: 'co2', 'humidity', 'light', 'pressure', 'sla', 'temp', 'voc', or 'pm25'
    environ_var_list = ['co2', 'pm25']

    # Calculate the summary statistics and create graphs for the desired environmental variables.
    for environ_var in environ_var_list:
        # Calculate pm25 summary stats (percentiles, max, mean, % above 12) for each participant individually, for all
        # participants combined, and for each group (A, B, C) combined. Add them to participant_data under the key
        # 'summary_stats'.
        participant_data, data_groups = prep_summary_stats(participant_data, environ_var, environ_var_list)

        # graph_group_timeseries(participant_data, educational_groups, data_groups.keys(), environ_var, graph_location)
        # plot_summaries(participant_data, legend_elements, graph_location)
        # plot_box_whisker(participant_data, legend_elements, graph_location)
        print(participant_data)

    return

def setup_logging():
    """Sets up logging configuration, displaying DEBUG to CRITICAL messages in various colors.

    Returns:
        logger (logging.Logger): The logger object used for logging messages.
    """
    logging.basicConfig(filename='air_quality.log', level=logging.DEBUG) # Set up logging configuration

    logger = logging.getLogger() # Create logger object

    # Create console handler and set the formatter to the custom formatter
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(
        ColoredFormatter(fmt='%(asctime)s %(levelname)s: %(message)s', datefmt='%Y-%m-%d %H:%M:%S'))

    console_handler.setLevel(logging.INFO) # Set console handler log level

    logger.addHandler(console_handler) # Add console handler to logger object

    return logger

def surveyExportPrep(logger):
    """Ensures that all necessary information has been entered in order to download the Qualtrics data log.

    Args:
        logger (logging.Logger): The logger object used for logging messages.

    Returns:
        data_log_loc (str) : the location of the downloaded Qualtrics survey data.
    """

    # IDs for access to Qualtrics AIRE data log survey.
    apiToken = "kpPRpAhkIOQM5pLLaMvazhZZ6zFu9bIED0TyTVxp"
    dataCenter = "sjc1"
    surveyId = "SV_3dDF6dhdbgb81Ho"
    fileFormat = "csv"

    # Confirms proper file format.
    if fileFormat not in ["csv", "tsv", "spss"]:
        logging.error('fileFormat must be either csv, tsv, or spss')
        sys.exit(2)

    # Confirms survey ID.
    r = re.compile('^SV_.*')
    m = r.match(surveyId)
    if not m:
        logging.error("survey Id must match ^SV_.*")
        sys.exit(2)

    # Exports survey to local device.
    data_log_loc = exportSurvey(apiToken, surveyId, dataCenter, fileFormat, logger)

    return data_log_loc

def exportSurvey(apiToken, surveyId, dataCenter, fileFormat, logger):
    """Exports Qualtrics 'AIRE data log survey' which contains the sensor_ID, groupNO, and data collection period dates.
    Code copied from https://api.qualtrics.com/ZG9jOjg3NzY3MA-getting-survey-responses-via-the-new-export-ap-is.
    Args:
        apiToken (str) : ID for accessing Qualtrics account, found online.
        surveyId (str) : ID for Qualtrics 'AIRE data log survey'.
        dataCenter (str) : ID for Qualtrics organization, found online.
        fileFormat (str) : format for outputted Qualtrics data file.
        logger (logging.Logger): The logger object used for logging messages.

    Returns:
        data_log_loc (str) : the location of the downloaded Qualtrics survey data.

    """

    surveyId = surveyId
    fileFormat = fileFormat
    dataCenter = dataCenter

    # Setting static parameters
    requestCheckProgress = 0.0
    progressStatus = "inProgress"
    baseUrl = "https://{0}.qualtrics.com/API/v3/surveys/{1}/export-responses/".format(dataCenter, surveyId)
    headers = {
        "content-type": "application/json",
        "x-api-token": apiToken,
    }

    # Step 1: Creating Data Export
    downloadRequestUrl = baseUrl
    downloadRequestPayload = '{"format":"' + fileFormat + '"}'
    downloadRequestResponse = requests.request("POST", downloadRequestUrl, data=downloadRequestPayload, headers=headers)
    progressId = downloadRequestResponse.json()["result"]["progressId"]
    logger.info(downloadRequestResponse.text)

    # Step 2: Checking on Data Export Progress and waiting until export is ready
    while progressStatus != "complete" and progressStatus != "failed":
        logger.info(progressStatus)
        requestCheckUrl = baseUrl + progressId
        requestCheckResponse = requests.request("GET", requestCheckUrl, headers=headers)
        requestCheckProgress = requestCheckResponse.json()["result"]["percentComplete"]
        logger.info("Download is " + str(requestCheckProgress) + " complete")
        progressStatus = requestCheckResponse.json()["result"]["status"]

    # step 2.1: Check for error
    if progressStatus == "failed":
        raise Exception("export failed")

    fileId = requestCheckResponse.json()["result"]["fileId"]

    # Step 3: Downloading file
    requestDownloadUrl = baseUrl + fileId + '/file'
    requestDownload = requests.request("GET", requestDownloadUrl, headers=headers, stream=True)

    # Step 4: Unzipping the file
    zip_name = "MyQualtricsDownload2"
    zipfile.ZipFile(io.BytesIO(requestDownload.content)).extractall(zip_name)

    # Inform the operator
    cdir = os.getcwd()
    data_log_loc = f'{cdir}/{zip_name}/AIRE_data_log.{fileFormat}'
    logger.info(f'Qualtrics download complete, {fileFormat} file located in: {data_log_loc}.')
    return data_log_loc

def create_part_id_list(data_log_loc):
    """Creates a dictionary of all the row number and corresponding participant IDs. Creates a list of all the unique
    participant IDs from the Qualtrics data log.

    Args:
        data_log_loc (str) : location of the Qualtrics data log file

    Returns:
        part_id_list (list) : list of all the unique participant IDs from the Qualtrics data log.
        data_log_df (df) : Qualtrics data log data.
    """

    data_log_df = pandas.read_csv(data_log_loc)

    # Place all participant IDs into a dictionary with the row number as the key. 'Q2' is the key for the Participant
    # ID# column.
    nested_dict = (data_log_df[['Q2']].to_dict())
    part_id_dict = nested_dict['Q2']

    # Remove non IDs, get unique values from the dictionary values, and sort in ascending order.
    part_id_dict = {k: v for k, v in part_id_dict.items() if
                    v not in ('Participant ID#', '{"ImportId":"QID2_TEXT"}', 'Participant ID# (ex: A014)')}
    unique_values = set(part_id_dict.values())
    part_id_list = sorted(unique_values)

    return part_id_list, data_log_df, part_id_dict

def pull_group_and_dates(data_log_df, part_id_dict, part_id):
    """Reads Qualtrics data log, pulling out the dates of each visit into a dict, as well as the GroupNO and
    airthings_id for the given participant.

    Args:
        data_log_df (df) : Qualtrics data log data.
        part_id_dict (dict) : row number as the key and participant ID as the value to locate all entries for a given
        participant.
        part_id (str) : the inputted participant ID.

    Returns:
        date_dict (dict) : dictionary of visit dates with visit number as the keys and the date as the value.
        GroupNO (str) : educational group assignment of the given participant (A, B, or C).
        airthings_id (str) : the airthings SpacePro ID for the given participant.
    """

    # Grab the visit dates from the data log for the inputted participant. Put the dates into a dict with the key as the
    # visit number and the value as the date.
    date_dict = {}
    for row_num in part_id_dict.keys():
        if part_id_dict[row_num] == part_id:
            visit_num = data_log_df.iloc[row_num]['Q4']
            visit_date = data_log_df.iloc[row_num]['Q1']
            visit_time = data_log_df.iloc[row_num]['Q1.1']

            date_dict[visit_num] = visit_date + ' ' + visit_time

            # Pull the GroupNO and airthings_id for the given participant, do not pull nan
            if pandas.isna(data_log_df.iloc[row_num]['V1.2']) == False:
                GroupNO = data_log_df.iloc[row_num]['V1.2']
            if pandas.isna(data_log_df.iloc[row_num]['V1.4a']) == False:
                airthings_id = data_log_df.iloc[row_num]['V1.4a']

    return date_dict, GroupNO, airthings_id

def convert_visit_date(date_dict, part_id):
    """Converts the date/times pulled from the Qualtrics data log into strings, and into datetime objects. Then adds
    the start date for the intervention and follow-up periods as needed by the R code.

    Args:
        date_dict (dict) : dictionary of visit dates with visit number as the keys and the date as the value.
        part_id (str) : the inputted participant ID.

    Returns:
        date_dict (dict) : dictionary of visit dates with the values now as datetime objects.
    """

    for key in date_dict.keys():
        if isinstance((date_dict[key]), list):
            date_dict[key] = ''.join(date_dict[key])
        try:
            # Try parsing the date string using the format '%m-%d-%Y %H:%M'
            date_dict[key] = datetime.strptime(date_dict[key], '%m-%d-%Y %H:%M')
        except ValueError:
            try:
                # If parsing with '%m-%d-%Y %H:%M' fails, try parsing with '%m/%d/%y %H:%M'
                date_dict[key] = datetime.strptime(date_dict[key], '%m/%d/%y %H:%M')
            except ValueError:
                # Handle the case when both formats fail
                logging.error(f"Invalid date format: {date_dict[key]}!")

    # Confirm that the given participant is not missing visits 1-3.
    for visit in ['1', '2', '3']:
        if visit not in date_dict.keys():
            logging.error(f"Participant {part_id} does not have a data log entry for visit {visit}. Please record this "
                          f"visit via Qualtrics before trying again.")
            exit()

    # Add the start date for the intervention and follow-up periods under the key {visit_num}B.
    for key in ['2', '3']:
        date_dict[f"{key}{'B'}"] = date_dict[key] + timedelta(minutes=1)

    # to download all data through today (except for A004 who did not keep their monitor):
    #TODO: automate choice of downloading through current date or through visit 4 or through visit 5.
    if part_id != "A004":
        date_dict['4'] = datetime.today().replace(microsecond=0)

    return date_dict

def convert_GroupNO(GroupNO):
    # Converts the GroupNO distinctions from 1, 2, or 3 to A, B, or C
    if GroupNO == "1":
        GroupNO = 'A'
    elif GroupNO == '2':
        GroupNO = 'B'
    elif GroupNO == '3':
        GroupNO = "C"

    return GroupNO

def airthings_auth():
    """Gets access token from the Airthings API client.

    Returns:
        access_token (str) : access token required for accessing Airthings data via the API.
    """

    client_id = "f785859c-cdfa-4a53-9822-e7533fbfafa1"
    client_secret = "a8d3cf6c-2f7e-4fbf-ac44-6decdf60454b"
    token_url = "https://accounts-api.airthings.com/v1/token"

    payload = {
        "grant_type": "client_credentials",
        "client_id": client_id,
        "client_secret": client_secret,
        "scope": "read:device"
    }

    response = requests.post(token_url, data=payload)
    response = response.json()

    access_token = response['access_token']

    return access_token

def get_airthings_devices(access_token):
    """Pulls the list of airthings devices from the Airthings API. This will be used to determine the serial numbers of
    the participant's airthings device.

    Args:
        access_token (str) : access token required for accessing Airthings data via the API.

    Returns:
        airthings_devices (dict) : API response for get devices request. All devices on Maddie's airthings account and
        their info.
    """

    url = "https://ext-api.airthings.com/v1/devices"
    headers = {
        "Authorization": f"Bearer {access_token}"
    }

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        airthings_devices = response.json()
    else:
        logging.error(f"Request failed with status code {response.status_code}")

    return airthings_devices

def create_SN_dict(airthings_devices):
    """Creates a dictionary with the given device name as the key and the serial number as the value. Needed for
    retrieving historical data from an individual sensor.

    Args:
        airthings_devices (dict) : API response for get devices request. All devices on Maddie's airthings account and
        their info.

    Returns:
        SN_dict (dict) : device name : serial number for all airthings Space Pro devices on Maddie's account.
    """

    SN_dict = {}

    # Cycle through all the device entries, if the device is the Space Pro (not a hub), add the ID and SN to the dict.
    for entry in airthings_devices['devices']:
        if entry['deviceType'] == 'VIEW_PLUS_BUSINESS':
            SN = entry['id']
            name = entry['segment']['name']
            SN_dict[name] = SN

    return SN_dict

def pull_airthings_data(part_id, access_token, airthings_id, SN_dict, date_dict, logger):
    """Pulls the airthings data for the given participant for their collection period.
    Args:
        part_id (str) : the inputted participant ID.
        access_token (str) : access token required for accessing Airthings data via the API.
        airthings_id (str) : the airthings SpacePro ID for the given participant.
        SN_dict (dict) : device name : serial number for all airthings Space Pro devices on Maddie's account.
        date_dict (dict) : dictionary of visit dates with the values now as datetime objects.
        logger (logging.Logger): The logger object used for logging messages.

    returns:
        data_df (df) : dataframe of all the data from the given participant

    """

    # Retrieves the proper SN given the airthings_id
    if airthings_id not in SN_dict.keys():
        logger.error(f"The entered airthings id {airthings_id} is not valid. Valid options for airthings IDs are: {SN_dict.keys()}")
    SN = SN_dict[airthings_id]

    # url and header for historical data request.
    url = f"https://ext-api.airthings.com/v1/devices/{SN}/samples"
    headers = {
        f"Authorization": f"Bearer {access_token}"
    }

    # Parameters for the request, including start and end times of the collection period and the resolution.
    params = {
        "start": int(date_dict['1'].timestamp()),
        "end": int(date_dict['4'].timestamp()),
        # resolution options: "HOUR" "FOUR_HOURS" "DAY" "THREE_DAYS" "WEEK"
        "resolution": "HOUR"
    }

    # Send the request.
    response = requests.get(url, headers=headers, params=params)

    # If successful, convert the response to a json then dataframe.
    if response.status_code == 200:
        data = response.json()
        data_df = pandas.DataFrame(data['data'])

        # Convert time column from ISO8601 to datetime objects
        data_df['time'] = pandas.to_datetime(data_df['time'], unit='s')

        # Convert data columns to numeric.
        for col in data_df.columns:
            if col != 'time':
                data_df[col] = pd.to_numeric(data_df[col], errors='coerce') # Convert all data columns (not the time col
                # to numeric data type)

        # Reorder the columns so that 'time' is the first column
        data_df = data_df.reindex(columns=['time'] + list(data_df.columns.drop('time')))

    else:
        logging.error(f"Get request for Airthings {airthings_id} for participant {part_id} failed with status code "
              f"{response.status_code}")

    return data_df

def fill_participant_data(participant_data, part_id, date_dict, GroupNO, airthings_id, data_df):
    """Fills the participant_data dictionary with all the info for the current participant.

    Args:
        participant_data (dict) : nested dictionary updated to contain participant IDs as keys, their date_dict, and
        group_assignment.
        date_dict (dict) : dictionary of visit dates with visit number as the keys and the date as the value.
        GroupNO (str) : educational group assignment of the given participant (A, B, or C).
        airthings_id (str) : the airthings SpacePro ID for the given participant.
        part_id (str) : participant ID
        data_df (df) : dataframe of all the data from the given participant

    returns:
        participant_data (dict) : nested dictionary updated to contain participant IDs as keys, their date_dict, and
        group_assignment.
    """

    # Add the part_id as a key in the participant_data dict with a nested info.
    participant_data[part_id] = {
        'date_dict': date_dict,
        'GroupNO': GroupNO,
        'airthings_id': airthings_id,
        'data': data_df,
    }

    # Assign a color based on the GroupNO.
    participant_data = assign_color(participant_data, part_id, GroupNO)

    return participant_data

def assign_color(participant_data, part_id, GroupNO):
    """Adds a color code based on the GroupNO of the participant.
    Args:
        participant_data (dict) : nested dictionary containing participant IDs as keys, their date_dict, and
        group_assignment.
        part_id (str) : participant ID
        GroupNO (str) : educational group assignment of the given participant (A, B, or C).

    Returns:
        participant_data (dict) : nested dictionary containing participant IDs as keys, their date_dict, and
        group_assignment. Now containing color assignment.
    """

    # Define the pastel color palette
    colors = sns.color_palette('pastel')[1:5]
    # Assign colors based on 'GroupNO' value
    if GroupNO == 'A':
        color = colors[0]
    elif GroupNO == 'B':
        color = colors[1]
    elif GroupNO == 'C':
        color = colors[2]
    else:
        color = colors[3]

    participant_data[part_id]['color'] = color

    return participant_data

def prep_summary_stats(participant_data, environ_var, environ_var_list):
    """ Preps for summary statistic (percentiles, max, mean, % above 12) calculations for environ_var. Calculations for
    each participant, all participants combined, and all participants of each group (A, B, C) combined.

    Args:
        participant_data (dict) : nested dictionary updated to contain participant IDs as keys, their date_dict, and
        group_assignment.
        environ_var (str) : the name of the environmental variable that we are currently looking at/calculating stats for.

    Returns:
        participant_data (dict) : nested dictionary updated to contain participant IDs as keys, their date_dict, and
        group_assignment. Now contains a nested summary statistics dictionary.
        data_groups (dict) : metadata for all participants combined, group A combined, group B combined, and group C
        combined.

    Raises:
        KeyError: If the "data" key is not present in participant_data or if the environ_var column is not present in the
        DataFrame.
    """

    # initialize a dict of lists to combine data from all participants, and from all participants of each group.
    data_groups = {
    'overall': [],
    'group_A': [],
    'group_B': [],
    'group_C': []
    }

    # Go through each individual participant, grab the data column, drop nan, and place it into the data_groups.
    for part_id in participant_data.keys():

        # If one of the combined groups, do not proceed as it will not contain the requested data key.
        if part_id in data_groups.keys():
            break

        data = participant_data[part_id]["data"]

        # Check if "data" key exists and is a DataFrame
        if not isinstance(data, pd.DataFrame):
            raise KeyError("'data' key must contain a DataFrame.")

        # Check if environ_var column exists in the DataFrame
        if environ_var not in data.columns:
            raise KeyError(f"{environ_var} column not found in the DataFrame.")
        else:
            environ_var_column = data[environ_var]
            environ_var_column = environ_var_column.dropna()  # Drop any non numeric values

        # Add the data to the overall data list and to its respective group list.
        data_groups['overall'].extend(environ_var_column)
        group = participant_data[part_id]["GroupNO"]

        if group == 'A':
            data_groups['group_A'].extend(environ_var_column)
        elif group == 'B':
            data_groups['group_B'].extend(environ_var_column)
        elif group == 'C':
            data_groups['group_C'].extend(environ_var_column)

        # Create yet another nested dictionary to hold all the summary stats. The key is 'summary_stats' and contains
        #     # environmental variables as nested keys. If the participant doesn't have a summary_stats key yet, create it.
        #     # Otherwise, simply add the summary_stats to the corresponding key.
        if 'summary_stats' not in participant_data[part_id]:
            participant_data[part_id]['summary_stats'] = pd.DataFrame(columns=environ_var_list)

        # Calculate summary stats for current individual participant. Add the summary stats and the data list to
        # participant_data
        summary_statistics = calculate_summary_stats(environ_var_column, environ_var)
        participant_data[part_id]['summary_stats'][environ_var] = summary_statistics

    # Calculate summary stats for all participants combined and for each group combined.
    for data_grouping, data_list in data_groups.items():
        summary_statistics = calculate_summary_stats(data_list, environ_var)

        # If the overall category has not been initialized in participant_data yet, initialize it.
        if data_grouping not in participant_data.keys():
            participant_data[data_grouping] = {}

        # Initialize a summary stats key.
        if 'summary_stats' not in participant_data[data_grouping]:
            participant_data[data_grouping]['summary_stats'] = pd.DataFrame(columns=environ_var_list)

        # Add the summary stats and the combined data to participant_data
        participant_data[data_grouping]['summary_stats'] = summary_statistics
        participant_data[data_grouping]['data'] = pandas.DataFrame({environ_var: data_list})

    # Add a "GroupNO" key for all entries in data_groups.
    for key in data_groups.keys():
        participant_data[key]["GroupNO"] = 'D'
        #participant_data[key]["GroupNO"] = key[-1]
        # Add color code for all entries in data_groups.
        participant_data = assign_color(participant_data, key, participant_data[key]["GroupNO"])


    return participant_data, data_groups

def calculate_summary_stats(environ_var_column, environ_var):
    """ Calculate the summary statistics for a given set of environ_var values and return them in a dictionary.
    Args:
        environ_var_column (list) : list of environ_var values for an individual participant, all participants, or all participants
        of one group.
        environ_var (str) : the current environmental variable name.

    Returns:
        summary_statistics (dict) : all the summary statistics from the given PM2.5 values, arranged in dict.
    """

    # Create a dictionary with the calculated summary statistics
    summary_statistics = {
        "10th_percentile": np.percentile(environ_var_column, 10),
        "25th_percentile": np.percentile(environ_var_column, 25),
        "50th_percentile": np.percentile(environ_var_column, 50),
        "75th_percentile": np.percentile(environ_var_column, 75),
        "90th_percentile": np.percentile(environ_var_column, 90),
        "Maximum": np.max(environ_var_column),
        "Mean": np.mean(environ_var_column),
    }

    # If we are dealing with pm25, calculate the percentage of time above the threshold of 12.
    if environ_var == "pm25":
        summary_statistics["Pecentage above 12"] = (sum(value > 12 for value in environ_var_column) / len(environ_var_column)) * 100

    return summary_statistics

def group_lists(participant_data):
    """Creates 3 lists, one for each educational group, to sort all participant IDs into their respective groups.

    Args:
        participant_data (dict) : nested dictionary with participant IDs as keys as all data as values.

    Returns:
        educational_groups (dict) : dictionary containing 3 lists. Each list contains all participant IDs from that
        educational group.
    """

    # Initializes dictionary to contain the IDs of all participants in each educational group.
    educational_groups = {
    'A' : [],
    'B' : [],
    'C' : []
    }

    for part_id in participant_data.keys():
        group = participant_data[part_id]["GroupNO"]

        # Records participant ID into one of the 3 educational group lists.
        if group == 'A':
            educational_groups['A'].append(part_id)
        elif group == 'B':
            educational_groups['B'].append(part_id)
        elif group == 'C':
            educational_groups['C'].append(part_id)

    return educational_groups

def graph_group_timeseries(participant_data, educational_groups, data_groups_keys, environ_var, graph_location):
    """Graphs PM2.5 timeseries data for all particpants of each educational group. Results in 3 graphs.

    Args:
        participant_data (dict) : nested dictionary with participant IDs as keys as all data as values.
        educational_groups (dict) : dictionary containing 3 lists. Each list contains all participant IDs from that
        educational group.
        data_groups_keys (list) : names of the overall categories: all participants combined, group A combined, group B
        combined, and group C combined.
        environ_var (str) : Name of current environmental variable.
        graph_location (str) : pathway to where graphs are saved
    """

    # Define a list of colors, line styles, and markers to make lines unique.
    colors = sns.color_palette('pastel')
    line_styles = ['-', '--', '-.', ':']
    markers = ['.', 'o', 'v', '^', 's', 'd']

    # Create one graph for each educational group
    for ed_group in ['A', 'B', 'C']:
        plt.figure(figsize=(8, 5), dpi=150)
        plt.title(f'{environ_var} vs Time, Group {ed_group}', fontdict={'fontweight': 'bold', 'fontsize': 18})
        plt.xlabel('Timestamp')
        plt.ylabel(f'{environ_var}')
        plt.xticks(rotation=45)

        # Go through all participants of the current educational group, plotting PM2.5 vs time.
        participants = educational_groups[ed_group]
        for i, part_id in enumerate(participants):
            # Get the color, line style, and marker for the current participant
            color = colors[i % len(colors)]
            line_style = line_styles[i % len(line_styles)]
            marker = markers[i % len(markers)]

            # If the entry is not one of the overall entries, the data_groups keys, plot PM2.5 vs time using the specified
            # color, line style, and marker.
            if part_id not in data_groups_keys:
                plt.plot(participant_data[part_id]['data']['time'], participant_data[part_id]['data'][environ_var], color=color,
                     linestyle=line_style, marker=marker, linewidth=2, markersize=2, label=part_id)

        plt.legend()
        plt.show()

        # # Save the plot to the specified directory
        # save_graph(graph_location, f"group_{ed_group}_pm25_plot.png")

    return

def save_graph(graph_location, file_name):
    # Save the plot to the specified directory
    file_path = os.path.join(graph_location, file_name)
    plt.savefig(file_path)

    # Close the plot to free up resources
    plt.close()

    return

def plot_summaries(participant_data, legend_elements, graph_location):
    """Creates a bar chart of the 3 summary statistics ('max', 'mean', 'percentage_above_12'). Each of the three charts
    includes each individual participant, all participants, all Group A, all group B, and all group C. Bars are color-coded
    by group assignment.
    Args:
        participant_data (dict) : nested dictionary with participant IDs as keys and all data as values.
        legend_elements (list) : defines color coding for legend.
        graph_location (str) : pathway to where graphs are saved.
    """

    participant_ids = list(participant_data.keys())

    # Define the pastel color palette
    colors = sns.color_palette('pastel')[1:5]

    # Create list of summary stats to be graphed via bar. Everything but percentiles.
    summary_stats = participant_data[list(participant_data.keys())[0]]['summary_stats'].keys()
    stats_to_graph = []
    for item in summary_stats:
        if 'percentile' not in item:
            stats_to_graph.append(item)

    # Create a bar chart for each summary statistic.
    for sum_stat in stats_to_graph:
        plt.figure()
        plt.figure(figsize=(8, 5), dpi=150)
        plt.title(f'{sum_stat} vs Participant', fontdict={'fontweight': 'bold', 'fontsize': 18})
        plt.xlabel('Participant')
        plt.ylabel(sum_stat)

        # Retrieve the summary statistic values for each participant
        stat_values = [participant_data[part_id]['summary_stats'][sum_stat] for part_id in participant_ids]

        # Assign colors based on 'GroupNO' value
        bar_colors = [colors[0] if participant_data[part_id]["GroupNO"] == 'A' else
                    colors[1] if participant_data[part_id]["GroupNO"] == 'B' else
                    colors[2] if participant_data[part_id]["GroupNO"] == 'C' else
                    colors[3] for part_id in participant_ids]

        # Create the bar plot with assigned colors
        plt.bar(participant_ids, stat_values, color=bar_colors)

    plt.legend(handles=legend_elements)

    # Show the plot
    plt.show()

    # # Save the plot to the specified directory
    # save_graph(graph_location, f"{sum_stat}_vs_participant.png")

    return

def plot_box_whisker(participant_data, legend_elements, graph_location):
    """Creates a box and whisker plot for the 'pm25' values of all participants.
    Args:
        participant_data (dict) : nested dictionary with participant IDs as keys and all data as values.
        legend_elements (list) : defines color coding for legend.
        graph_location (str) : pathway to where graphs are saved.
    """
    # Extract participant IDs and their corresponding 'pm25' values
    participant_ids = list(participant_data.keys())
    data_values = []

    # Create a nested list of 'pm25' values for all participants
    for part_id in participant_ids:
        pm25_list = participant_data[part_id]['data']['pm25'].dropna().tolist()
        data_values.append(pm25_list)

    # Create a box and whisker plot with all participants
    bp = plt.boxplot(data_values, patch_artist=True, showfliers=False)

    # Set the x-axis tick labels as participant IDs
    plt.xticks(range(1, len(participant_ids) + 1), participant_ids)
    plt.xticks(rotation=45)

    # Set the facecolor of each box based on participant's color.
    for i, box in enumerate(bp['boxes']):
        box.set_facecolor(participant_data[participant_ids[i]]['color'])

    # Set the color of median line to black
    for median in bp['medians']:
        median.set(color='black')

    # Set labels and title
    plt.xlabel('Participant')
    plt.ylabel('PM2.5')
    plt.title('Box and Whisker Plot')
    plt.legend(handles=legend_elements)
    plt.figure(figsize=(8, 5), dpi=150)

    # Show the plot
    plt.show()

    return


if __name__ == "__main__":
    main()