import os
import time
import requests
import random
import pandas as pd
import numpy as np
from tqdm import tqdm

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

file_path_4min = username + "_team_data_4min.csv"
file_path_14min = username + "_team_data_14min.csv"
file_path_28min = username + "_team_data_28min.csv"
file_path_42min = username + "_team_data_42min.csv"


if os.path.exists(file_path_4min):
    os.remove(file_path_4min)

if os.path.exists(file_path_14min):
    os.remove(file_path_14min)
    
if os.path.exists(file_path_28min):
    os.remove(file_path_28min)
    
if os.path.exists(file_path_42min):
    os.remove(file_path_42min)

# Initialize StartNumber
StartNumber = 0
n=0

# Perform the loop 6 times for 300 matches
for _ in range(6):
    
    for _ in tqdm(range(100), desc="Gathering 50 matches", unit="seconds"):
        time.sleep(1.2 + random.uniform(0.005, 0.3))

    combined_data_4min = []
    combined_data_14min = []
    combined_data_28min = []
    combined_data_42min = []

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
        
        
        # if match is longer than 4 minutes, then run the code
        if match_data["info"]["gameMode"] == "CLASSIC" and match_data["info"]["gameDuration"] >= 240 and match_data["info"]["gameDuration"] <=5400:

            team_1_4min = {"Gold": 0, "Level": 0, "Minions": 0, "Kills": 0, "Assists": 0, "Deaths": 0, "Towers": 0, "Dragons": 0, "Heralds": 0, "Barons": 0}
            team_2_4min = {"Gold": 0, "Level": 0, "Minions": 0, "Kills": 0, "Assists": 0, "Deaths": 0, "Towers": 0, "Dragons": 0, "Heralds": 0, "Barons": 0}

            # Determine the minute that we are looking for
            max_frame_index = 4
            # Get the length of the frames in the match timeline
            timeline_frames_length = len(match_timeline["info"]["frames"])
            # Calculate the frame index, ensuring it does not exceed the maximum frame index
            frame_index = min(max_frame_index, timeline_frames_length - 1)


            for j in range(1, 6):
                participant_frame = match_timeline["info"]["frames"][frame_index]["participantFrames"].get(str(j))
                if participant_frame is not None:
                    team_1_4min["Gold"] += participant_frame["totalGold"]
                    team_1_4min["Level"] += participant_frame["level"]
                    team_1_4min["Minions"] += participant_frame["minionsKilled"]
                    team_1_4min["Minions"] += participant_frame["jungleMinionsKilled"]

            for j in range(6, 11):
                participant_frame = match_timeline["info"]["frames"][frame_index]["participantFrames"].get(str(j))
                if participant_frame is not None:
                    team_2_4min["Gold"] += participant_frame["totalGold"]
                    team_2_4min["Level"] += participant_frame["level"]
                    team_2_4min["Minions"] += participant_frame["minionsKilled"]
                    team_2_4min["Minions"] += participant_frame["jungleMinionsKilled"]

            team_1_4min["Level"] /= 5
            team_2_4min["Level"] /= 5

            team_1_4min["Gold_diff"] = team_1_4min["Gold"] - team_2_4min["Gold"]
            team_2_4min["Gold_diff"] = team_2_4min["Gold"] - team_1_4min["Gold"]
            
            #The rest of the info is not available in the minute 14 data, so it has to be scarped minute by minute that why we iterate from 1 to 15 (15 minute is not taken into account, 15 is because how Python works)
            for i in range(1, 5):

                    #For each minute a list of events its presented, so we can iterate through each event and get necessary info
                            for j in match_timeline["info"]["frames"][i]["events"]:

                                #If the Killer ID is between 1 and 5 is corresponds to team1, if its bigger than 5 is for team2. This pattern is repeated through out the iteration of events
                                if (j["type"] == "CHAMPION_KILL") and (1 <= j["killerId"] <= 5):
                                    team_1_4min["Kills"] += 1
                                    team_2_4min["Deaths"] += 1
                                    try:
                                        team_1_4min["Assists"] += len(j["assistingParticipantIds"])
                                    except:
                                        pass
                                if (j["type"] == "CHAMPION_KILL") and (j["killerId"] > 5):
                                    team_2_4min["Kills"] += 1
                                    team_1_4min["Deaths"] += 1
                                    try:
                                        team_2_4min["Assists"] += len(j["assistingParticipantIds"])
                                    except:
                                        pass
                                    
                                if (j["type"] == "BUILDING_KILL") and (j["teamId"] == 200):
                                    team_1_4min["Towers"] += 1
                                if (j["type"] == "BUILDING_KILL") and (j["teamId"] == 100):
                                    team_2_4min["Towers"] += 1 
                                
                                #Get Dragons and Heralds
                                if (j["type"] == "ELITE_MONSTER_KILL") and (1 <= j["killerId"] <= 5):
                                    if j["monsterType"] == "DRAGON":
                                        team_1_4min["Dragons"] += 1
                                    elif j["monsterType"] == "RIFTHERALD":
                                        team_1_4min["Heralds"] += 1
                                    elif j["monsterType"] == "BARON_NASHOR":
                                        team_1_4min["Barons"] += 1
                                    
                                    
                                if (j["type"] == "ELITE_MONSTER_KILL") and (j["killerId"] > 5):
                                    if j["monsterType"] == "DRAGON":
                                        team_2_4min["Dragons"] += 1
                                    elif j["monsterType"] == "RIFTHERALD":
                                        team_2_4min["Heralds"] += 1    
                                    elif j["monsterType"] == "BARON_NASHOR":
                                        team_1_4min["Barons"] += 1

            if match_data["info"]["teams"][0]["win"]:
                team_1_4min["Win"] = 1
                team_2_4min["Win"] = 0
            else:
                team_1_4min["Win"] = 0
                team_2_4min["Win"] = 1

            team_1_4min_data = {
                'Gold': team_1_4min["Gold"],
                'Level': team_1_4min["Level"],
                'Minions': team_1_4min["Minions"],
                'Kills': team_1_4min["Kills"],
                'Assists': team_1_4min["Assists"],
                'Deaths': team_1_4min["Deaths"],
                'Towers': team_1_4min["Towers"],
                'Dragons': team_1_4min["Dragons"],
                'Heralds': team_1_4min["Heralds"],
                'Barons': team_1_4min["Barons"],
                'Gold_diff': team_1_4min["Gold_diff"],
                'Win': team_1_4min["Win"]
            }

            team_2_4min_data = {
                'Gold': team_2_4min["Gold"],
                'Level': team_2_4min["Level"],
                'Minions': team_2_4min["Minions"],
                'Kills': team_2_4min["Kills"],
                'Assists': team_2_4min["Assists"],
                'Deaths': team_2_4min["Deaths"],
                'Towers': team_2_4min["Towers"],
                'Dragons': team_2_4min["Dragons"],
                'Heralds': team_2_4min["Heralds"],
                'Barons': team_2_4min["Barons"],
                'Gold_diff': team_2_4min["Gold_diff"],
                'Win': team_2_4min["Win"]
            }

            combined_data_4min.append(team_1_4min_data)
            combined_data_4min.append(team_2_4min_data)
            
        # if match is longer than 14 minutes, then run the code
        if match_data["info"]["gameMode"] == "CLASSIC" and match_data["info"]["gameDuration"] >= 840 and match_data["info"]["gameDuration"] <=5400:

            team_1_14min = {"Gold": 0, "Level": 0, "Minions": 0, "Kills": 0, "Assists": 0, "Deaths": 0, "Towers": 0, "Dragons": 0, "Heralds": 0, "Barons": 0}
            team_2_14min = {"Gold": 0, "Level": 0, "Minions": 0, "Kills": 0, "Assists": 0, "Deaths": 0, "Towers": 0, "Dragons": 0, "Heralds": 0, "Barons": 0}

            # Determine the minute that we are looking for
            max_frame_index = 14
            # Get the length of the frames in the match timeline
            timeline_frames_length = len(match_timeline["info"]["frames"])
            # Calculate the frame index, ensuring it does not exceed the maximum frame index
            frame_index = min(max_frame_index, timeline_frames_length - 1)


            for j in range(1, 6):
                participant_frame = match_timeline["info"]["frames"][frame_index]["participantFrames"].get(str(j))
                if participant_frame is not None:
                    team_1_14min["Gold"] += participant_frame["totalGold"]
                    team_1_14min["Level"] += participant_frame["level"]
                    team_1_14min["Minions"] += participant_frame["minionsKilled"]
                    team_1_14min["Minions"] += participant_frame["jungleMinionsKilled"]

            for j in range(6, 11):
                participant_frame = match_timeline["info"]["frames"][frame_index]["participantFrames"].get(str(j))
                if participant_frame is not None:
                    team_2_14min["Gold"] += participant_frame["totalGold"]
                    team_2_14min["Level"] += participant_frame["level"]
                    team_2_14min["Minions"] += participant_frame["minionsKilled"]
                    team_2_14min["Minions"] += participant_frame["jungleMinionsKilled"]

            team_1_14min["Level"] /= 5
            team_2_14min["Level"] /= 5

            team_1_14min["Gold_diff"] = team_1_14min["Gold"] - team_2_14min["Gold"]
            team_2_14min["Gold_diff"] = team_2_14min["Gold"] - team_1_14min["Gold"]
            
            #The rest of the info is not available in the minute 14 data, so it has to be scarped minute by minute that why we iterate from 1 to 14
            for i in range(1, 15):

                    #For each minute a list of events its presented, so we can iterate through each event and get necessary info
                            for j in match_timeline["info"]["frames"][i]["events"]:

                                #If the Killer ID is between 1 and 5 is corresponds to team1, if its bigger than 5 is for team2. This pattern is repeated through out the iteration of events
                                if (j["type"] == "CHAMPION_KILL") and (1 <= j["killerId"] <= 5):
                                    team_1_14min["Kills"] += 1
                                    team_2_14min["Deaths"] += 1
                                    try:
                                        team_1_14min["Assists"] += len(j["assistingParticipantIds"])
                                    except:
                                        pass
                                if (j["type"] == "CHAMPION_KILL") and (j["killerId"] > 5):
                                    team_2_14min["Kills"] += 1
                                    team_1_14min["Deaths"] += 1
                                    try:
                                        team_2_14min["Assists"] += len(j["assistingParticipantIds"])
                                    except:
                                        pass
                                    
                                if (j["type"] == "BUILDING_KILL") and (j["teamId"] == 200):
                                    team_1_14min["Towers"] += 1
                                if (j["type"] == "BUILDING_KILL") and (j["teamId"] == 100):
                                    team_2_14min["Towers"] += 1 
                                
                                #Get Dragons and Heralds
                                if (j["type"] == "ELITE_MONSTER_KILL") and (1 <= j["killerId"] <= 5):
                                    if j["monsterType"] == "DRAGON":
                                        team_1_14min["Dragons"] += 1
                                    elif j["monsterType"] == "RIFTHERALD":
                                        team_1_14min["Heralds"] += 1
                                    elif j["monsterType"] == "BARON_NASHOR":
                                        team_1_14min["Barons"] += 1
                                    
                                    
                                if (j["type"] == "ELITE_MONSTER_KILL") and (j["killerId"] > 5):
                                    if j["monsterType"] == "DRAGON":
                                        team_2_14min["Dragons"] += 1
                                    elif j["monsterType"] == "RIFTHERALD":
                                        team_2_14min["Heralds"] += 1    
                                    elif j["monsterType"] == "BARON_NASHOR":
                                        team_1_4min["Barons"] += 1               
                            
            if match_data["info"]["teams"][0]["win"]:
                team_1_14min["Win"] = 1
                team_2_14min["Win"] = 0
            else:
                team_1_14min["Win"] = 0
                team_2_14min["Win"] = 1

            team_1_14min_data = {
                'Gold': team_1_14min["Gold"],
                'Level': team_1_14min["Level"],
                'Minions': team_1_14min["Minions"],
                'Kills': team_1_14min["Kills"],
                'Assists': team_1_14min["Assists"],
                'Deaths': team_1_14min["Deaths"],
                'Towers': team_1_14min["Towers"],
                'Dragons': team_1_14min["Dragons"],
                'Heralds': team_1_14min["Heralds"],
                'Barons': team_1_14min["Barons"],
                'Gold_diff': team_1_14min["Gold_diff"],
                'Win': team_1_14min["Win"]
            }

            team_2_14min_data = {
                'Gold': team_2_14min["Gold"],
                'Level': team_2_14min["Level"],
                'Minions': team_2_14min["Minions"],
                'Kills': team_2_14min["Kills"],
                'Assists': team_2_14min["Assists"],
                'Deaths': team_2_14min["Deaths"],
                'Towers': team_2_14min["Towers"],
                'Dragons': team_2_14min["Dragons"],
                'Heralds': team_2_14min["Heralds"],
                'Barons': team_2_14min["Barons"],
                'Gold_diff': team_2_14min["Gold_diff"],
                'Win': team_2_14min["Win"]
            }

            combined_data_14min.append(team_1_14min_data)
            combined_data_14min.append(team_2_14min_data)
            
        # if match is longer than 28 minutes, then run the code
        if match_data["info"]["gameMode"] == "CLASSIC" and match_data["info"]["gameDuration"] >= 1680 and match_data["info"]["gameDuration"] <=5400:

            team_1_28min = {"Gold": 0, "Level": 0, "Minions": 0, "Kills": 0, "Assists": 0, "Deaths": 0, "Towers": 0, "Dragons": 0, "Heralds": 0, "Barons": 0}
            team_2_28min = {"Gold": 0, "Level": 0, "Minions": 0, "Kills": 0, "Assists": 0, "Deaths": 0, "Towers": 0, "Dragons": 0, "Heralds": 0, "Barons": 0}

            # Determine the minute that we are looking for
            max_frame_index = 28
            # Get the length of the frames in the match timeline
            timeline_frames_length = len(match_timeline["info"]["frames"])
            # Calculate the frame index, ensuring it does not exceed the maximum frame index
            frame_index = min(max_frame_index, timeline_frames_length - 1)


            for j in range(1, 6):
                participant_frame = match_timeline["info"]["frames"][frame_index]["participantFrames"].get(str(j))
                if participant_frame is not None:
                    team_1_28min["Gold"] += participant_frame["totalGold"]
                    team_1_28min["Level"] += participant_frame["level"]
                    team_1_28min["Minions"] += participant_frame["minionsKilled"]
                    team_1_28min["Minions"] += participant_frame["jungleMinionsKilled"]

            for j in range(6, 11):
                participant_frame = match_timeline["info"]["frames"][frame_index]["participantFrames"].get(str(j))
                if participant_frame is not None:
                    team_2_28min["Gold"] += participant_frame["totalGold"]
                    team_2_28min["Level"] += participant_frame["level"]
                    team_2_28min["Minions"] += participant_frame["minionsKilled"]
                    team_2_28min["Minions"] += participant_frame["jungleMinionsKilled"]

            team_1_28min["Level"] /= 5
            team_2_28min["Level"] /= 5

            team_1_28min["Gold_diff"] = team_1_28min["Gold"] - team_2_28min["Gold"]
            team_2_28min["Gold_diff"] = team_2_28min["Gold"] - team_1_28min["Gold"]
            
            #The rest of the info is not available in the minute 14 data, so it has to be scarped minute by minute that why we iterate from 1 to 14
            for i in range(1, 29):

                    #For each minute a list of events its presented, so we can iterate through each event and get necessary info
                            for j in match_timeline["info"]["frames"][i]["events"]:

                                #If the Killer ID is between 1 and 5 is corresponds to team1, if its bigger than 5 is for team2. This pattern is repeated through out the iteration of events
                                if (j["type"] == "CHAMPION_KILL") and (1 <= j["killerId"] <= 5):
                                    team_1_28min["Kills"] += 1
                                    team_2_28min["Deaths"] += 1
                                    try:
                                        team_1_28min["Assists"] += len(j["assistingParticipantIds"])
                                    except:
                                        pass
                                if (j["type"] == "CHAMPION_KILL") and (j["killerId"] > 5):
                                    team_2_28min["Kills"] += 1
                                    team_1_28min["Deaths"] += 1
                                    try:
                                        team_2_28min["Assists"] += len(j["assistingParticipantIds"])
                                    except:
                                        pass

                                if (j["type"] == "BUILDING_KILL") and (j["teamId"] == 200):
                                    team_1_28min["Towers"] += 1
                                if (j["type"] == "BUILDING_KILL") and (j["teamId"] == 100):
                                    team_2_28min["Towers"] += 1 
                                
                                #Get Dragons and Heralds
                                if (j["type"] == "ELITE_MONSTER_KILL") and (1 <= j["killerId"] <= 5):
                                    if j["monsterType"] == "DRAGON":
                                        team_1_28min["Dragons"] += 1
                                    elif j["monsterType"] == "RIFTHERALD":
                                        team_1_28min["Heralds"] += 1
                                    elif j["monsterType"] == "BARON_NASHOR":
                                        team_1_28min["Barons"] += 1
                                    
                                    
                                if (j["type"] == "ELITE_MONSTER_KILL") and (j["killerId"] > 5):
                                    if j["monsterType"] == "DRAGON":
                                        team_2_28min["Dragons"] += 1
                                    elif j["monsterType"] == "RIFTHERALD":
                                        team_2_28min["Heralds"] += 1    
                                    elif j["monsterType"] == "BARON_NASHOR":
                                        team_1_28min["Barons"] += 1               
                                

            if match_data["info"]["teams"][0]["win"]:
                team_1_28min["Win"] = 1
                team_2_28min["Win"] = 0
            else:
                team_1_28min["Win"] = 0
                team_2_28min["Win"] = 1

            team_1_28min_data = {
                'Gold': team_1_28min["Gold"],
                'Level': team_1_28min["Level"],
                'Minions': team_1_28min["Minions"],
                'Kills': team_1_28min["Kills"],
                'Assists': team_1_28min["Assists"],
                'Deaths': team_1_28min["Deaths"],
                'Towers': team_1_28min["Towers"],
                'Dragons': team_1_28min["Dragons"],
                'Heralds': team_1_28min["Heralds"],
                'Barons': team_1_28min["Barons"],
                'Gold_diff': team_1_28min["Gold_diff"],
                'Win': team_1_28min["Win"]
            }

            team_2_28min_data = {
                'Gold': team_2_28min["Gold"],
                'Level': team_2_28min["Level"],
                'Minions': team_2_28min["Minions"],
                'Kills': team_2_28min["Kills"],
                'Assists': team_2_28min["Assists"],
                'Deaths': team_2_28min["Deaths"],
                'Towers': team_2_28min["Towers"],
                'Dragons': team_2_28min["Dragons"],
                'Heralds': team_2_28min["Heralds"],
                'Barons': team_2_28min["Barons"],
                'Gold_diff': team_2_28min["Gold_diff"],
                'Win': team_2_28min["Win"]
            }

            combined_data_28min.append(team_1_28min_data)
            combined_data_28min.append(team_2_28min_data)
            
        # if match is longer than 42 minutes, then run the code
        if match_data["info"]["gameMode"] == "CLASSIC" and match_data["info"]["gameDuration"] >= 2520 and match_data["info"]["gameDuration"] <=5400:

            team_1_42min = {"Gold": 0, "Level": 0, "Minions": 0, "Kills": 0, "Assists": 0, "Deaths": 0, "Towers": 0, "Dragons": 0, "Heralds": 0, "Barons": 0}
            team_2_42min = {"Gold": 0, "Level": 0, "Minions": 0, "Kills": 0, "Assists": 0, "Deaths": 0, "Towers": 0, "Dragons": 0, "Heralds": 0, "Barons": 0}

            # Determine the minute that we are looking for
            max_frame_index = 42
            # Get the length of the frames in the match timeline
            timeline_frames_length = len(match_timeline["info"]["frames"])
            # Calculate the frame index, ensuring it does not exceed the maximum frame index
            frame_index = min(max_frame_index, timeline_frames_length - 1)


            for j in range(1, 6):
                participant_frame = match_timeline["info"]["frames"][frame_index]["participantFrames"].get(str(j))
                if participant_frame is not None:
                    team_1_42min["Gold"] += participant_frame["totalGold"]
                    team_1_42min["Level"] += participant_frame["level"]
                    team_1_42min["Minions"] += participant_frame["minionsKilled"]
                    team_1_42min["Minions"] += participant_frame["jungleMinionsKilled"]

            for j in range(6, 11):
                participant_frame = match_timeline["info"]["frames"][frame_index]["participantFrames"].get(str(j))
                if participant_frame is not None:
                    team_2_42min["Gold"] += participant_frame["totalGold"]
                    team_2_42min["Level"] += participant_frame["level"]
                    team_2_42min["Minions"] += participant_frame["minionsKilled"]
                    team_2_42min["Minions"] += participant_frame["jungleMinionsKilled"]

            team_1_42min["Level"] /= 5
            team_2_42min["Level"] /= 5

            team_1_42min["Gold_diff"] = team_1_42min["Gold"] - team_2_42min["Gold"]
            team_2_42min["Gold_diff"] = team_2_42min["Gold"] - team_1_42min["Gold"]
            
            #The rest of the info is not available in the minute 14 data, so it has to be scarped minute by minute that why we iterate from 1 to 14
            for i in range(1, 43):

                    #For each minute a list of events its presented, so we can iterate through each event and get necessary info
                            for j in match_timeline["info"]["frames"][i]["events"]:

                                #If the Killer ID is between 1 and 5 is corresponds to team1, if its bigger than 5 is for team2. This pattern is repeated through out the iteration of events
                                if (j["type"] == "CHAMPION_KILL") and (1 <= j["killerId"] <= 5):
                                    team_1_42min["Kills"] += 1
                                    team_2_42min["Deaths"] += 1
                                    try:
                                        team_1_42min["Assists"] += len(j["assistingParticipantIds"])
                                    except:
                                        pass
                                if (j["type"] == "CHAMPION_KILL") and (j["killerId"] > 5):
                                    team_2_42min["Kills"] += 1
                                    team_1_42min["Deaths"] += 1
                                    try:
                                        team_2_42min["Assists"] += len(j["assistingParticipantIds"])
                                    except:
                                        pass
                                    
                                if (j["type"] == "BUILDING_KILL") and (j["teamId"] == 200):
                                    team_1_42min["Towers"] += 1
                                if (j["type"] == "BUILDING_KILL") and (j["teamId"] == 100):
                                    team_2_42min["Towers"] += 1 
                                
                                #Get Dragons and Heralds
                                if (j["type"] == "ELITE_MONSTER_KILL") and (1 <= j["killerId"] <= 5):
                                    if j["monsterType"] == "DRAGON":
                                        team_1_42min["Dragons"] += 1
                                    elif j["monsterType"] == "RIFTHERALD":
                                        team_1_42min["Heralds"] += 1
                                    elif j["monsterType"] == "BARON_NASHOR":
                                        team_1_42min["Barons"] += 1
                                    
                                if (j["type"] == "ELITE_MONSTER_KILL") and (j["killerId"] > 5):
                                    if j["monsterType"] == "DRAGON":
                                        team_2_42min["Dragons"] += 1
                                    elif j["monsterType"] == "RIFTHERALD":
                                        team_2_42min["Heralds"] += 1
                                    elif j["monsterType"] == "BARON_NASHOR":
                                        team_1_42min["Barons"] += 1

            if match_data["info"]["teams"][0]["win"]:
                team_1_42min["Win"] = 1
                team_2_42min["Win"] = 0
            else:
                team_1_42min["Win"] = 0
                team_2_42min["Win"] = 1

            team_1_42min_data = {
                'Gold': team_1_42min["Gold"],
                'Level': team_1_42min["Level"],
                'Minions': team_1_42min["Minions"],
                'Kills': team_1_42min["Kills"],
                'Assists': team_1_42min["Assists"],
                'Deaths': team_1_42min["Deaths"],
                'Towers': team_1_42min["Towers"],
                'Dragons': team_1_42min["Dragons"],
                'Heralds': team_1_42min["Heralds"],
                'Barons': team_1_42min["Barons"],
                'Gold_diff': team_1_42min["Gold_diff"],
                'Win': team_1_42min["Win"]
            }

            team_2_42min_data = {
                'Gold': team_2_42min["Gold"],
                'Level': team_2_42min["Level"],
                'Minions': team_2_42min["Minions"],
                'Kills': team_2_42min["Kills"],
                'Assists': team_2_42min["Assists"],
                'Deaths': team_2_42min["Deaths"],
                'Towers': team_2_42min["Towers"],
                'Dragons': team_2_42min["Dragons"],
                'Heralds': team_2_42min["Heralds"],
                'Barons': team_2_42min["Barons"],
                'Gold_diff': team_2_42min["Gold_diff"],
                'Win': team_2_42min["Win"]
            }

            combined_data_42min.append(team_1_42min_data)
            combined_data_42min.append(team_2_42min_data)


    # Update StartNumber and EndNumber for the next iteration
    StartNumber += 50
    n=n+1
    print("Loop", n)
    print()

    # Save the combined data to a CSV file
    combined_df_4min = pd.DataFrame(combined_data_4min)
    combined_df_4min.to_csv(file_path_4min, index=False, mode='a', header=not os.path.exists(file_path_4min))
    
    combined_df_14min = pd.DataFrame(combined_data_14min)
    combined_df_14min.to_csv(file_path_14min, index=False, mode='a', header=not os.path.exists(file_path_14min))
    
    combined_df_28min = pd.DataFrame(combined_data_28min)
    combined_df_28min.to_csv(file_path_28min, index=False, mode='a', header=not os.path.exists(file_path_28min))
    
    combined_df_42min = pd.DataFrame(combined_data_42min)
    combined_df_42min.to_csv(file_path_42min, index=False, mode='a', header=not os.path.exists(file_path_42min))
    
    
time.sleep(600)