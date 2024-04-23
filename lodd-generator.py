#!/usr/bin/env python3
"""Module to process data from Strava web scraper"""

import configparser
import os
import json


if __name__ == "__main__":

    config = configparser.ConfigParser()
    config.read(os.path.join(os.getcwd(), 'settings', 'config.ini'),
                encoding='utf-8')

    RESULTS_FILE = config['CAMPAIGN'].get('RESULTS_FILE')
    TICKET_FILE = "lodd.txt"
    TICKET_WEEKS = [14, 15]

    with open(RESULTS_FILE, 'r', encoding='utf-8') as file:
        datastore = json.load(file)

    ticket_id = 1
    with open(TICKET_FILE, "w", encoding="utf-8") as file:
        unique_names = set()
        two_tickets = 0
        one_ticket = 0
        no_tickets = 0
        rows_written = 0

        for athlete_id, athlete_data in datastore.items():
            athlete_name = athlete_data["athlete_name"]
            tickets = athlete_data["tickets"]

            for number in range(tickets):
                file.write(f'{ticket_id} - {athlete_name}\n')
                rows_written += 1
                ticket_id = ticket_id+1

            unique_names.add(athlete_name)

    print(f"Kolleger med aktivitetstid: {len(unique_names)}")
    print(f"Totalt antall lodd utdelt: {rows_written}")
    print('Loddfilen ligger som lodd.txt')
