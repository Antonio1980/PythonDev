#!/usr/bin/env python

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

regex = re.compile(
    r"""^(?P<ip>\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}) -?.+ - \[(?P<timestamp_>.*?)\]\s\"(?P<method>[A-Z][A-Z][A-Z])"""
    r"""\s(?P<request>/.+\sHTTP/\d\.\d).+(?P<request_time>\d\.\d+)$""")


config = {
    "REPORT_SIZE": 1000,
    "REPORT_DIR": "./reports",
    "LOG_DIR": "./logs"
}


def handle_err(err):
    print(err)
    exit(-1)


class Config:

    __slots__ = (
        "REPORT_SIZE",
        "REPORT_DIR",
        "LOG_DIR",
        "OUTPUT_LOG",
    )

    def __init__(self):
        try:
            my_parser = argparse.ArgumentParser(prog='my_parser', usage='%(prog)s [path] ',
                                                argument_default=argparse.SUPPRESS,
                                                description='Log Parser.', epilog='Enjoy the logs parser! :)')
            my_parser.add_argument('-p', '--path', metavar='P', type=str, default='config/',
                                   help='path to config.json.bak')
            args = my_parser.parse_args()
            print("Building configuration.")
            config_path = args.path
            config_file = config_path + "config.json"

            if os.path.isfile(config_file):
                print('The config_file found in provided path.')
                with open(config_file) as j:
                    json_dict = json.load(j)
                    config.update(json_dict)
            for config_key in config:
                setattr(self, config_key, config[config_key])
        except (FileNotFoundError, IndexError, json.JSONDecodeError) as ex:
            handle_err(f"Error with config building {ex}")


settings = Config()


def build_output_logging():
    try:
        settings.__getattribute__("OUTPUT_LOG")
    except AttributeError as err:
        setattr(settings, "OUTPUT_LOG", None)

    if settings.OUTPUT_LOG:
        timestamp_ = str(int(datetime.today().timestamp()))
        log_dir = settings.OUTPUT_LOG
        filename = f"/log_parser{timestamp_}.logs"
        log_file = Path(log_dir + filename)
        if not os.path.isdir(log_dir):
            os.makedirs(log_dir)
            print("Successfully created the directory %s " % log_dir)
            print(f"Log file: {log_file}")
        return log_file
    else:
        return None


def check_report():
    logging.info("The configuration successfully build.")
    today_ = str(datetime.today().date())
    report_f_name = f'/report-{today_}.html'
    report_file = Path(settings.REPORT_DIR + report_f_name)
    if os.path.isdir(settings.REPORT_DIR):
        logging.info(f"Report directory is: {settings.REPORT_DIR}")
    if os.path.isfile(report_file):
        logging.info(f"Report {report_f_name} already processed!")
        sys.exit(0)
    else:
        return report_file


def sort_logs_dir(dir_):
    try:
        logging.info("Sorting nginx logs dir...")
        return sorted(os.listdir(dir_), key=lambda s: s[9:])
    except (IndexError, ValueError) as ex:
        logging.exception(f"Error occurred while sorting logs dirs: {ex}")


def render_template(*table_json):
    try:
        logging.info("Rendering template...")
        t = open('report.html', 'r+').read()
        template = Template(t)
        logging.info(f"REPORT SIZE {settings.REPORT_SIZE}")
        table_json = sorted(table_json, key=lambda item: item["time_sum"], reverse=True)[:settings.REPORT_SIZE]

        table_json = {"table_json": table_json}
        return template.safe_substitute(table_json)
    except (IndexError, ValueError) as ex:
        logging.exception(f"Error occurred while rendering template: {ex}")


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
        dir_ = sort_logs_dir(settings.LOG_DIR)

        for archive in dir_:
            given_file = os.path.join(settings.LOG_DIR, archive)
            if given_file.endswith('.gz') and 'nginx' in given_file:
                with gzip.open(given_file, 'r', "utf-8") as file:
                    for line in file.readlines():
                        match = regex.search(line.decode('utf-8'))
                        if match:
                            counter += 1
                            _parse_line(match)
            else:
                if 'nginx' in given_file and "ui.logs" in given_file.split("-")[2]:
                    with open(given_file) as file:
                        for line in file.readlines():
                            match = regex.search(line)
                            if match:
                                counter += 1
                                _parse_line(match)
        result_set["counter"] = counter
        return result_set
    except (IndexError, ValueError) as ex:
        logging.exception(f"Error occurred while parsing logs file: {ex}")


def get_max(list_):
    try:
        max_ = list_[0]
        for i in list_:
            if i > max_:
                max_ = i
        return max_
    except (IndexError, ValueError) as ex:
        logging.exception(f"Error occurred while calculating max value: {ex}")


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
            item[1]["time_max"] = max(item[1]["times"])
            item[1]["time_med"] = round(statistics.median(item[1]["times"]), 9)
            item[1]["time_perc"] = round((item[1]["time_sum"] / timer) * 100, 9)
            item[1]["count_perc"] = round((item[1]["count"] / counter) * 100, 9)
            item[1]["time_sum"] = round(item[1]["time_sum"], 3)
        return table_
    except (IndexError, ValueError) as ex:
        logging.exception(f"Error occurred while building dictionary: {ex}")


def clean_dict(table_):
    try:
        logging.info("Completely building dictionary object.")
        [item[1].pop("times") for item in table_.items()]
        return [item[1] for item in table_.items()]
    except (IndexError, ValueError) as ex:
        logging.exception(f"Error occurred while cleaning dictionary: {ex}")


def save_report(report_file_, result):
    try:
        logging.info("Writing report html...")
        if os.path.isdir(settings.REPORT_DIR):
            open(report_file_, 'w+').close()
        else:
            os.makedirs(settings.REPORT_DIR)
            open(report_file_, 'w+').close()
        with open(report_file_, "r+") as f:
            f.seek(0)
            f.write(result)
    except (IndexError, ValueError) as ex:
        logging.exception(f"Error occurred while saving report: {ex}")


def main():
    logging.basicConfig(filename=build_output_logging(), level=logging.DEBUG)
    r_file = check_report()
    parsed_dict = parse_ngnix_logs()
    _dict = build_dict(parsed_dict)
    cleaned_dict = clean_dict(_dict)
    template = render_template(*cleaned_dict)
    save_report(r_file, template)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logging.error(e)
