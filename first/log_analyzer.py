#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import re
import sys
import json
import gzip
import logging
import argparse
import statistics
from pathlib import Path
from string import Template
from datetime import datetime

# log_format ui_short '$remote_addr  $remote_user $http_x_real_ip [$time_local] "$request" '
#                     '$status $body_bytes_sent "$http_referer" '
#                     '"$http_user_agent" "$http_x_forwarded_for" "$http_X_REQUEST_ID" "$http_X_RB_USER" '
#                     '$request_time';

config = {
    "REPORT_SIZE": 1000,
    "REPORT_DIR": "./reports",
    "LOG_DIR": "./log"
}

regex = re.compile(
    r"""^(?P<ip>\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}) -?.+ - \[(?P<timestamp>.*?)\]\s\"(?P<method>[A-Z][A-Z][A-Z])"""
    r"""\s(?P<request>/.+\sHTTP/\d\.\d).+(?P<request_time>\d\.\d+)$""")

my_parser = argparse.ArgumentParser(prog='my_parser', usage='%(prog)s [path] ', argument_default=argparse.SUPPRESS,
                                    description='Log Parser.', epilog='Enjoy the log parser! :)')

my_parser.add_argument('-p', '--path', metavar='P', type=str, help='the path to config.json')

args = my_parser.parse_args()

if hasattr(args, "path"):

    config_file = args.path

    if os.path.isfile(config_file):
        print('The config_file found in provided path.')
        with open(config_file) as j:
            json_dict = json.load(j)
            config.update(json_dict)

timestamp = str(int(datetime.today().timestamp()))
today = str(datetime.today().date())
report_f_name = '/report-' + today + '.html'
report_file = Path(config["REPORT_DIR"] + report_f_name)


def define_logger():
    if "OUTPUT_LOG" in config.keys():
        log_dir = config["OUTPUT_LOG"]
        filename = "/log_parser" + timestamp + ".log"
        log_file = Path(log_dir + filename)

        if not os.path.isdir(log_dir):
            os.makedirs(log_dir)
            print("Successfully created the directory %s " % log_dir)
            print(f"Log file: {log_file}")
            return log_file
        else:
            return log_file
    else:
        return None


def check_report():
    try:
        if os.path.isdir(config["REPORT_DIR"]):
            logging.info(f"Report directory is: {config['REPORT_DIR']}")
        if os.path.isfile(report_file):
            logging.exception(f"Report {report_f_name} already processed!")
            sys.exit()
    except BaseException as e:
        logging.exception(f"Error occurred while sorting log dirs: {e}")


def sort_logs_dir(dir_):
    try:
        logging.info("Sorting nginx logs dir...")
        return sorted(os.listdir(dir_), key=lambda s: s[9:])
    except BaseException as e:
        logging.exception(f"Error occurred while sorting log dirs: {e}")


def render_template(*table_json):
    try:
        logging.info("Rendering template...")
        t = open('report.html', 'r+').read()
        template = Template(t)
        logging.info(f"REPORT SIZE {config['REPORT_SIZE']}")
        table_json = sorted(table_json, key=lambda item: item["time_sum"], reverse=True)[:config["REPORT_SIZE"]]

        table_json = {"table_json": table_json}
        return template.safe_substitute(table_json)
    except BaseException as e:
        logging.exception(f"Error occurred while rendering template: {e}")


def parse_ngnix_logs():
    try:
        result_set = {}
        counter = 0

        def _parse_line(match_line):
            uri = match_line.groups()[3].split()[0]
            if uri is not None and uri not in result_set.keys():

                result_set[uri] = {}
                result_set[uri]["times"] = []
                result_set[uri]["times"].append(float(match_line.groups()[4]))
                result_set[uri]["url"] = uri
                result_set[uri]["count"] = 1
                result_set[uri]["time_sum"] = float(match_line.groups()[4])
            elif uri is not None and uri in result_set.keys():
                result_set[uri]["count"] += 1
                result_set[uri]["times"].append(float(match_line.groups()[4]))
                result_set[uri]["time_sum"] += float(match_line.groups()[4])

        logging.info("Starting to parse logs...")
        dir_ = sort_logs_dir(config['LOG_DIR'])

        for archive in dir_:
            given_file = os.path.join(config['LOG_DIR'], archive)
            if given_file.endswith('.gz') and 'nginx' in given_file:
                with gzip.open(given_file, 'r', "utf-8") as file:
                    for line in file.readlines():
                        match = regex.search(line.decode('utf-8'))
                        if match:
                            counter += 1
                            _parse_line(match)
            else:
                if 'nginx' in given_file and "ui.log" in given_file.split("-")[2]:
                    with open(given_file) as file:
                        for line in file.readlines():
                            match = regex.search(line)
                            if match:
                                counter += 1
                                _parse_line(match)
        result_set["counter"] = counter
        return result_set
    except BaseException as e:
        logging.exception(f"Error occurred while parsing log file: {e}")


def get_max(list_):
    try:
        max_ = list_[0]
        for i in list_:
            if i > max_:
                max_ = i
        return max_
    except BaseException as e:
        logging.exception(f"Error occurred while calculating max value: {e}")


def build_dict(table_):
    try:
        logging.info("Calculating time requirements object...")
        counter = table_.pop("counter")
        timer = 0
        for item in table_.items():

            for i in item[1]["times"]:
                timer += i

        for item in table_.items():
            item[1]["time_avg"] = round(item[1]["time_sum"] / item[1]["count"], 9)
            item[1]["time_max"] = get_max(item[1]["times"])
            item[1]["time_med"] = statistics.median(item[1]["times"])
            item[1]["time_perc"] = round((item[1]["time_sum"] / timer) * 100, 9)
            item[1]["count_perc"] = round((item[1]["count"] / counter) * 100, 5)
            item[1]["time_sum"] = round(item[1]["time_sum"], 9)
        return table_
    except BaseException as e:
        logging.exception(f"Error occurred while building dictionary: {e}")


def clean_dict(table_):
    try:
        logging.info("Completely building dictionary object.")
        [item[1].pop("times") for item in table_.items()]
        return [item[1] for item in table_.items()]
    except BaseException as e:
        logging.exception(f"Error occurred while cleaning dictionary: {e}")


def save_report(result):
    try:
        logging.info("Writing report html...")
        if os.path.isdir(config["REPORT_DIR"]):
            open(report_file, 'w+').close()
        else:
            os.makedirs(config["REPORT_DIR"])
            open(report_file, 'w+').close()
        with open(report_file, "r+") as f:
            s = f.read()
            f.seek(0)
            f.write(result + s)
    except BaseException as e:
        logging.exception(f"Error occurred while saving report: {e}")


def main():
    logging.basicConfig(filename=define_logger(), level=logging.DEBUG)
    check_report()
    parsed_dict = parse_ngnix_logs()
    builded_dict = build_dict(parsed_dict)
    cleaned_dict = clean_dict(builded_dict)
    template = render_template(*cleaned_dict)
    save_report(template)


if __name__ == "__main__":
    main()
