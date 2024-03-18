#!/usr/bin/env python3
"""Module to process data from Strava web scraper"""

import csv
import json
from datetime import datetime

# Configuration of global variables
CSV_FILE = "data/skrap/club_leaderboard.csv"
RESULTS_FILE = "data/result/results.json"
CAMPAIGN_WEEK_START = 12
CAMPAIGN_WEEK_STOP = 13


class Transformer:
    """Class to transform data and handle files"""
    def __init__(self):
        self.datastore = {}

    def read_datastore(self):
        """Method to read json data from file"""
        try:
            with open(RESULTS_FILE, 'r', encoding='utf-8') as file:
                self.datastore = json.load(file)
        except FileNotFoundError:
            print(f"{RESULTS_FILE} not found, creating new")
            with open(RESULTS_FILE, 'w', encoding='utf-8') as file:
                json.dump({}, file)

    def save_datastore(self):
        """Method to write json data to file"""
        with open(RESULTS_FILE, 'w', encoding='utf-8') as file:
            json.dump(self.datastore, file, indent=2)

    def process_csv(self):
        """Method to read and process csv data from file"""
        with open(CSV_FILE, 'r', encoding='utf-8') as file:
            csv_list = list(csv.DictReader(file))

        for dictionary in csv_list:

            if "moving_time" in dictionary:
                moving_time = int(float(dictionary["moving_time"]))
            else:
                moving_time = int(0)

            try:
                week_number = self.get_week_number(dictionary["leaderboard_date_start"])
                athlete_weekly_uid = f'{week_number}-{dictionary["athlete_id"]}'

                self.datastore.update(
                    {athlete_weekly_uid: {
                        "week_number": int(week_number),
                        "athlete_name": dictionary["athlete_name"],
                        "activities": int(dictionary["activities"]),
                        "moving_time": moving_time,
                        "distance": int(float(dictionary["distance"])),
                        "elevation_gain": int(float(dictionary["elevation_gain"])),
                        "tickets": int(self.calculate_tickets(moving_time))
                    }})

            except (KeyError, ValueError) as error:
                print(f'An error occured processing CSV: {error}')

    def purge_non_campaign_activities(self):
        """Method to delete records outside campaign from datastore"""
        records_to_delete = []
        records_before_purge = len(self.datastore)

        print(f'There are {records_before_purge} records in datastore')

        for key, value in self.datastore.items():
            if value["week_number"] not in range(CAMPAIGN_WEEK_START,
                                                 CAMPAIGN_WEEK_STOP+1):
                records_to_delete.append(key)

        for key in records_to_delete:
            del self.datastore[key]

        print(f'{records_before_purge - len(self.datastore)}'
              f' were outside campaign period and have been deleted')

    def get_week_number(self, date_str):
        """Method to translate weekday to week number"""
        date_obj = datetime.strptime(date_str, '%Y-%m-%d')
        week_number = date_obj.strftime('%G-W%V')

        return week_number.split('-W')[1]

    def calculate_tickets(self, moving_time_seconds):
        """Method to translate activity minutes into tickets"""
        try:
            if moving_time_seconds/60 in range(150, 299):
                tickets = 1
            elif moving_time_seconds/60 >= 300:
                tickets = 2
            else:
                tickets = 0

        except ZeroDivisionError as error:
            tickets = 0
            print(f'An error occured calculating tickets: {error}')

        return tickets


if __name__ == "__main__":

    transformer = Transformer()
    transformer.read_datastore()
    transformer.process_csv()
    transformer.purge_non_campaign_activities()
    transformer.save_datastore()
