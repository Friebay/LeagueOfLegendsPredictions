import os
import time
import requests
import random
import pandas as pd
import numpy as np
from tqdm import tqdm

def get_minute_stats(minute, match_timeline, match_data):
  
    # Initialize stats for both teams
    team_1_stats = {"Gold": 0, "Level": 0, "Minions": 0, "Kills": 0, "Assists": 0, "Deaths": 0, "Towers": 0, "Dragons": 0, "Heralds": 0, "Barons": 0}
    team_2_stats = {"Gold": 0, "Level": 0, "Minions": 0, "Kills": 0, "Assists": 0, "Deaths": 0, "Towers": 0, "Dragons": 0, "Heralds": 0, "Barons": 0}
    
     # Calculate the frame index, ensuring it does not exceed the maximum frame index
    timeline_frames_length = len(match_timeline["info"]["frames"])
    frame_index = min(minute, timeline_frames_length - 1)
    
     # Collect stats for team 1
    for j in range(1, 6):
        participant_frame = match_timeline["info"]["frames"][frame_index]["participantFrames"].get(str(j))
        if participant_frame is not None:
            team_1_stats["Gold"] += participant_frame["totalGold"]
            team_1_stats["Level"] += participant_frame["level"]
            team_1_stats["Minions"] += participant_frame["minionsKilled"] + participant_frame["jungleMinionsKilled"]
            
     # Collect stats for team 2
    for j in range(6, 11):
        participant_frame = match_timeline["info"]["frames"][frame_index]["participantFrames"].get(str(j))
        if participant_frame is not None:
            team_2_stats["Gold"] += participant_frame["totalGold"]
            team_2_stats["Level"] += participant_frame["level"]
            team_2_stats["Minions"] += participant_frame["minionsKilled"] + participant_frame["jungleMinionsKilled"]
            
     # Calculate average level for each team
    team_1_stats["Level"] /= 5
    team_2_stats["Level"] /= 5
    
     # Calculate gold difference between teams
    team_1_stats["Gold_diff"] = team_1_stats["Gold"] - team_2_stats["Gold"]
    team_2_stats["Gold_diff"] = team_2_stats["Gold"] - team_1_stats["Gold"]
    
     # Iterate through each minute's events to collect remaining stats
    for i in range(1, minute+1):
        for event in match_timeline["info"]["frames"][i]["events"]:
            if event["type"] == "CHAMPION_KILL":
              
                if 1 <= event["killerId"] <= 5:  # Killer is from team 1
                    team_1_stats["Kills"] += 1
                    team_2_stats["Deaths"] += 1
                    team_1_stats["Assists"] += len(event.get("assistingParticipantIds", []))
                    
                else:  # Killer is from team 2
                    team_2_stats["Kills"] += 1
                    team_1_stats["Deaths"] += 1
                    team_2_stats["Assists"] += len(event.get("assistingParticipantIds", []))
            elif event["type"] == "BUILDING_KILL":
               
                if event["teamId"] == 200:  # Building belonged to team 2
                    team_1_stats["Towers"] += 1
                else:  # Building belonged to team 1
                    team_2_stats["Towers"] += 1 
                    
            elif event["type"] == "ELITE_MONSTER_KILL":
                if event["monsterType"] == "DRAGON":
                    if 1 <= event["killerId"] <= 5:  # Killer is from team 1
                        team_1_stats["Dragons"] += 1
                    else:  # Killer is from team 2
                        team_2_stats["Dragons"] += 1
                        
                elif event["monsterType"] == "RIFTHERALD":
                    if 1 <= event["killerId"] <= 5:  # Killer is from team 1
                        team_1_stats["Heralds"] += 1
                    else:  # Killer is from team 2
                        team_2_stats["Heralds"] += 1
                        
                elif event["monsterType"] == "BARON_NASHOR":
                    if 1 <= event["killerId"] <= 5:  # Killer is from team 1
                        team_1_stats["Barons"] += 1
                    else:  # Killer is from team 2
                        team_2_stats["Barons"] += 1
                        
     # Determine which team won
    if match_data["info"]["teams"][0]["win"]:
        team_1_stats["Win"] = 1
        team_2_stats["Win"] = 0
    else:
        team_1_stats["Win"] = 0
        team_2_stats["Win"] = 1
        
    return team_1_stats, team_2_stats

with open("API.txt", "r") as file:
    api_key = file.read().strip()

with open("name.txt", "r") as file:
    username = file.read().strip()
    
username = username.replace(" ", "%20")
print()

api_AccountURL = "https://euw1.api.riotgames.com/lol/summoner/v4/summoners/by-name/" + username

api_AccountURLandAPI = api_AccountURL + '?api_key=' + api_key

responseAccount = requests.get(api_AccountURLandAPI)
player_info = responseAccount.json()

puuid = player_info['puuid']

file_paths = [f"{username}_team_data_{i}min.csv" for i in range(1, 45)]

for file_path in file_paths:
    if os.path.exists(file_path):
        os.remove(file_path)

# Initialize StartNumber
StartNumber = 0
n=0

