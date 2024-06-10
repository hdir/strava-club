#!/usr/bin/env python3
"""Module to create list of athletes and tickets"""

import configparser
import os
import json


if __name__ == "__main__":

    config = configparser.ConfigParser()
    config.read(os.path.join(os.getcwd(), 'settings', 'config.ini'),
                encoding='utf-8')

    RESULTS_FILE = config['CAMPAIGN'].get('RESULTS_FILE')
    TICKET_FILE = "lodd.txt"
    TICKET_WEEKS = [16, 17, 18, 19, 20, 21, 22, 23]

    with open(RESULTS_FILE, 'r', encoding='utf-8') as file:
        datastore = json.load(file)

    with open(TICKET_FILE, "w", encoding="utf-8") as file:
        unique_names = set()
        ticket_id = 0
        rows_written = 0

        for athlete_data in datastore.values():
            if athlete_data["week_number"] in TICKET_WEEKS:
                athlete_name = athlete_data["athlete_name"]
                tickets = athlete_data["tickets"]

                for number in range(tickets):
                    rows_written += 1
                    ticket_id += 1
                    file.write(f'{ticket_id} - {athlete_name}\n')

                unique_names.add(athlete_name)

    print(f"Kolleger med aktivitetstid: {len(unique_names)}")
    print(f"Totalt antall lodd utdelt: {rows_written}")
    print('Loddfilen ligger som lodd.txt')
