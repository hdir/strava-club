#!/usr/bin/env python3
"""Module to create html page of data from Strava web scraper"""

import json
from datetime import datetime

# Configuration of global variables
RESULTS_FILE = "data/result/results.json"
INDEX_FILE = 'index-beta.md'


class ToolBox():
    """Class with methods to be used calculating and processing results"""

    def get_current_week_number(self):
        """Method to get current week number"""
        week_number = datetime.now().strftime('%G-W%V')

        return week_number.split('-W')[1]

    def format_duration(self, duration_seconds):
        """Method to convert seconds to hh:mm"""
        try:
            seconds = int(max(0, duration_seconds))
            hours = seconds // 3600
            minutes = (seconds % 3600) // 60
            hours = f"{hours:02d}:{minutes:02d}"

        except ZeroDivisionError as error:
            hours = 0   
            print(f'An error occured formating time: {error}')

        return hours

    def format_distance(self, distance_meters):
        """Method to convert meters to km"""
        km = float(distance_meters/1000)

        return km

    def get_tickets(self, int_tickets):
        """Method to convert tickets int to tickets emoji"""
        if int_tickets == 2:
            visual_tickets = "🎫🎫"
        elif int_tickets == 1:
            visual_tickets = "🎫"
        else:
            visual_tickets = ""

        return visual_tickets

    def calculate_co2_saved(self, distance_km):
        """Method to calculate saved co2 pr km"""
        return round(distance_km*0.016, 2)


class Datastore():
    """Class to temporarily store copy of master data"""
    def __init__(self):
        self.master_data = {}
        self.read_master_data()
    
    def read_master_data(self):
        """Method to read json data from file"""
        with open(RESULTS_FILE, 'r', encoding='utf-8') as file:
            self.datastore = json.load(file)
    
    # Consider method to sort


class Results():
    """Class to calculate and temporarily store results for provided dataset"""
    def __init__(self, dataset):
        self.dataset = dataset
        self.total_athletes = self.count_athletes()
        self.athlete_summary = self.create_athlete_summary()
        self.aggregated_summary = self.create_aggregated_summary()
        self.rankings = self.get_changed_ranking()

    def count_athletes(self):
        """Method to count unique athletes in provided dataset"""
        unique_athlete_names = set()
        
        for entry in self.dataset.values():
            unique_athlete_names.add(entry["athlete_name"])
        
        return len(unique_athlete_names)
    
    def create_athlete_summary(self):
        """Method to create summary for athletes in provided dataset"""
        athlete_summary = {}

        # Create a dictionary to store the accumulated data for each athlete
        # Accumulate data for each athlete across all weeks
        for value in self.dataset.values():
            athlete_name = value["athlete_name"]

            if athlete_name not in athlete_summary:
                athlete_summary[athlete_name] = {
                    'activities': 0,
                    'distance': 0,
                    'moving_time': 0,
                    'elevation_gain': 0,
                    'tickets': 0
                }

            athlete_summary[athlete_name]['activities'] += value['activities']
            athlete_summary[athlete_name]['distance'] += value['distance']
            athlete_summary[athlete_name]['moving_time'] += value['moving_time']
            athlete_summary[athlete_name]['elevation_gain'] += value['elevation_gain']
            athlete_summary[athlete_name]['tickets'] += value['tickets']
        #Must add self to variables    
        #Consider moving this to function when refactoring
        athlete_summary = dict(sorted(athlete_summary.items(), key=lambda item: item[1]['distance'], reverse=True))
        
        return athlete_summary

    def create_aggregated_summary(self):
        """Method to create aggregated summary provided dataset"""
        aggregated_summary = {"moving_time": 0,
                            "distance": 0,
                            "elevation_gain": 0,
                            "activities": 0,
                            "athletes": 0,
                            "co2_saved": 0
                            }
        
        for record in self.dataset.values(): 
            aggregated_summary["moving_time"] += record["moving_time"]
            aggregated_summary["distance"] += ToolBox.format_distance(record["distance"])
            aggregated_summary["elevation_gain"] += record["elevation_gain"]
            aggregated_summary["activities"] += record["activities"]
            
        aggregated_summary["athletes"] = self.total_athletes
        aggregated_summary["co2_saved"] = ToolBox.calculate_co2_saved(aggregated_summary["distance"])
            
        return aggregated_summary
    
    def get_changed_ranking(self):
        """Method to get rankings for athletes in provided dataset"""
        ranking_current_week = []
        ranking_previous_week = []
        rankings = {}
        
        for value in self.dataset.values():

            if value["week_number"] == int(get_current_week_number()):
                ranking_current_week.append(value["athlete_name"])

            if value["week_number"] == int(get_current_week_number())-1:
                ranking_previous_week.append(value["athlete_name"])
        
        for value in data.values():
            if value["athlete_name"] in ranking_current_week and value["athlete_name"] in ranking_previous_week:
                current_rank = ranking_current_week.index(value["athlete_name"])
                previous_rank = ranking_previous_week.index(value["athlete_name"])

                if previous_rank - current_rank > 1:
                    rankings.update({value["athlete_name"]: "🔥"})
                elif current_rank < previous_rank:
                    rankings.update({value["athlete_name"]: "🔺"})
                elif current_rank > previous_rank:
                    rankings.update({value["athlete_name"]: "🔻"})
                elif current_rank == previous_rank:
                    rankings.update({value["athlete_name"]: "⏩"})
            else:
                rankings.update({value["athlete_name"]: "⭐"})

        return rankings

class Template():
    """Class to produce md-files for displaying results"""
    def __init__(self, outfile):
        #self.datastore = {}

if __name__ == "__main__":

    toobox = ToolBox()
    datastore = Datastore()
    results_all_teams = Results(datastore.master_data)
    outfile_index = Template(INDEX_FILE)
