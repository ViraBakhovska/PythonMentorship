#!/bin/python3
import os
import sys
from datetime import datetime

#file_path = sys.argv[1]
file_path = 'C:\PythonMentorship\Task_1\input\log_data\log_data.txt'

def group_by_date_and_IP (record_list):
    grouped_by_date = {}
    for record in record_list:
        if record["Datetime"].date() not in grouped_by_date:
            grouped_by_date[record["Datetime"].date()] = {}
        grouped_by_IP = grouped_by_date[record["Datetime"].date()]
        if record["IP"] not in grouped_by_IP:
            grouped_by_IP[record["IP"]] = record["Size"]
        else:
            grouped_by_IP[record["IP"]] += record["Size"]
    return grouped_by_date


def print_top_downloader(grouped_by_date):
    print('IP address of the top downloader: ')
    for date, ip in grouped_by_date.items():
        top_downloader = max(ip, key = ip.get)
        print(f'{date} - {top_downloader}')


def get_least_busy_hours(record_list):
    list_of_hours = dict.fromkeys(range(00,24),0)
    for record  in record_list:
        list_of_hours[record['Datetime'].hour] += 1
    least_busy_hour = (min(list_of_hours,key = list_of_hours.get), list_of_hours[min(list_of_hours,key = list_of_hours.get)])
    return least_busy_hour

with open(file_path,'r') as log_data:
    log_data_record = []
    for line in log_data:
        line = line.replace('\n','')
        str = line.split(' ')
        log_data_record.append({'IP' : str[0],
                                'Datetime' : datetime.strptime(str[1],'[%d/%b/%Y:%H:%M:%S]'),
                                'Size' : int(str[2])})


print_top_downloader(group_by_date_and_IP(log_data_record))

least_busy_hour = get_least_busy_hours(log_data_record)
print(f'The least busy hour: {least_busy_hour[0]}:00 Frequency of requests : {least_busy_hour[1]}')