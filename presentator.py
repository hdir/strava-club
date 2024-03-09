import json

# Load the JSON content from the file
with open('results.json', 'r') as json_file:
    data = json.load(json_file)

# Create a dictionary to store the accumulated data for each athlete
athlete_summary = {}

# Accumulate data for each athlete across all weeks
for key, value in data.items():
    athlete_name = value["athlete_name"]

    if athlete_name not in athlete_summary:
        athlete_summary[athlete_name] = {
            'activities': 0,
            'distance': 0,
            'distance_longest': 0,
            'elevation_gain': 0
        }

    athlete_summary[athlete_name]['activities'] += value['activities']
    athlete_summary[athlete_name]['distance'] += value['distance']
    athlete_summary[athlete_name]['distance_longest'] += value['distance_longest']
    athlete_summary[athlete_name]['elevation_gain'] += value['elevation_gain']

# Create HTML tables for each section
ukens_resultater_table = "<table border='1'><tr><th>Athlete Name</th><th>Total Activities</th><th>Total Distance</th><th>Total Distance Longest</th><th>Total Elevation Gain</th></tr>"
for key, value in data.items():
    if value["week_number"] == "09":
        ukens_resultater_table += f"<tr><td>{value['athlete_name']}</td><td>{value['activities']}</td><td>{value['distance']}</td><td>{value['distance_longest']}</td><td>{value['elevation_gain']}</td></tr>"
ukens_resultater_table += "</table>"

forrige_ukes_resultater_table = "<table border='1'><tr><th>Athlete Name</th><th>Total Activities</th><th>Total Distance</th><th>Total Distance Longest</th><th>Total Elevation Gain</th></tr>"
for key, value in data.items():
    if value["week_number"] == "10":
        forrige_ukes_resultater_table += f"<tr><td>{value['athlete_name']}</td><td>{value['activities']}</td><td>{value['distance']}</td><td>{value['distance_longest']}</td><td>{value['elevation_gain']}</td></tr>"
forrige_ukes_resultater_table += "</table>"

resultater_hele_perioden_table = "<table border='1'><tr><th>Athlete Name</th><th>Total Activities</th><th>Total Distance</th><th>Total Distance Longest</th><th>Total Elevation Gain</th></tr>"
for athlete_name, summary_data in athlete_summary.items():
    resultater_hele_perioden_table += (
        f"<tr><td>{athlete_name}</td>"
        f"<td>{summary_data['activities']}</td>"
        f"<td>{summary_data['distance']}</td>"
        f"<td>{summary_data['distance_longest']}</td>"
        f"<td>{summary_data['elevation_gain']}</td></tr>"
    )
resultater_hele_perioden_table += "</table>"

# HTML content with the summarized table
html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>My HTML Page</title>
</head>
<body>
    <section id="ukens_resultater">
        <h2>Ukens resultater</h2>
        {ukens_resultater_table}
    </section>

    <section id="forrige_ukes_resultater">
        <h2>Forrige ukes resultater</h2>
        {forrige_ukes_resultater_table}
    </section>

    <section id="resultater_hele_perioden">
        <h2>Resultater hele perioden</h2>
        {resultater_hele_perioden_table}
    </section>
</body>
</html>
"""

# Specify the file path where you want to save the HTML file
file_path = 'output_with_summarized_table.html'

# Write the HTML content to the file
with open(file_path, 'w', encoding='utf-8') as html_file:
    html_file.write(html_content)

print(f"HTML file with summarized table created at: {file_path}")
