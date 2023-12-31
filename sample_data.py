# # Set of simple sample data to use for development.
# participant_data = {
#         'A001': {
#             'date_dict': {
#                 '1': datetime(2023, 3, 23, 14, 45),
#                 '2': datetime(2023, 4, 7, 10, 10),
#                 '3': datetime(2023, 4, 24, 16, 0),
#                 '4': datetime(2023, 7, 11, 12, 50, 10),
#                 '2B': datetime(2023, 4, 7, 10, 11),
#                 '3B': datetime(2023, 4, 24, 16, 1)
#             },
#             'GroupNO': 'A',
#             'airthings_id': 'A01',
#             'data': pandas.DataFrame({
#                 'time': pd.to_datetime(
#                     ['2023-03-23 19:00:00', '2023-03-23 23:00:00', '2023-03-24 21:00:00', '2023-03-25 22:00:00',
#                      '2023-03-25 23:00:00']),
#                 'co2': [753.0, 757.0, 742.0, 600, 750.0],
#                 'humidity': [35.0, 36.0, 37.0, 37.0, 20],
#                 'light': [23, 29, 3016, 13, 20],
#                 'pressure': [1000, 1003.6, 1002.5, 1002.4, 1002.2],
#                 'sla': [54.0, 48.0, 35, 49.0, 49.0],
#                 'temp': [22.2, 22.1, 22.0, 25, 21.9],
#                 'voc': [49.0, 49.0, 60, 53.0, 59.0],
#                 'pm25': [10, 15, 8, 17, 22],
#                 'pm1': [30, 10, 8, 5, 50]
#             }),
#         },
#         'A002': {
#             'date_dict': {
#                 '1': datetime(2023, 3, 27, 15, 0),
#                 '2': datetime(2023, 4, 14, 14, 0),
#                 '3': datetime(2023, 4, 28, 9, 0),
#                 '4': datetime(2023, 7, 11, 12, 50, 11),
#                 '2B': datetime(2023, 4, 14, 14, 1),
#                 '3B': datetime(2023, 4, 28, 9, 1)
#             },
#             'GroupNO': 'A',
#             'airthings_id': 'A02',
#             'data': pandas.DataFrame({
#                 'time': pd.to_datetime(
#                     ['2023-03-23 19:00:00', '2023-03-23 20:00:00', '2023-03-23 21:00:00', '2023-03-23 22:00:00',
#                      '2023-03-24 19:00:00']),
#                 'co2': [800, 789.0, 1000, 942.0, 965.0],
#                 'humidity': [30.0, 31.0, 31.0, 32.0, 35.0],
#                 'light': [39, 35, 28, 14, 31],
#                 'pressure': [1015.3, 1015.0, 1014.6, 1015.3, 1015.2],
#                 'sla': [44.0, 49.0, 51.0, 54.0, 43.0],
#                 'temp': [22.5, 22.3, 22.2, 22.1, 22.1],
#                 'voc': [46.0, 57.0, 48.0, 50.0, 56.0],
#                 'pm25': [12, 9, 18, 6, 20],
#                 'pm1': [90, 10, 20, 30, 80]
#             }),
#         },
#         'A003': {
#             'date_dict': {
#                 '1': datetime(2023, 3, 28, 13, 0),
#                 '2': datetime(2023, 4, 10, 12, 0),
#                 '3': datetime(2023, 4, 28, 14, 0),
#                 '4': datetime(2023, 7, 11, 12, 50, 12),
#                 '2B': datetime(2023, 4, 10, 12, 1),
#                 '3B': datetime(2023, 4, 28, 14, 1)
#             },
#             'GroupNO': 'B',
#             'airthings_id': 'A03',
#             'data': pandas.DataFrame({
#                 'time': pd.to_datetime(
#                     ['2023-03-28 17:00:00', '2023-03-29 18:00:00', '2023-03-29 19:00:00', '2023-03-30 20:00:00',
#                      '2023-03-31 21:00:00']),
#                 'co2': [725.0, 708.0, 654.0, 650.0, 638.0],
#                 'humidity': [32.0, 33.0, 34.0, 34.0, 34.0],
#                 'light': [42, 41, 44, 36, 35],
#                 'pressure': [1016.1, 1015.8, 1015.2, 1015.0, 1015.0],
#                 'sla': [51.0, 42.0, 41.0, 42.0, 42.0],
#                 'temp': [20.6, 19.5, 19.6, 19.5, 19.5],
#                 'voc': [46.0, 54.0, 68.0, 59.0, 55.0],
#                 'pm25': [5, 7, 6, 3, 9],
#                 'pm1': [60, 100, 8, 80, 25]
#             }),
#         },
#         'A004': {
#             'date_dict': {
#                 '1': datetime(2023, 3, 28, 13, 0),
#                 '2': datetime(2023, 4, 10, 12, 0),
#                 '3': datetime(2023, 4, 28, 14, 0),
#                 '4': datetime(2023, 7, 11, 12, 50, 12),
#                 '2B': datetime(2023, 4, 10, 12, 1),
#                 '3B': datetime(2023, 4, 28, 14, 1)
#             },
#             'GroupNO': 'C',
#             'airthings_id': 'A03',
#             'data': pandas.DataFrame({
#                 'time': pd.to_datetime(
#                     ['2023-03-28 17:00:00', '2023-03-28 18:00:00', '2023-03-28 19:00:00', '2023-03-28 20:00:00',
#                      '2023-03-28 21:00:00']),
#                 'co2': [750.0, 730.0, 650.0, 650.0, 700.0],
#                 'humidity': [32.0, 33.0, 34.0, 34.0, 34.0],
#                 'light': [42, 41, 44, 36, 35],
#                 'pressure': [1016.1, 1015.8, 1015.2, 1015.0, 1015.0],
#                 'sla': [51.0, 42.0, 41.0, 42.0, 42.0],
#                 'temp': [20.6, 19.5, 19.6, 19.5, 19.5],
#                 'voc': [46.0, 54.0, 68.0, 59.0, 55.0],
#                 'pm25': [5, 7, 15, 3, 12],
#                 'pm1': [30, 10, 8, 1, 50]
#             }),
#         },
#         'A005': {
#             'date_dict': {
#                 '1': datetime(2023, 3, 28, 13, 0),
#                 '2': datetime(2023, 4, 10, 12, 0),
#                 '3': datetime(2023, 4, 28, 14, 0),
#                 '4': datetime(2023, 7, 11, 12, 50, 12),
#                 '2B': datetime(2023, 4, 10, 12, 1),
#                 '3B': datetime(2023, 4, 28, 14, 1)
#             },
#             'GroupNO': 'C',
#             'airthings_id': 'A03',
#             'data': pandas.DataFrame({
#                 'time': pd.to_datetime(
#                     ['2023-03-28 17:00:00', '2023-03-28 18:00:00', '2023-03-28 19:00:00', '2023-03-28 20:00:00',
#                      '2023-03-28 21:00:00']),
#                 'co2': [725.0, 708.0, 654.0, 650.0, 638.0],
#                 'humidity': [32.0, 33.0, 34.0, 34.0, 34.0],
#                 'light': [42, 41, 44, 36, 35],
#                 'pressure': [1016.1, 1015.8, 1015.2, 1015.0, 1015.0],
#                 'sla': [51.0, 42.0, 41.0, 42.0, 42.0],
#                 'temp': [20.6, 19.5, 19.6, 19.5, 19.5],
#                 'voc': [46.0, 54.0, 68.0, 59.0, 55.0],
#                 'pm25': [5, 7, 6, 3, 9],
#                 'pm1': [30, 35, 90, 70, 80]
#             }),
#         },
#         'A006': {
#             'date_dict': {
#                 '1': datetime(2023, 3, 23, 14, 45),
#                 '2': datetime(2023, 4, 7, 10, 10),
#                 '3': datetime(2023, 4, 24, 16, 0),
#                 '4': datetime(2023, 7, 11, 12, 50, 10),
#                 '2B': datetime(2023, 4, 7, 10, 11),
#                 '3B': datetime(2023, 4, 24, 16, 1)
#             },
#             'GroupNO': 'B',
#             'airthings_id': 'A01',
#             'data': pandas.DataFrame({
#                 'time': pd.to_datetime(
#                     ['2023-03-23 19:00:00', '2023-03-24 20:00:00', '2023-03-25 21:00:00', '2023-03-25 22:00:00',
#                      '2023-03-26 23:00:00']),
#                 'co2': [753.0, 757.0, 742.0, 751.0, 750.0],
#                 'humidity': [35.0, 36.0, 37.0, 37.0, 37.0],
#                 'light': [23, 29, 22, 16, 13],
#                 'pressure': [1004.4, 1003.6, 1002.5, 1002.4, 1002.2],
#                 'sla': [54.0, 48.0, 48.0, 49.0, 49.0],
#                 'temp': [22.2, 22.1, 22.0, 22.0, 21.9],
#                 'voc': [49.0, 49.0, 55.0, 53.0, 59.0],
#                 'pm25': [10, 15, 8, 5, 22],
#                 'pm1': [70, 20, 70, 80, 50]
#             }),
#         },
#
#     }