#!/usr/bin/env python3
"""Module to process data from Strava web scraper"""

import csv
import json
from datetime import datetime

# Configuration of global variables
CSV_FILE = "testdata.csv"
RESULTS_FILE = "results.json"

class Filehandler:
    """Class to process data and handle files"""
    def __init__(self):
        #self.backup()
        self.datastore = {}
        self.read_datastore()
        self.process_csv()

    def get_week_number(self, date_str):
        """Method to translate weekday to week number"""
        date_obj = datetime.strptime(date_str, '%Y-%m-%d')
        week_number = date_obj.strftime('%G-W%V')
        return week_number.split('-W')[1]

    def read_datastore(self):
        """Method to read json data from file"""
        with open(RESULTS_FILE, 'r', encoding='utf-8') as file:
            self.datastore = json.load(file)

    def process_csv(self):
        """Method to read and process csv data from file"""
        with open(CSV_FILE, 'r', encoding='utf-8') as file:
            csv_list = list(csv.DictReader(file))

        for dictionary in csv_list:
            week_number = self.get_week_number(dictionary["leaderboard_date_start"])
            athlete_weekly_uid = f'{week_number}-{dictionary["athlete_name"]}'
            self.datastore.update({athlete_weekly_uid: {"week_number": week_number,
                                   "athlete_name": dictionary["athlete_name"],
                                   "activities": int(dictionary["activities"]),
                                   "distance": int(float(dictionary["distance"]))/1000,
                                   "distance_longest": int(float(dictionary["distance_longest"]))/1000,
                                   "elevation_gain": int(float(dictionary["elevation_gain"]))
                                   }})

        self.save_datastore()

    def save_datastore(self):
        """Method to write json data to file"""
        with open(RESULTS_FILE, 'w', encoding='utf-8') as file:
            json.dump(self.datastore, file, indent=2)

class Transformations:
    """Class to enrich datastore with aggregation etc"""
    def __init__(self):
        pass

    def update_totals(self):
        """Method to update totals for a given period"""

if __name__ == "__main__":

    filehandler = Filehandler()
    #tranfsformations = Transformations() Maybe handle in script to create html file

#Add basic error handling with output file
#Make backup of file,todays date