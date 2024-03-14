#!/usr/bin/env python3
"""Module to create html page of data from Strava web scraper"""

import json
from datetime import datetime

# File handling
FILE_PATH = 'index.md'

# Load the JSON content from the file
with open('data/result/results.json', 'r') as json_file:
    unsorted_data = json.load(json_file)
    data = dict(
        sorted(
            unsorted_data.items(), key=lambda item: item[1]["distance"], reverse=True))

with open('data/result/lag.json', 'r') as json_file:
    unsorted_data = json.load(json_file)
    lag = dict(
        sorted(
            unsorted_data.items(), key=lambda item: item[1]["distance"], reverse=True))

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

    # Create a dictionary to store the accumulated data for each athlete
    # Accumulate data for each athlete across all weeks
    #use .values() instead, dont need key
    for key, value in lag.items():
        athlete_names = value["athlete_names"]
        for key, value in data.items():
            athlete_name = value["athlete_name"]

    # Hent data for alle athleter som hører til laget
            if athlete_name in athlete_names:
                team_summary[athlete_name] = {
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

        return team_summary

def create_aggregated_summary():
    aggregated_summary = {"moving_time": 0,
                          "distance": 0,
                          "elevation_gain": 0,
                          "activities": 0,
                          "athletes": 0,
                          "co2_saved": 0
                         }
    

    for record in data.values(): 
        aggregated_summary["moving_time"] += record["moving_time"]
        aggregated_summary["distance"] += format_distance(record["distance"])
        aggregated_summary["elevation_gain"] += record["elevation_gain"]
        aggregated_summary["activities"] += record["activities"]
        
    aggregated_summary["athletes"] = count_athletes()
    aggregated_summary["co2_saved"] = calculate_co2_saved(aggregated_summary["distance"])
        
    return aggregated_summary

athlete_summary = create_athlete_summary()
aggregated_summary = create_aggregated_summary()

# Each table row should come on new line
aggregerte_resultater_table = f"<table class='table-aggregated'>\
<tr><td>👥 {aggregated_summary['athletes']} kolleger</td>\
<td>🏁 {aggregated_summary['activities']} aktiviteter</td>\
<td>⏳ {format_duration(aggregated_summary['moving_time'])} (t:m)</td></tr>\
<tr><td>📏 {round(aggregated_summary['distance'], 1)} km</td>\
<td>🧗 {aggregated_summary['elevation_gain']} høydemeter</td>\
<td>🌱 {aggregated_summary['co2_saved']} kg CO2 spart</td></tr>\
</table>"

ukens_resultater_table = "<table class='table'>\
<tr><th>Navn</th>\
<th>Antall aktiviteter</th>\
<th>Varighet (t:m)</th>\
<th>Distanse (km)</th>\
<th>Høydemeter</th></tr>"

for key, value in data.items():
    if int(value["week_number"]) == int(get_current_week_number()):
        ukens_resultater_table += (
            f"<tr><td>{rankings[value['athlete_name']]} {value['athlete_name']}</td>"
            f"<td>{value['activities']}</td>"
            f"<td>{format_duration(value['moving_time'])} {get_tickets(value['tickets'])}</td>"
            f"<td>{format_distance(value['distance'])}</td>"
            f"<td>{value['elevation_gain']}</td></tr>"
        )
ukens_resultater_table += "</table>"

forrige_ukes_resultater_table = "<table class='table'>\
<tr><th>Navn</th>\
<th>Antall aktiviteter</th>\
<th>Varighet (t:m)</th>\
<th>Distanse (km)</th>\
<th>Høydemeter</th></tr>"

for key, value in data.items():
    if int(value["week_number"]) == int(get_current_week_number())-1:
        forrige_ukes_resultater_table += (
            f"<tr><td>{value['athlete_name']}</td>"
            f"<td>{value['activities']}</td>"
            f"<td>{format_duration(value['moving_time'])} {get_tickets(value['tickets'])}</td>"
            f"<td>{format_distance(value['distance'])}</td>"
            f"<td>{value['elevation_gain']}</td></tr>"
        )
forrige_ukes_resultater_table += "</table>"

resultater_hele_perioden_table = "<table class='table'>\
<tr><th>Navn</th>\
<th>Aktiviteter</th>\
<th>Varighet (t:m)</th>\
<th>Lodd</th>\
<th>Distanse (km)</th>\
<th>Høydemeter</th></tr>"

for athlete_name, summary_data in athlete_summary.items():
    resultater_hele_perioden_table += (
        f"<tr><td>{athlete_name}</td>"
        f"<td>{summary_data['activities']}</td>"
        f"<td>{format_duration(summary_data['moving_time'])}</td>"
        f"<td>{summary_data['tickets']}</td>"
        f"<td>{format_distance(summary_data['distance'])}</td>"
        f"<td>{summary_data['elevation_gain']}</td></tr>"
    )
resultater_hele_perioden_table += "</table>"

# HTML content with the summarized table
html_content = f"""---
layout: default
title: Resultater
nav_order: 1
---

# Vår 2024 - Resultater

Informasjon om [aktivitetskampanjen](docs/info.md). For å delta må du også bli medlem i [Helsedirektoratets klubb på Strava](https://www.strava.com/clubs/754665).

<div class="tile-aggregated" id="aggregerte_data">
    <h2>Aggregerte data</h2>
    {aggregerte_resultater_table}
</div>
<div class="tile" id="ukens_resultater">
    <h2>Ukens resultater (uke {int(get_current_week_number())})</h2>
    {ukens_resultater_table}
</div>
<div class="tile" id="forrige_ukes_resultater">
    <h2>Forrige ukes resultater (uke {int(get_current_week_number())-1})</h2>
    {forrige_ukes_resultater_table}
</div>
<div class="tile" id="resultater_hele_perioden">
    <h2>Resultater hele perioden</h2>
    {resultater_hele_perioden_table}
</div>
"""



# Write the HTML content to the file
with open(FILE_PATH, 'w', encoding='utf-8') as html_file:
    html_file.write(html_content)
# debugging
#with open(FILE_PATH_DATA, 'w', encoding='utf-8') as html_file:
#    html_file.write(html_content)

print(f"HTML file created at: {FILE_PATH}")
