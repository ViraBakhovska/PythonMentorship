"""This module parse log file:
- print the IP address of the top downloader
- print the least busy hour"""

import sys
from datetime import datetime

FILE_PATH = sys.argv[1]
#FILE_PATH = 'C:\PythonMentorship\Task_1\input\log_data\log_data.txt'

def group_by_date_and_ip(record_list):
    """This function group log data by date and ip"""
    grouped_by_date = {}
    for record in record_list:
        if record["Datetime"].date() not in grouped_by_date:
            grouped_by_date[record["Datetime"].date()] = {}
        grouped_by_ip = grouped_by_date[record["Datetime"].date()]
        if record["IP"] not in grouped_by_ip:
            grouped_by_ip[record["IP"]] = record["Size"]
        else:
            grouped_by_ip[record["IP"]] += record["Size"]
    return grouped_by_date


def print_top_downloader(grouped_by_date):
    """This function print IP address of the top downloader
    (having the highest sum of download file sizes) for the given day"""
    print('IP address of the top downloader: ')
    for date, ip_address in grouped_by_date.items():
        top_downloader = max(ip_address, key=ip_address.get)
        print(f'{date} - {top_downloader}')


def get_least_busy_hours(record_list):
    """This function get the hour that has the least number of requests"""
    list_of_hours = dict.fromkeys(range(0, 24), 0)
    for record  in record_list:
        list_of_hours[record['Datetime'].hour] += 1
    least_busy_hour = (min(list_of_hours, key=list_of_hours.get),
                       list_of_hours[min(list_of_hours, key=list_of_hours.get)])
    return least_busy_hour

with open(FILE_PATH, 'r') as log_data:
    log_data_record = []
    for line in log_data:
        line = line.replace('\n', '')
        line = line.split(' ')
        log_data_record.append({'IP' : line[0],
                                'Datetime' : datetime.strptime(line[1], '[%d/%b/%Y:%H:%M:%S]'),
                                'Size' : int(line[2])})


print_top_downloader(group_by_date_and_ip(log_data_record))

min_busy_hour = get_least_busy_hours(log_data_record)
print(f'The least busy hour: {min_busy_hour[0]}:00 Frequency of requests : {min_busy_hour[1]}')
