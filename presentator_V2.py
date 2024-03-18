#!/usr/bin/env python3
"""Module to create html page of data from Strava web scraper"""

import json
import textwrap
from datetime import datetime

# Configuration of global variables
RESULTS_FILE = "data/result/results.json"
INDEX_FILE = 'index.md'
TEAMS_FEATURE = False
CAMPAIGN_WEEK_START = 12


class Toolbox():
    """Class with methods to be used calculating and processing results"""
    def __init__(self):
        pass

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
        distance_km = float(distance_meters/1000)

        return distance_km

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

    def get_teams(self):
        """Method to create a list of teams based on content in datastore"""
        unique_teams = set()

        for value in datastore.master_data.values():
            if value["team"] != "":
                unique_teams.add(value["team"])

        return unique_teams

    def sort_dictionary(self, dictionary_to_sort, sortkey):
        """Method to sort a dictionary based on a given key"""
        sorted_dict = dict(sorted(dictionary_to_sort.items(), key=lambda item: item[1][sortkey], reverse=True))

        return sorted_dict


class Datastore():
    """Class to temporarily store copy of master data"""
    def __init__(self):
        self.master_data = {}
        self.read_master_data()

    def read_master_data(self):
        """Method to read json data from file"""
        with open(RESULTS_FILE, 'r', encoding='utf-8') as file:
            self.master_data = json.load(file)

        self.master_data = toolbox.sort_dictionary(self.master_data, "distance")


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

        athlete_summary = toolbox.sort_dictionary(athlete_summary, "distance")

        return athlete_summary

    def create_aggregated_summary(self):
        """Method to create aggregated summary for provided dataset"""
        aggregated_summary = {"moving_time": 0,
                              "distance": 0,
                              "elevation_gain": 0,
                              "activities": 0,
                              "athletes": 0,
                              "co2_saved": 0
                              }

        for record in self.dataset.values():
            aggregated_summary["moving_time"] += record["moving_time"]
            aggregated_summary["distance"] += toolbox.format_distance(record["distance"])
            aggregated_summary["elevation_gain"] += record["elevation_gain"]
            aggregated_summary["activities"] += record["activities"]

        aggregated_summary["athletes"] = self.total_athletes
        aggregated_summary["co2_saved"] = toolbox.calculate_co2_saved(aggregated_summary["distance"])

        return aggregated_summary

    def get_changed_ranking(self):
        """Method to get rankings for athletes in provided dataset"""
        ranking_current_week = []
        ranking_previous_week = []
        rankings = {}

        for value in self.dataset.values():

            if value["week_number"] == int(toolbox.get_current_week_number()):
                ranking_current_week.append(value["athlete_name"])

            if value["week_number"] == int(toolbox.get_current_week_number())-1:
                ranking_previous_week.append(value["athlete_name"])

        print(toolbox.get_current_week_number())
        for value in self.dataset.values():
            if int(CAMPAIGN_WEEK_START) == int(toolbox.get_current_week_number()):
                rankings.update({value["athlete_name"]: ""})
            else:
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
    def __init__(self, name_of_team, dataset, results_object, outfile):
        self.team_name = name_of_team
        self.dataset = dataset
        self.results = results_object
        self.outfile = outfile
        self.create_html_file()

    def create_aggregated_results_table(self):
        """Method to create html table for aggregated results"""
        aggregated_results_table = f"""<table class='table-aggregated'>
                <tr>
                    <td>👥 {self.results.aggregated_summary['athletes']} kolleger</td>
                    <td>🏁 {self.results.aggregated_summary['activities']} aktiviteter</td>
                    <td>⏳ {toolbox.format_duration(self.results.aggregated_summary['moving_time'])} (t:m)</td></tr>
                <tr>
                    <td>📏 {round(self.results.aggregated_summary['distance'], 1)} km</td>
                    <td>🧗 {self.results.aggregated_summary['elevation_gain']} høydemeter</td>
                    <td>🌱 {self.results.aggregated_summary['co2_saved']} kg CO2 spart</td></tr>
            </table>"""

        return aggregated_results_table

    def create_current_week_results_table(self):
        """Method to create html table for current week results"""
        current_week_results_table = """<table class='table'>
                <tr><th>Navn</th>
                    <th>Aktiviteter</th>
                    <th>Varighet (t:m)</th>
                    <th>Distanse (km)</th>
                    <th>Høydemeter</th>
                </tr>
                """

        for value in self.dataset.values():
            if int(value["week_number"]) == int(toolbox.get_current_week_number()):
                current_week_results_table += (f"""<tr>
                    <td>{self.results.rankings[value['athlete_name']]} {value['athlete_name']}</td>
                    <td>{value['activities']}</td>
                    <td>{toolbox.format_duration(value['moving_time'])} {toolbox.get_tickets(value['tickets'])}</td>
                    <td>{toolbox.format_distance(value['distance'])}</td>
                    <td>{value['elevation_gain']}</td>
                </tr>
                """
                                               )
        current_week_results_table += "</table>"

        return current_week_results_table

    def create_previous_week_results_table(self):
        """Method to create html table for previous week results"""
        previous_week_results_table = """<table class='table'>
                <tr><th>Navn</th>
                    <th>Aktiviteter</th>
                    <th>Varighet (t:m)</th>
                    <th>Distanse (km)</th>
                    <th>Høydemeter</th>
                </tr>
                """

        for value in self.dataset.values():
            if int(value["week_number"]) == int(toolbox.get_current_week_number())-1:
                previous_week_results_table += (f"""<tr>
                    <td>{value['athlete_name']}</td>
                    <td>{value['activities']}</td>
                    <td>{toolbox.format_duration(value['moving_time'])} {toolbox.get_tickets(value['tickets'])}</td>
                    <td>{toolbox.format_distance(value['distance'])}</td>
                    <td>{value['elevation_gain']}</td>
                </tr>
                """
                                                )
        previous_week_results_table += "</table>"

        return previous_week_results_table

    def create_complete_results_table(self):
        """Method to create html table for complete results"""
        complete_results_table = """<table class='table'>
                <tr>
                    <th>Navn</th>
                    <th>Aktiviteter</th>
                    <th>Varighet (t:m)</th>
                    <th>Lodd</th>
                    <th>Distanse (km)</th>
                    <th>Høydemeter</th>
                </tr>
                """

        for athlete_name, summary_data in self.results.athlete_summary.items():
            complete_results_table += (f"""<tr>
                    <td>{athlete_name}</td>
                    <td>{summary_data['activities']}</td>
                    <td>{toolbox.format_duration(summary_data['moving_time'])}</td>
                    <td>{summary_data['tickets']}</td>
                    <td>{toolbox.format_distance(summary_data['distance'])}</td>
                    <td>{summary_data['elevation_gain']}</td>
                </tr>
                """
                                       )
        complete_results_table += "</table>"

        return complete_results_table

    def assemble_html_content(self):
        """Method to assemble html content to one block"""
        if self.team_name == "Alle deltakere":
            heading_specific = self.team_name
        else:
            heading_specific = f'Lag {self.team_name}'

        html_content = textwrap.dedent(f"""\
        ---
        layout: default
        title: Resultater {heading_specific}
        nav_order: 1
        ---

        # Vår 2024 - Resultater: {heading_specific}

        Lite data? Vi simulerte ny aksjonsstart uke 12 (18. mars 2024). Informasjon om [aktivitetskampanjen](docs/info.md). For å delta må du også bli medlem i [Helsedirektoratets klubb på Strava](https://www.strava.com/clubs/754665).

        <div id="aggregated data">
            <h2>Aggregerte data</h2>
            {self.create_aggregated_results_table()}
        </div>
        <div id="current_week_results">
            <h2>Ukens resultater (uke {int(toolbox.get_current_week_number())})</h2>
            {self.create_current_week_results_table()}
        </div>
        <div id="previous_week_results">
            <h2>Forrige ukes resultater (uke {int(toolbox.get_current_week_number())-1})</h2>
            {self.create_previous_week_results_table()}
        </div>
        <div id="complete_results">
            <h2>Resultater hele perioden</h2>
            {self.create_complete_results_table()}
        </div>
        """)

        return html_content

    def create_html_file(self):
        """Method to write html block to file"""
        with open(self.outfile, 'w', encoding='utf-8') as html_file:
            html_file.write(self.assemble_html_content())

        print(f"HTML file created at: {self.outfile}")


if __name__ == "__main__":

    toolbox = Toolbox()
    datastore = Datastore()

    print(f"Teams feature is {TEAMS_FEATURE}")

    if not datastore.master_data:
        print(f"Dictionary in file is empty: {RESULTS_FILE}")

    # Create objects for all athletes across teams
    results_all_teams = Results(datastore.master_data)
    outfile_index = Template("Alle deltakere", datastore.master_data, results_all_teams, INDEX_FILE)

    # Create objects for each team
    if TEAMS_FEATURE is True:
        for team_name in toolbox.get_teams():
            team_data = {}

            for keys, values in datastore.master_data.items():
                if values["team"] == team_name:
                    team_data[keys] = values

            team_results = Results(team_data)
            team_outfile = Template(team_name, team_data, team_results, f'team_{team_name}.md')

    # Placeholder to produce comparison across teams, use Results and Template class