# Perform the loop 6 times for 300 matches
for _ in range(2):
    
    for _ in tqdm(range(100), desc="Gathering 50 matches", unit="seconds"):
        time.sleep(1.2 + random.uniform(0.005, 0.3))

    combined_data = [[] for i in range(46)]

    api_MatchHistory = "https://europe.api.riotgames.com/lol/match/v5/matches/by-puuid/" + puuid + "/ids?start=" + str(StartNumber) + "&count=" + "50"

    api_MatchHistoryAPI = api_MatchHistory + '&api_key=' + api_key

    responseMatchHistory = requests.get(api_MatchHistoryAPI)
    match_ids = responseMatchHistory.json()

    for _ in tqdm(range(100), desc="Extracting match info", unit="seconds"):
        time.sleep(1.2 + random.uniform(0.005, 0.3))

    for i in range(50):
        api_MatchData = "https://europe.api.riotgames.com/lol/match/v5/matches/" + match_ids[i] + '?api_key=' + api_key
        responseMatchData = requests.get(api_MatchData)
        match_data = responseMatchData.json()

        api_MatchTimeline = "https://europe.api.riotgames.com/lol/match/v5/matches/" + match_ids[i] + '/timeline' + '?api_key=' + api_key
        responseMatchTimeline = requests.get(api_MatchTimeline)
        match_timeline = responseMatchTimeline.json()
        
        # if match is longer than 1 minutes, then run the code
        if match_data["info"]["gameMode"] == "CLASSIC" and match_data["info"]["gameDuration"] >= 60 and match_data["info"]["gameDuration"] <=5400:
            
            minutes = 1
            team_1_stats, team_2_stats = get_minute_stats(minutes, match_timeline, match_data)
            
            combined_data[minutes-1].append(team_1_stats)
            combined_data[minutes-1].append(team_2_stats)
        
        # if match is longer than 2 minutes, then run the code
        if match_data["info"]["gameMode"] == "CLASSIC" and match_data["info"]["gameDuration"] >= 120 and match_data["info"]["gameDuration"] <=5400:

            minutes = 2
            team_1_stats, team_2_stats = get_minute_stats(minutes, match_timeline, match_data)
            
            combined_data[minutes-1].append(team_1_stats)
            combined_data[minutes-1].append(team_2_stats)
        
        # if match is longer than 3 minutes, then run the code
        if match_data["info"]["gameMode"] == "CLASSIC" and match_data["info"]["gameDuration"] >= 180 and match_data["info"]["gameDuration"] <=5400:

            minutes = 3
            team_1_stats, team_2_stats = get_minute_stats(minutes, match_timeline, match_data)
            
            combined_data[minutes-1].append(team_1_stats)
            combined_data[minutes-1].append(team_2_stats)
        
        # if match is longer than 4 minutes, then run the code
        if match_data["info"]["gameMode"] == "CLASSIC" and match_data["info"]["gameDuration"] >= 240 and match_data["info"]["gameDuration"] <=5400:

            minutes = 4
            team_1_stats, team_2_stats = get_minute_stats(minutes, match_timeline, match_data)
            
            combined_data[minutes-1].append(team_1_stats)
            combined_data[minutes-1].append(team_2_stats)
            
        # if match is longer than 5 minutes, then run the code
        if match_data["info"]["gameMode"] == "CLASSIC" and match_data["info"]["gameDuration"] >= 300 and match_data["info"]["gameDuration"] <=5400:

            minutes = 5
            team_1_stats, team_2_stats = get_minute_stats(minutes, match_timeline, match_data)
            
            combined_data[minutes-1].append(team_1_stats)
            combined_data[minutes-1].append(team_2_stats)
            
        # if match is longer than 6 minutes, then run the code
        if match_data["info"]["gameMode"] == "CLASSIC" and match_data["info"]["gameDuration"] >= 360 and match_data["info"]["gameDuration"] <=5400:

            minutes = 6
            team_1_stats, team_2_stats = get_minute_stats(minutes, match_timeline, match_data)
            
            combined_data[minutes-1].append(team_1_stats)
            combined_data[minutes-1].append(team_2_stats)
            
        # if match is longer than 14 minutes, then run the code
        if match_data["info"]["gameMode"] == "CLASSIC" and match_data["info"]["gameDuration"] >= 840 and match_data["info"]["gameDuration"] <=5400:

            minutes = 14
            team_1_stats, team_2_stats = get_minute_stats(minutes, match_timeline, match_data)
            
            combined_data[minutes-1].append(team_1_stats)
            combined_data[minutes-1].append(team_2_stats)
            
        # if match is longer than 28 minutes, then run the code
        if match_data["info"]["gameMode"] == "CLASSIC" and match_data["info"]["gameDuration"] >= 1680 and match_data["info"]["gameDuration"] <=5400:

            minutes = 28
            team_1_stats, team_2_stats = get_minute_stats(minutes, match_timeline, match_data)
            
            combined_data[minutes-1].append(team_1_stats)
            combined_data[minutes-1].append(team_2_stats)
            
        # if match is longer than 42 minutes, then run the code
        if match_data["info"]["gameMode"] == "CLASSIC" and match_data["info"]["gameDuration"] >= 2520 and match_data["info"]["gameDuration"] <=5400:

            minutes = 42
            team_1_stats, team_2_stats = get_minute_stats(minutes, match_timeline, match_data)
            
            combined_data[minutes-1].append(team_1_stats)
            combined_data[minutes-1].append(team_2_stats)

    # Update StartNumber and EndNumber for the next iteration
    StartNumber += 50
    n=n+1
    print("Loop", n)
    print()

    # Save the combined data to a CSV file
    combined_data = [pd.DataFrame(combined_data[i]) for i in range(0, 46)]

    for df, file_path in zip(combined_data, file_paths):
        df.to_csv(file_path, index=False, mode='a', header=not os.path.exists(file_path))    
    
time.sleep(600)