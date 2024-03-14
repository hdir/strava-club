#!/usr/bin/env python3
"""Module to create html page of data from Strava web scraper"""

import json
from datetime import datetime

# File handling
FILE_PATH = 'docs/lag.md'

# Load the JSON content from the file
with open('data/result/results.json', 'r') as json_file:
    unsorted_data = json.load(json_file)
    data = dict(
        sorted(
            unsorted_data.items(), key=lambda item: item[1]["distance"], reverse=True))

with open('data/result/lag.json', 'r') as json_file:
    lag = json.load(json_file)

def get_current_week_number():
    """Function to get current week number"""
    week_number = datetime.now().strftime('%G-W%V')
    return week_number.split('-W')[1]


def format_duration(duration_seconds):
    try:
        seconds = int(max(0, duration_seconds))
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60

        hours = f"{hours:02d}:{minutes:02d}"

    except ZeroDivisionError as error:
        hours = 0   
        print(f'An error occured formating time: {error}')
    
    return hours


def format_distance(distance):
    km = float(distance/1000)
    return km

def calculate_co2_saved(distance):
    return round(distance*0.016, 2)

def create_athlete_summary():
    athlete_summary = {}

    # Create a dictionary to store the accumulated data for each athlete
    # Accumulate data for each athlete across all weeks
    #use .values() instead, dont need key
    for key, value in data.items():
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

    return athlete_summary

def create_team_summary():
    team_summary = {}
    
    # Create a dictionary to store the accumulated data for each team
    # Accumulate data for for each team across all weeks
    for key, value in lag.items():
        athlete_names = value["athlete_names"]
        lag_nr = value["lagnr"]
        for key, value in data.items():
            athlete_name = value["athlete_name"]
            # Hent data for alle athleter som hører til laget
            if athlete_name in athlete_names:
                team_summary[lag_nr]['activities'] += value['activities']
                team_summary[lag_nr]['distance'] += value['distance']
                team_summary[lag_nr]['moving_time'] += value['moving_time']
                team_summary[lag_nr]['elevation_gain'] += value['elevation_gain']

    return team_summary

team_summary = create_team_summary()

lag_resultater_hele_perioden_table = "<table class='table'>\
<tr><th>Lag</th>\
<th>Aktiviteter</th>\
<th>Varighet (t:m)</th>\
<th>Distanse (km)</th>\
<th>Høydemeter</th></tr>"

for lagnr, summary_data in team_summary.items():
    lag_resultater_hele_perioden_table += (
        f"<tr><td>{lagnr}</td>"
        f"<td>{summary_data['activities']}</td>"
        f"<td>{format_duration(summary_data['moving_time'])}</td>"
        f"<td>{summary_data['tickets']}</td>"
        f"<td>{format_distance(summary_data['distance'])}</td>"
        f"<td>{summary_data['elevation_gain']}</td></tr>"
    )
lag_resultater_hele_perioden_table += "</table>"

# HTML content with the summarized table
html_content = f"""---
layout: default
title: Lagkonkurransen
nav_order: 3
---

# Vår 2024 - Lagkonkurransen

Informasjon om [aktivitetskampanjen](docs/info.md). For å delta må du også bli medlem i [Helsedirektoratets klubb på Strava](https://www.strava.com/clubs/754665).

<div class="tile-aggregated" id="aggregerte_data">
    <h2>Aggregerte lagdata</h2>
    {lag_resultater_hele_perioden_table}
</div>
"""

# Write the HTML content to the file
with open(FILE_PATH, 'w', encoding='utf-8') as html_file:
    html_file.write(html_content)
# debugging
#with open(FILE_PATH_DATA, 'w', encoding='utf-8') as html_file:
#    html_file.write(html_content)

print(f"HTML file created at: {FILE_PATH}")
