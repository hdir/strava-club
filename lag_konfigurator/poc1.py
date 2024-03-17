from fastapi import FastAPI, HTTPException, Form, Request
from fastapi.responses import HTMLResponse
import requests
import json
from typing import Dict, List, Optional
from fastapi.templating import Jinja2Templates

app = FastAPI()

# Create an instance of Jinja2Templates
templates = Jinja2Templates(directory="templates")


# Define the fetch_json_data function to fetch JSON data from URL
def fetch_json_data(url: str) -> dict:
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        raise HTTPException(status_code=response.status_code, detail="Failed to fetch JSON data")

# Initial fetch of JSON data
json_data = fetch_json_data("https://raw.githubusercontent.com/hdir/strava-club/main/data/result/results.json")

# Step 2: Endpoint to write team name to JSON file
@app.post("/create_team/")
async def create_team(team_name: str = Form(...)):
    if len(team_name) < 3:
        raise HTTPException(status_code=400, detail="Team name must be at least 3 characters long")

    # Check if team_name already exists in team data
    with open("team_data.json", "r") as f:
        team_data = json.load(f)
    if team_name in team_data:
        raise HTTPException(status_code=400, detail="Team name already exists")

    # Add team_name to team data
    team_data[team_name] = {}

    # Write updated team data to JSON file
    with open("team_data.json", "w") as f:
        json.dump(team_data, f, indent=4)

    return {"message": "Team created successfully"}

# Step 3: Endpoint to update team members in JSON file
# Endpoint to render the HTML form with dynamically populated team names
@app.route("/add_members/", methods=["GET", "POST"])
async def show_add_members_form(request: Request):
    if request.method == "GET":
        # Read team names from team_data.json
        with open("team_data.json", "r") as f:
            team_data = json.load(f)
        team_names = list(team_data.keys())

        # Extract unique athlete names from team data
        all_athlete_names = []
        for team_info in team_data.values():
            all_athlete_names.extend(team_info.get("athletes", []))
        unique_athlete_names = list(set(all_athlete_names))

        # Render HTML form with team names and athlete names
        return templates.TemplateResponse(
            "add_members_form.html",
            {"request": request, "team_names": team_names, "unique_athlete_names": unique_athlete_names, "json_data": json_data}
        )
    elif request.method == "POST":
        form = await request.form()
        team_name = form["team_select"]
        selected_athletes = form.getlist("athlete_select")

        # Read team data from team_data.json
        with open("team_data.json", "r") as f:
            team_data = json.load(f)

        # Update selected athletes for the corresponding team
        team_data[team_name]["athletes"] = selected_athletes

        # Write updated team data to team_data.json
        with open("team_data.json", "w") as f:
            json.dump(team_data, f, indent=4)

        # Extract unique athlete names from team data again
        all_athlete_names = []
        for team_info in team_data.values():
            all_athlete_names.extend(team_info.get("athletes", []))
        unique_athlete_names = list(set(all_athlete_names))

        # Render HTML form with success message
        return templates.TemplateResponse(
            "add_members_form.html",
            {"request": request, "team_names": list(team_data.keys()), "unique_athlete_names": unique_athlete_names, "message": "Members added successfully", "json_data": json_data}
        )





# Step 1: Read the content of the JSON file into a dictionary
def fetch_json_data(url: str) -> Dict:
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        raise HTTPException(status_code=response.status_code, detail="Failed to fetch JSON data")

# Step 4: Endpoint to return the JSON file with team names and members
@app.get("/get_team_data/", response_class=HTMLResponse)
async def get_team_data():
    with open("team_data.json", "r") as f:
        team_data = f.read()
    
    return team_data

# HTML interface
html_content = """
<!DOCTYPE html>
<html>
    <head>
        <title>Team Management</title>
    </head>
    <body>
        <h1>Create Team</h1>
        <form action="/create_team/" method="post">
            <label for="team_name">Team Name:</label><br>
            <input type="text" id="team_name" name="team_name" required minlength="3"><br>
            <button type="submit">Create Team</button>
        </form>

        
        
        
    </body>
</html>
"""

@app.get("/", response_class=HTMLResponse)
async def get_html():
    return HTMLResponse(content=html_content)
