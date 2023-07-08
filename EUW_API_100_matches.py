import os
import time
import requests
import pandas as pd
import numpy as np
from tqdm import tqdm

api_key = "x"
username = "x"

api_key = input("Enter your API key: ")
username = input("Enter your username: ")
username = username.replace(" ", "%20")
print()

api_AccountURL = "https://euw1.api.riotgames.com/lol/summoner/v4/summoners/by-name/" + username

api_AccountURLandAPI = api_AccountURL + '?api_key=' + api_key

responseAccount = requests.get(api_AccountURLandAPI)
player_info = responseAccount.json()

puuid = player_info['puuid']

file_name = "team_data.csv"
file_path = username + "_" + file_name

if os.path.exists(file_path):
    os.remove(file_path)

# Initialize StartNumber
StartNumber = 0
n=0

# Perform the loop 2 times for 100 matches
for _ in range(2):
    
    for _ in tqdm(range(100), desc="Gathering 100 matches", unit="seconds"):
        time.sleep(1.3)

    # Initialize combined_data for each iteration
    combined_data = []

    api_MatchHistory = "https://europe.api.riotgames.com/lol/match/v5/matches/by-puuid/" + puuid + "/ids?start=" + str(StartNumber) + "&count=" + "50"

    api_MatchHistoryAPI = api_MatchHistory + '&api_key=' + api_key

    responseMatchHistory = requests.get(api_MatchHistoryAPI)
    match_ids = responseMatchHistory.json()

    for _ in tqdm(range(100), desc="Extracting match info'", unit="seconds"):
        time.sleep(1.3)

    for i in range(50):
        api_MatchData = "https://europe.api.riotgames.com/lol/match/v5/matches/" + match_ids[i] + '?api_key=' + api_key
        responseMatchData = requests.get(api_MatchData)
        match_data = responseMatchData.json()

        api_MatchTimeline = "https://europe.api.riotgames.com/lol/match/v5/matches/" + match_ids[i] + '/timeline' + '?api_key=' + api_key
        responseMatchTimeline = requests.get(api_MatchTimeline)
        match_timeline = responseMatchTimeline.json()

        if match_data["info"]["gameMode"] == "CLASSIC" and match_data["info"]["gameDuration"] >= 840 and match_data["info"]["gameDuration"] <=7200:

            team_1 = {"Gold": 0, "Level": 0, "Minions": 0, "Jungle_minions": 0, "Kills": 0, "Assists": 0, "Deaths": 0, "Plates": 0, "Towers": 0, "Dragons": 0, "Heralds": 0, "Sight_wards": 0, "Control_wards": 0}
            team_2 = {"Gold": 0, "Level": 0, "Minions": 0, "Jungle_minions": 0, "Kills": 0, "Assists": 0, "Deaths": 0, "Plates": 0, "Towers": 0, "Dragons": 0, "Heralds": 0, "Sight_wards": 0, "Control_wards": 0}

            frame_index = min(14, len(match_timeline["info"]["frames"]) - 1)

            for j in range(1, 6):
                participant_frame = match_timeline["info"]["frames"][frame_index]["participantFrames"].get(str(j))
                if participant_frame is not None:
                    team_1["Gold"] += participant_frame["totalGold"]
                    team_1["Level"] += participant_frame["level"]
                    team_1["Minions"] += participant_frame["minionsKilled"]
                    team_1["Jungle_minions"] += participant_frame["jungleMinionsKilled"]

            for j in range(6, 11):
                participant_frame = match_timeline["info"]["frames"][frame_index]["participantFrames"].get(str(j))
                if participant_frame is not None:
                    team_2["Gold"] += participant_frame["totalGold"]
                    team_2["Level"] += participant_frame["level"]
                    team_2["Minions"] += participant_frame["minionsKilled"]
                    team_2["Jungle_minions"] += participant_frame["jungleMinionsKilled"]

            team_1["Level"] /= 5
            team_2["Level"] /= 5

            team_1["Gold_diff"] = team_1["Gold"] - team_2["Gold"]
            team_2["Gold_diff"] = team_2["Gold"] - team_1["Gold"]
            
            #The rest of the info is not available in the minute 14 data, so it has to be taken minute by minute

                    #For each minute a list of events its presented, so we can iterate through each event and get necessary info
            for j in match_timeline["info"]["frames"][i]["events"]:

                                #Get Kills, deaths and assists. Each event has a KillerID. 
                                #If the Killer ID is between 1 and 5 is corresponds to team1, if its bigger than 5 is for team2. This pattern is repeated through out the iteration of events
                                if (j["type"] == "CHAMPION_KILL") and (1 <= j["killerId"] <= 5):
                                    team_1["Kills"] += 1
                                    team_2["Deaths"] += 1
                                    try:
                                        team_1["Assists"] += len(j["assistingParticipantIds"])
                                    except:
                                        pass
                                if (j["type"] == "CHAMPION_KILL") and (j["killerId"] > 5):
                                    team_2["Kills"] += 1
                                    team_1["Deaths"] += 1
                                    try:
                                        team_2["Assists"] += len(j["assistingParticipantIds"])
                                    except:
                                        pass
                                
                                #Get Turret plates destroyed
                                if (j["type"] == "TURRET_PLATE_DESTROYED") and (1 <= j["killerId"] <= 5):
                                    team_1["Plates"] += 1
                                if (j["type"] == "TURRET_PLATE_DESTROYED") and (j["killerId"] > 5):
                                    team_2["Plates"] += 1
                                    
                                if (j["type"] == "BUILDING_KILL") and (j["teamId"] == 200):
                                    team_1["Towers"] += 1
                                if (j["type"] == "BUILDING_KILL") and (j["teamId"] == 100):
                                    team_2["Towers"] += 1 
                                
                                #Get Dragons and Heralds
                                if (j["type"] == "ELITE_MONSTER_KILL") and (1 <= j["killerId"] <= 5):
                                    if j["monsterType"] == "DRAGON":
                                        team_1["Dragons"] += 1
                                    elif j["monsterType"] == "RIFTHERALD":
                                        team_1["Heralds"] += 1
                                    
                                if (j["type"] == "ELITE_MONSTER_KILL") and (j["killerId"] > 5):
                                    if j["monsterType"] == "DRAGON":
                                        team_2["Dragons"] += 1
                                    elif j["monsterType"] == "RIFTHERALD":
                                        team_2["Heralds"] += 1                
                                
                                #Get wards placed
                                if (j["type"] == "WARD_PLACED" and j["wardType"] == "CONTROL_WARD") and (1 <= j["creatorId"] <= 5):
                                    team_1["Control_wards"] += 1
                                if (j["type"] == "WARD_PLACED" and j["wardType"] == "CONTROL_WARD") and (j["creatorId"] > 5):
                                    team_2["Control_wards"] += 1
                                    
                                if (j["type"] == "WARD_PLACED" and (j["wardType"] == "SIGHT_WARD" or j["wardType"] == "YELLOW_TRINKET")) and (1 <= j["creatorId"] <= 5):
                                    team_1["Sight_wards"] += 1
                                if (j["type"] == "WARD_PLACED" and (j["wardType"] == "SIGHT_WARD" or j["wardType"] == "YELLOW_TRINKET")) and (j["creatorId"] > 5):
                                    team_2["Sight_wards"] += 1

            if match_data["info"]["teams"][0]["win"]:
                team_1["Win"] = 1
                team_2["Win"] = 0
            else:
                team_1["Win"] = 0
                team_2["Win"] = 1

            team_1_data = {
                'Gold': team_1["Gold"],
                'Level': team_1["Level"],
                'Minions': team_1["Minions"],
                'Jungle_minions': team_1["Jungle_minions"],
                'Kills': team_1["Kills"],
                'Assists': team_1["Assists"],
                'Deaths': team_1["Deaths"],
                'Plates': team_1["Plates"],
                'Towers': team_1["Towers"],
                'Dragons': team_1["Dragons"],
                'Heralds': team_1["Heralds"],
                'Sight_wards': team_1["Sight_wards"],
                'Control_wards': team_1["Control_wards"],
                'Gold_diff': team_1["Gold_diff"],
                'Win': team_1["Win"]
            }

            team_2_data = {
                'Gold': team_2["Gold"],
                'Level': team_2["Level"],
                'Minions': team_2["Minions"],
                'Jungle_minions': team_2["Jungle_minions"],
                'Kills': team_2["Kills"],
                'Assists': team_2["Assists"],
                'Deaths': team_2["Deaths"],
                'Plates': team_2["Plates"],
                'Towers': team_2["Towers"],
                'Dragons': team_2["Dragons"],
                'Heralds': team_2["Heralds"],
                'Sight_wards': team_2["Sight_wards"],
                'Control_wards': team_2["Control_wards"],
                'Gold_diff': team_2["Gold_diff"],
                'Win': team_2["Win"]
            }

            combined_data.append(team_1_data)
            combined_data.append(team_2_data)

    # Update StartNumber and EndNumber for the next iteration
    StartNumber += 50
    n=n+1
    print("Loop", n)
    print()

    # Save the combined data to a CSV file
    combined_df = pd.DataFrame(combined_data)
    combined_df.to_csv(file_path, index=False, mode='a', header=not os.path.exists(file_path))