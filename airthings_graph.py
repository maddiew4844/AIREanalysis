#!/usr/bin/env python

""" Airthings graph

Python script to analyze and display airthings data from the AIRE study. Pulls data from all participants, calculates
summary statistics, creates Excel summary statistics file, and creates graphical displays of the results.

This script requires that ???? be installed within the environment.

Author: Madeleine Wallace
Last updated: 07/07/23
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

    # Calculate pm25 summary stats (percentiles, max, mean, % above 12) for all the participants. Add them to
    # particpant_data
    participant_data = calculate_summary_stats(participant_data)
    print(participant_data)

    graph_location = "/Users/maddiewallace/PycharmProjects/AIREanalysis/graph_outputs"

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
        print('fileFormat must be either csv, tsv, or spss')
        sys.exit(2)

    # Confirms survey ID.
    r = re.compile('^SV_.*')
    m = r.match(surveyId)
    if not m:
        print("survey Id must match ^SV_.*")
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
        date_dict[key] = datetime.strptime(date_dict[key], '%m-%d-%Y %H:%M')

    # Confirm that the given participant is not missing visits 1-3.
    for visit in ['1', '2', '3']:
        if visit not in date_dict.keys():
            logging.error(f"Participant {part_id} does not have a data log entry for visit {visit}. Please record this "
                          f"visit via Qualtrics before trying again.")
            exit()

    # Add the start date for the intervention and follow-up periods under the key {visit_num}B.
    for key in ['2', '3']:
        date_dict["{}{}".format(key, "B")] = date_dict[key] + timedelta(minutes=1)

    # to download all data through today (except for A009 and A004 who did not keep their monitors):
    #TODO: automate choice of downloading through current date or through visit 4 or through visit 5.
    if part_id != "A009" or part_id != "A004":
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
        print(f"Request failed with status code {response.status_code}")

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

        # Reorder the columns so that 'time' is the first column
        data_df = data_df.reindex(columns=['time'] + list(data_df.columns.drop('time')))

    else:
        print(f"Get request for Airthings {airthings_id} for participant {part_id} failed with status code "
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
        'data': data_df
    }

    return participant_data

def calculate_summary_stats(participant_data):
    """ Calculates summary statistics for the "pm25" column in the "data" key of all the participants from
    participant_data. Summary stats include: percentiles, max, mean, % above 12.

    Args:
        participant_data (dict) : nested dictionary updated to contain participant IDs as keys, their date_dict, and
        group_assignment.

    Returns:
        participant_data (dict) : nested dictionary updated to contain participant IDs as keys, their date_dict, and
        group_assignment. Now contains a nested summary statistics dictionary.

    Raises:
        KeyError: If the "data" key is not present in participant_data or if "pm25" column is not present in the DataFrame.
    """

    for part_id in participant_data.keys():
        data = participant_data[part_id]["data"]

        # Check if "data" key exists and is a DataFrame
        if not isinstance(data, pd.DataFrame):
            raise KeyError("'data' key must contain a DataFrame.")

        # Check if "pm25" column exists in the DataFrame
        if "pm25" not in data.columns:
            raise KeyError("'pm25' column not found in the DataFrame.")
        else:
            pm25_column = data["pm25"]

        # Calculate the percentage above 12 before turning pm25 into a list.
        percentage_above_12 = (np.sum(pm25_column > 12) / len(pm25_column)) * 100

        pm25_column = data["pm25"].dropna().tolist()

        # Calculate summary statistics
        tenth_percentile = np.percentile(pm25_column, 10)
        twentyfifth_percentile = np.percentile(pm25_column, 25)
        fiftieth_percentile = np.percentile(pm25_column, 50)
        seventyfifth_percentile = np.percentile(pm25_column, 75)
        ninetieth_percentile = np.percentile(pm25_column, 90)
        maximum = np.max(pm25_column)
        mean = np.mean(pm25_column)

        # Create a dictionary with the summary statistics
        summary_statistics = {
            "10th_percentile": tenth_percentile,
            "25th_percentile": twentyfifth_percentile,
            "50th_percentile": fiftieth_percentile,
            "75th_percentile": seventyfifth_percentile,
            "90th_percentile": ninetieth_percentile,
            "max": maximum,
            "mean": mean,
            "percentage_above_12": percentage_above_12
        }

        # Add the summary stats dictionary to participant_data.
        participant_data[part_id]['summary_stats'] = summary_statistics

    return participant_data


if __name__ == "__main__":
    main()

#
# folder_path = "/Users/maddiewallace/PycharmProjects/AIRE_Report_Back2/outputs/"
# csv_files = [file for file in os.listdir(folder_path) if file.endswith(".csv")]
#
# group_a = ['A001', 'A004', 'A007', 'A010', 'A013']
# group_b = ['A002', 'A005', 'A008', 'A011', 'A014']
# group_c = ['A003', 'A006', 'A009', 'A012', 'A015']
#
# pm25_data = {}
#
# for file in csv_files:
#     file_path = os.path.join(folder_path, file)
#     participant_id = os.path.splitext(file)[0]
#     data = pd.read_csv(file_path)
#     data['pm25'] = pd.to_numeric(data['pm25'], errors='coerce')  # Convert 'PM2.5' column to numeric
#     pm25_data[participant_id] = data['pm25'].dropna().tolist()
#
# def calculate_summary_statistics(data):
#     summary_stats = {}
#     all_values = []
#
#     for participant, values in data.items():
#         summary_stats[participant] = {}
#         values = np.array(values)
#
#         # Calculate summary statistics
#         summary_stats[participant]['10th_percentile'] = np.percentile(values, 10)
#         summary_stats[participant]['25th_percentile'] = np.percentile(values, 25)
#         summary_stats[participant]['50th_percentile'] = np.percentile(values, 50)
#         summary_stats[participant]['75th_percentile'] = np.percentile(values, 75)
#         summary_stats[participant]['90th_percentile'] = np.percentile(values, 90)
#         summary_stats[participant]['max'] = np.max(values)
#         summary_stats[participant]['mean'] = np.mean(values)
#         summary_stats[participant]['percentage_above_12'] = (np.sum(values > 12) / len(values)) * 100
#
#         all_values.extend(values)
#
#     # Calculate summary statistics for the entire dataset
#     all_values = np.array(all_values)
#     summary_stats['overall'] = {
#         '10th_percentile': np.percentile(all_values, 10),
#         '25th_percentile': np.percentile(all_values, 25),
#         '50th_percentile': np.percentile(all_values, 50),
#         '75th_percentile': np.percentile(all_values, 75),
#         '90th_percentile': np.percentile(all_values, 90),
#         'max': np.max(all_values),
#         'mean': np.mean(all_values),
#         'percentage_above_12': (np.sum(all_values > 12) / len(all_values)) * 100
#     }
#
#     return summary_stats
#
# # Call the function with the data
# summary_stats = calculate_summary_statistics(pm25_data)
#
# # Create a DataFrame for participant statistics
# df_participants = pd.DataFrame.from_dict(summary_stats, orient='index')
#
# # Sort the participants in ascending order based on the participant ID
# df_participants = df_participants.reindex(sorted(df_participants.index))
#
# # Save the DataFrame as a CSV file
# output_path = "/Users/maddiewallace/PycharmProjects/AIRE_Report_Back2/summary_stats/summary_stats.csv"
# df_participants.to_csv(output_path, index=True)
#
# # Define colors for each participant group
# group_colors = {'Group A': 'green', 'Group B': 'blue', 'Group C': 'yellow'}
#
# # Plotting percentage above 12
# plt.figure(figsize=(10, 6))
# plt.bar(df_participants.index, df_participants['percentage_above_12'], label='Percentage Above 12',
#         color=[group_colors['Group A'] if participant in group_a else
#                group_colors['Group B'] if participant in group_b else
#                group_colors['Group C']
#                for participant in df_participants.index])
# plt.bar('overall', df_participants.loc['overall', 'percentage_above_12'], label='Overall', color='orange')
# plt.title('Percentage of Time PM2.5 is Above 12')
# plt.xlabel('Participant')
# plt.ylabel('Percentage')
# plt.xticks(rotation=45)
#
# # Create legend with group colors
# legend_elements = [plt.bar(0, 0, color=color, label=label) for label, color in group_colors.items()]
# plt.legend(handles=legend_elements)
# plt.show()
#
# # Plotting maximum values
# plt.figure(figsize=(10, 6))
# plt.bar(df_participants.index, df_participants['max'], label='Maximum',
#         color=[group_colors['Group A'] if participant in group_a else
#                group_colors['Group B'] if participant in group_b else
#                group_colors['Group C']
#                for participant in df_participants.index])
# plt.bar('overall', df_participants.loc['overall', 'max'], label='Overall', color='orange')
# plt.title('Maximum PM2.5 Values')
# plt.xlabel('Participant')
# plt.ylabel('PM2.5')
# plt.xticks(rotation=45)
#
# # Create legend with group colors
# legend_elements = [plt.bar(0, 0, color=color, label=label) for label, color in group_colors.items()]
# plt.legend(handles=legend_elements)
# plt.show()
#
# # Plotting mean values
# plt.figure(figsize=(10, 6))
# plt.bar(df_participants.index, df_participants['mean'], label='Mean',
#         color=[group_colors['Group A'] if participant in group_a else
#                group_colors['Group B'] if participant in group_b else
#                group_colors['Group C']
#                for participant in df_participants.index])
# plt.bar('overall', df_participants.loc['overall', 'mean'], label='Overall', color='orange')
# plt.title('Mean')
# plt.xlabel('Participant')
# plt.ylabel('Percentage')
#
# # Create legend with group colors
# legend_elements = [plt.bar(0, 0, color=color, label=label) for label, color in group_colors.items()]
# plt.legend(handles=legend_elements)
# plt.show()
#
# # # Combine participant data into a list
# # participant_data = [pm25_data[participant] for participant in df_participants.index if participant != 'overall']
# #
# # # Create labels for the box plot
# # labels = [participant for participant in df_participants.index if participant != 'overall']
# #
# # # Plot box and whisker plot
# # plt.figure(figsize=(10, 6))
# # plt.boxplot(participant_data, labels=labels, patch_artist=True)
# #
# # # Set colors for each participant group
# # for patch, participant in zip(plt.gca().artists, labels):
# #     if participant in group_a:
# #         patch.set_facecolor(group_colors['Group A'])
# #     elif participant in group_b:
# #         patch.set_facecolor(group_colors['Group B'])
# #     elif participant in group_c:
# #         patch.set_facecolor(group_colors['Group C'])
# #
# # # Set color for the overall box
# # overall_patch = plt.gca().artists[0]
# # overall_patch.set_facecolor('red')
# #
# # plt.title('PM2.5 Distribution')
# # plt.xlabel('Participant')
# # plt.ylabel('PM2.5')
# # plt.xticks(rotation=45)
# #
# # # Create legend with group colors
# # legend_elements = [plt.bar(0, 0, color=color, label=label) for label, color in group_colors.items()]
# # legend_elements.append(plt.bar(0, 0, color='red', label='Overall'))
# # plt.legend(handles=legend_elements)
# #
# # plt.show()
#
