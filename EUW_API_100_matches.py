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

            team_1_1min = {"Gold": 0, "Level": 0, "Minions": 0, "Kills": 0, "Assists": 0, "Deaths": 0, "Towers": 0, "Dragons": 0, "Heralds": 0, "Barons": 0}
            team_2_1min = {"Gold": 0, "Level": 0, "Minions": 0, "Kills": 0, "Assists": 0, "Deaths": 0, "Towers": 0, "Dragons": 0, "Heralds": 0, "Barons": 0}

            # Determine the minute that we are looking for
            max_frame_index = 1
            # Get the length of the frames in the match timeline
            timeline_frames_length = len(match_timeline["info"]["frames"])
            # Calculate the frame index, ensuring it does not exceed the maximum frame index
            frame_index = min(max_frame_index, timeline_frames_length - 1)

            for j in range(1, 6):
                participant_frame = match_timeline["info"]["frames"][frame_index]["participantFrames"].get(str(j))
                if participant_frame is not None:
                    team_1_1min["Gold"] += participant_frame["totalGold"]
                    team_1_1min["Level"] += participant_frame["level"]
                    team_1_1min["Minions"] += participant_frame["minionsKilled"]
                    team_1_1min["Minions"] += participant_frame["jungleMinionsKilled"]

            for j in range(6, 11):
                participant_frame = match_timeline["info"]["frames"][frame_index]["participantFrames"].get(str(j))
                if participant_frame is not None:
                    team_2_1min["Gold"] += participant_frame["totalGold"]
                    team_2_1min["Level"] += participant_frame["level"]
                    team_2_1min["Minions"] += participant_frame["minionsKilled"]
                    team_2_1min["Minions"] += participant_frame["jungleMinionsKilled"]

            team_1_1min["Level"] /= 5
            team_2_1min["Level"] /= 5

            team_1_1min["Gold_diff"] = team_1_1min["Gold"] - team_2_1min["Gold"]
            team_2_1min["Gold_diff"] = team_2_1min["Gold"] - team_1_1min["Gold"]
            
            #The rest of the info is not available in the minute 1 data, so it has to be scarped minute by minute that why we iterate from 1 to 15 (15 minute is not taken into account, 15 is because how Python works)
            for i in range(1, max_frame_index+1):

                    #For each minute a list of events its presented, so we can iterate through each event and get necessary info
                            for j in match_timeline["info"]["frames"][i]["events"]:

                                #If the Killer ID is between 1 and 5 is corresponds to team1, if its bigger than 5 is for team2. This pattern is repeated through out the iteration of events
                                if (j["type"] == "CHAMPION_KILL") and (1 <= j["killerId"] <= 5):
                                    team_1_1min["Kills"] += 1
                                    team_2_1min["Deaths"] += 1
                                    try:
                                        team_1_1min["Assists"] += len(j["assistingParticipantIds"])
                                    except:
                                        pass
                                if (j["type"] == "CHAMPION_KILL") and (j["killerId"] > 5):
                                    team_2_1min["Kills"] += 1
                                    team_1_1min["Deaths"] += 1
                                    try:
                                        team_2_1min["Assists"] += len(j["assistingParticipantIds"])
                                    except:
                                        pass
                                    
                                if (j["type"] == "BUILDING_KILL") and (j["teamId"] == 200):
                                    team_1_1min["Towers"] += 1
                                if (j["type"] == "BUILDING_KILL") and (j["teamId"] == 100):
                                    team_2_1min["Towers"] += 1 
                                
                                #Get Dragons and Heralds
                                if (j["type"] == "ELITE_MONSTER_KILL") and (1 <= j["killerId"] <= 5):
                                    if j["monsterType"] == "DRAGON":
                                        team_1_1min["Dragons"] += 1
                                    elif j["monsterType"] == "RIFTHERALD":
                                        team_1_1min["Heralds"] += 1
                                    elif j["monsterType"] == "BARON_NASHOR":
                                        team_1_1min["Barons"] += 1
                                    
                                if (j["type"] == "ELITE_MONSTER_KILL") and (j["killerId"] > 5):
                                    if j["monsterType"] == "DRAGON":
                                        team_2_1min["Dragons"] += 1
                                    elif j["monsterType"] == "RIFTHERALD":
                                        team_2_1min["Heralds"] += 1    
                                    elif j["monsterType"] == "BARON_NASHOR":
                                        team_1_1min["Barons"] += 1

            if match_data["info"]["teams"][0]["win"]:
                team_1_1min["Win"] = 1
                team_2_1min["Win"] = 0
            else:
                team_1_1min["Win"] = 0
                team_2_1min["Win"] = 1

            team_1_1min_data = team_1_1min.copy()
            team_2_1min_data = team_2_1min.copy()

            combined_data[max_frame_index-1].append(team_1_1min_data)
            combined_data[max_frame_index-1].append(team_2_1min_data)
        
        # if match is longer than 2 minutes, then run the code
        if match_data["info"]["gameMode"] == "CLASSIC" and match_data["info"]["gameDuration"] >= 120 and match_data["info"]["gameDuration"] <=5400:

            team_1_2min = {"Gold": 0, "Level": 0, "Minions": 0, "Kills": 0, "Assists": 0, "Deaths": 0, "Towers": 0, "Dragons": 0, "Heralds": 0, "Barons": 0}
            team_2_2min = {"Gold": 0, "Level": 0, "Minions": 0, "Kills": 0, "Assists": 0, "Deaths": 0, "Towers": 0, "Dragons": 0, "Heralds": 0, "Barons": 0}

            # Determine the minute that we are looking for
            max_frame_index = 2
            # Get the length of the frames in the match timeline
            timeline_frames_length = len(match_timeline["info"]["frames"])
            # Calculate the frame index, ensuring it does not exceed the maximum frame index
            frame_index = min(max_frame_index, timeline_frames_length - 1)

            for j in range(1, 6):
                participant_frame = match_timeline["info"]["frames"][frame_index]["participantFrames"].get(str(j))
                if participant_frame is not None:
                    team_1_2min["Gold"] += participant_frame["totalGold"]
                    team_1_2min["Level"] += participant_frame["level"]
                    team_1_2min["Minions"] += participant_frame["minionsKilled"]
                    team_1_2min["Minions"] += participant_frame["jungleMinionsKilled"]

            for j in range(6, 11):
                participant_frame = match_timeline["info"]["frames"][frame_index]["participantFrames"].get(str(j))
                if participant_frame is not None:
                    team_2_2min["Gold"] += participant_frame["totalGold"]
                    team_2_2min["Level"] += participant_frame["level"]
                    team_2_2min["Minions"] += participant_frame["minionsKilled"]
                    team_2_2min["Minions"] += participant_frame["jungleMinionsKilled"]

            team_1_2min["Level"] /= 5
            team_2_2min["Level"] /= 5

            team_1_2min["Gold_diff"] = team_1_2min["Gold"] - team_2_2min["Gold"]
            team_2_2min["Gold_diff"] = team_2_2min["Gold"] - team_1_2min["Gold"]
            
            #The rest of the info is not available in the minute 1 data, so it has to be scarped minute by minute that why we iterate from 1 to 15 (15 minute is not taken into account, 15 is because how Python works)
            for i in range(1, max_frame_index+1):

                    #For each minute a list of events its presented, so we can iterate through each event and get necessary info
                            for j in match_timeline["info"]["frames"][i]["events"]:

                                #If the Killer ID is between 1 and 5 is corresponds to team1, if its bigger than 5 is for team2. This pattern is repeated through out the iteration of events
                                if (j["type"] == "CHAMPION_KILL") and (1 <= j["killerId"] <= 5):
                                    team_1_2min["Kills"] += 1
                                    team_2_2min["Deaths"] += 1
                                    try:
                                        team_1_2min["Assists"] += len(j["assistingParticipantIds"])
                                    except:
                                        pass
                                if (j["type"] == "CHAMPION_KILL") and (j["killerId"] > 5):
                                    team_2_2min["Kills"] += 1
                                    team_1_2min["Deaths"] += 1
                                    try:
                                        team_2_2min["Assists"] += len(j["assistingParticipantIds"])
                                    except:
                                        pass
                                    
                                if (j["type"] == "BUILDING_KILL") and (j["teamId"] == 200):
                                    team_1_2min["Towers"] += 1
                                if (j["type"] == "BUILDING_KILL") and (j["teamId"] == 100):
                                    team_2_2min["Towers"] += 1 
                                
                                #Get Dragons and Heralds
                                if (j["type"] == "ELITE_MONSTER_KILL") and (1 <= j["killerId"] <= 5):
                                    if j["monsterType"] == "DRAGON":
                                        team_1_2min["Dragons"] += 1
                                    elif j["monsterType"] == "RIFTHERALD":
                                        team_1_2min["Heralds"] += 1
                                    elif j["monsterType"] == "BARON_NASHOR":
                                        team_1_2min["Barons"] += 1
                                    
                                    
                                if (j["type"] == "ELITE_MONSTER_KILL") and (j["killerId"] > 5):
                                    if j["monsterType"] == "DRAGON":
                                        team_2_2min["Dragons"] += 1
                                    elif j["monsterType"] == "RIFTHERALD":
                                        team_2_2min["Heralds"] += 1    
                                    elif j["monsterType"] == "BARON_NASHOR":
                                        team_1_2min["Barons"] += 1

            if match_data["info"]["teams"][0]["win"]:
                team_1_2min["Win"] = 1
                team_2_2min["Win"] = 0
            else:
                team_1_2min["Win"] = 0
                team_2_2min["Win"] = 1

            team_1_2min_data = team_1_2min.copy()
            team_2_2min_data = team_2_2min.copy()

            combined_data[max_frame_index-1].append(team_1_2min_data)
            combined_data[max_frame_index-1].append(team_2_2min_data)
        
        # if match is longer than 3 minutes, then run the code
        if match_data["info"]["gameMode"] == "CLASSIC" and match_data["info"]["gameDuration"] >= 180 and match_data["info"]["gameDuration"] <=5400:

            team_1_3min = {"Gold": 0, "Level": 0, "Minions": 0, "Kills": 0, "Assists": 0, "Deaths": 0, "Towers": 0, "Dragons": 0, "Heralds": 0, "Barons": 0}
            team_2_3min = {"Gold": 0, "Level": 0, "Minions": 0, "Kills": 0, "Assists": 0, "Deaths": 0, "Towers": 0, "Dragons": 0, "Heralds": 0, "Barons": 0}

            # Determine the minute that we are looking for
            max_frame_index = 3
            # Get the length of the frames in the match timeline
            timeline_frames_length = len(match_timeline["info"]["frames"])
            # Calculate the frame index, ensuring it does not exceed the maximum frame index
            frame_index = min(max_frame_index, timeline_frames_length - 1)

            for j in range(1, 6):
                participant_frame = match_timeline["info"]["frames"][frame_index]["participantFrames"].get(str(j))
                if participant_frame is not None:
                    team_1_3min["Gold"] += participant_frame["totalGold"]
                    team_1_3min["Level"] += participant_frame["level"]
                    team_1_3min["Minions"] += participant_frame["minionsKilled"]
                    team_1_3min["Minions"] += participant_frame["jungleMinionsKilled"]

            for j in range(6, 11):
                participant_frame = match_timeline["info"]["frames"][frame_index]["participantFrames"].get(str(j))
                if participant_frame is not None:
                    team_2_3min["Gold"] += participant_frame["totalGold"]
                    team_2_3min["Level"] += participant_frame["level"]
                    team_2_3min["Minions"] += participant_frame["minionsKilled"]
                    team_2_3min["Minions"] += participant_frame["jungleMinionsKilled"]

            team_1_3min["Level"] /= 5
            team_2_3min["Level"] /= 5

            team_1_3min["Gold_diff"] = team_1_3min["Gold"] - team_2_3min["Gold"]
            team_2_3min["Gold_diff"] = team_2_3min["Gold"] - team_1_3min["Gold"]
            
            #The rest of the info is not available in the minute 1 data, so it has to be scarped minute by minute that why we iterate from 1 to 15 (15 minute is not taken into account, 15 is because how Python works)
            for i in range(1, max_frame_index+1):

                    #For each minute a list of events its presented, so we can iterate through each event and get necessary info
                            for j in match_timeline["info"]["frames"][i]["events"]:

                                #If the Killer ID is between 1 and 5 is corresponds to team1, if its bigger than 5 is for team2. This pattern is repeated through out the iteration of events
                                if (j["type"] == "CHAMPION_KILL") and (1 <= j["killerId"] <= 5):
                                    team_1_3min["Kills"] += 1
                                    team_2_3min["Deaths"] += 1
                                    try:
                                        team_1_3min["Assists"] += len(j["assistingParticipantIds"])
                                    except:
                                        pass
                                if (j["type"] == "CHAMPION_KILL") and (j["killerId"] > 5):
                                    team_2_3min["Kills"] += 1
                                    team_1_3min["Deaths"] += 1
                                    try:
                                        team_2_3min["Assists"] += len(j["assistingParticipantIds"])
                                    except:
                                        pass
                                    
                                if (j["type"] == "BUILDING_KILL") and (j["teamId"] == 200):
                                    team_1_3min["Towers"] += 1
                                if (j["type"] == "BUILDING_KILL") and (j["teamId"] == 100):
                                    team_2_3min["Towers"] += 1 
                                
                                #Get Dragons and Heralds
                                if (j["type"] == "ELITE_MONSTER_KILL") and (1 <= j["killerId"] <= 5):
                                    if j["monsterType"] == "DRAGON":
                                        team_1_3min["Dragons"] += 1
                                    elif j["monsterType"] == "RIFTHERALD":
                                        team_1_3min["Heralds"] += 1
                                    elif j["monsterType"] == "BARON_NASHOR":
                                        team_1_3min["Barons"] += 1
                                    
                                    
                                if (j["type"] == "ELITE_MONSTER_KILL") and (j["killerId"] > 5):
                                    if j["monsterType"] == "DRAGON":
                                        team_2_3min["Dragons"] += 1
                                    elif j["monsterType"] == "RIFTHERALD":
                                        team_2_3min["Heralds"] += 1    
                                    elif j["monsterType"] == "BARON_NASHOR":
                                        team_1_3min["Barons"] += 1

            if match_data["info"]["teams"][0]["win"]:
                team_1_3min["Win"] = 1
                team_2_3min["Win"] = 0
            else:
                team_1_3min["Win"] = 0
                team_2_3min["Win"] = 1

            team_1_3min_data = team_1_3min.copy()
            team_2_3min_data = team_2_3min.copy()

            combined_data[max_frame_index-1].append(team_1_3min_data)
            combined_data[max_frame_index-1].append(team_2_3min_data)
        
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
            for i in range(1, max_frame_index+1):

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

            team_1_4min_data = team_1_4min.copy()
            team_2_4min_data = team_2_4min.copy()

            combined_data[max_frame_index-1].append(team_1_4min_data)
            combined_data[max_frame_index-1].append(team_2_4min_data)
            
        # if match is longer than 5 minutes, then run the code
        if match_data["info"]["gameMode"] == "CLASSIC" and match_data["info"]["gameDuration"] >= 300 and match_data["info"]["gameDuration"] <=5400:

            team_1_5min = {"Gold": 0, "Level": 0, "Minions": 0, "Kills": 0, "Assists": 0, "Deaths": 0, "Towers": 0, "Dragons": 0, "Heralds": 0, "Barons": 0}
            team_2_5min = {"Gold": 0, "Level": 0, "Minions": 0, "Kills": 0, "Assists": 0, "Deaths": 0, "Towers": 0, "Dragons": 0, "Heralds": 0, "Barons": 0}

            max_frame_index = 5
            timeline_frames_length = len(match_timeline["info"]["frames"])
            frame_index = min(max_frame_index, timeline_frames_length - 1)


            for j in range(1, 6):
                participant_frame = match_timeline["info"]["frames"][frame_index]["participantFrames"].get(str(j))
                if participant_frame is not None:
                    team_1_5min["Gold"] += participant_frame["totalGold"]
                    team_1_5min["Level"] += participant_frame["level"]
                    team_1_5min["Minions"] += participant_frame["minionsKilled"]
                    team_1_5min["Minions"] += participant_frame["jungleMinionsKilled"]

            for j in range(6, 11):
                participant_frame = match_timeline["info"]["frames"][frame_index]["participantFrames"].get(str(j))
                if participant_frame is not None:
                    team_2_5min["Gold"] += participant_frame["totalGold"]
                    team_2_5min["Level"] += participant_frame["level"]
                    team_2_5min["Minions"] += participant_frame["minionsKilled"]
                    team_2_5min["Minions"] += participant_frame["jungleMinionsKilled"]

            team_1_5min["Level"] /= 5
            team_2_5min["Level"] /= 5

            team_1_5min["Gold_diff"] = team_1_5min["Gold"] - team_2_5min["Gold"]
            team_2_5min["Gold_diff"] = team_2_5min["Gold"] - team_1_5min["Gold"]
            
            for i in range(1, max_frame_index+1):

                    for j in match_timeline["info"]["frames"][i]["events"]:

                                if (j["type"] == "CHAMPION_KILL") and (1 <= j["killerId"] <= 5):
                                    team_1_5min["Kills"] += 1
                                    team_2_5min["Deaths"] += 1
                                    try:
                                        team_1_5min["Assists"] += len(j["assistingParticipantIds"])
                                    except:
                                        pass
                                if (j["type"] == "CHAMPION_KILL") and (j["killerId"] > 5):
                                    team_2_5min["Kills"] += 1
                                    team_1_5min["Deaths"] += 1
                                    try:
                                        team_2_5min["Assists"] += len(j["assistingParticipantIds"])
                                    except:
                                        pass
                                    
                                if (j["type"] == "BUILDING_KILL") and (j["teamId"] == 200):
                                    team_1_5min["Towers"] += 1
                                if (j["type"] == "BUILDING_KILL") and (j["teamId"] == 100):
                                    team_2_5min["Towers"] += 1 
                                
                                if (j["type"] == "ELITE_MONSTER_KILL") and (1 <= j["killerId"] <= 5):
                                    if j["monsterType"] == "DRAGON":
                                        team_1_5min["Dragons"] += 1
                                    elif j["monsterType"] == "RIFTHERALD":
                                        team_1_5min["Heralds"] += 1
                                    elif j["monsterType"] == "BARON_NASHOR":
                                        team_1_5min["Barons"] += 1
                                    
                                    
                                if (j["type"] == "ELITE_MONSTER_KILL") and (j["killerId"] > 5):
                                    if j["monsterType"] == "DRAGON":
                                        team_2_5min["Dragons"] += 1
                                    elif j["monsterType"] == "RIFTHERALD":
                                        team_2_5min["Heralds"] += 1    
                                    elif j["monsterType"] == "BARON_NASHOR":
                                        team_1_5min["Barons"] += 1

            if match_data["info"]["teams"][0]["win"]:
                team_1_5min["Win"] = 1
                team_2_5min["Win"] = 0
            else:
                team_1_5min["Win"] = 0
                team_2_5min["Win"] = 1

            team_1_5min_data = team_1_5min.copy()
            team_2_5min_data = team_2_5min.copy()

            combined_data[max_frame_index-1].append(team_1_5min_data)
            combined_data[max_frame_index-1].append(team_2_5min_data)
            
        # if match is longer than 6 minutes, then run the code
        if match_data["info"]["gameMode"] == "CLASSIC" and match_data["info"]["gameDuration"] >= 360 and match_data["info"]["gameDuration"] <=5400:

            team_1_6min = {"Gold": 0, "Level": 0, "Minions": 0, "Kills": 0, "Assists": 0, "Deaths": 0, "Towers": 0, "Dragons": 0, "Heralds": 0, "Barons": 0}
            team_2_6min = {"Gold": 0, "Level": 0, "Minions": 0, "Kills": 0, "Assists": 0, "Deaths": 0, "Towers": 0, "Dragons": 0, "Heralds": 0, "Barons": 0}

            max_frame_index = 6
            timeline_frames_length = len(match_timeline["info"]["frames"])
            frame_index = min(max_frame_index, timeline_frames_length - 1)


            for j in range(1, 6):
                participant_frame = match_timeline["info"]["frames"][frame_index]["participantFrames"].get(str(j))
                if participant_frame is not None:
                    team_1_6min["Gold"] += participant_frame["totalGold"]
                    team_1_6min["Level"] += participant_frame["level"]
                    team_1_6min["Minions"] += participant_frame["minionsKilled"]
                    team_1_6min["Minions"] += participant_frame["jungleMinionsKilled"]

            for j in range(6, 11):
                participant_frame = match_timeline["info"]["frames"][frame_index]["participantFrames"].get(str(j))
                if participant_frame is not None:
                    team_2_6min["Gold"] += participant_frame["totalGold"]
                    team_2_6min["Level"] += participant_frame["level"]
                    team_2_6min["Minions"] += participant_frame["minionsKilled"]
                    team_2_6min["Minions"] += participant_frame["jungleMinionsKilled"]

            team_1_6min["Level"] /= 5
            team_2_6min["Level"] /= 5

            team_1_6min["Gold_diff"] = team_1_6min["Gold"] - team_2_6min["Gold"]
            team_2_6min["Gold_diff"] = team_2_6min["Gold"] - team_1_6min["Gold"]
            
            for i in range(1, max_frame_index+1):

                    for j in match_timeline["info"]["frames"][i]["events"]:

                                if (j["type"] == "CHAMPION_KILL") and (1 <= j["killerId"] <= 5):
                                    team_1_6min["Kills"] += 1
                                    team_2_6min["Deaths"] += 1
                                    try:
                                        team_1_6min["Assists"] += len(j["assistingParticipantIds"])
                                    except:
                                        pass
                                if (j["type"] == "CHAMPION_KILL") and (j["killerId"] > 5):
                                    team_2_6min["Kills"] += 1
                                    team_1_6min["Deaths"] += 1
                                    try:
                                        team_2_6min["Assists"] += len(j["assistingParticipantIds"])
                                    except:
                                        pass
                                    
                                if (j["type"] == "BUILDING_KILL") and (j["teamId"] == 200):
                                    team_1_6min["Towers"] += 1
                                if (j["type"] == "BUILDING_KILL") and (j["teamId"] == 100):
                                    team_2_6min["Towers"] += 1 
                                
                                if (j["type"] == "ELITE_MONSTER_KILL") and (1 <= j["killerId"] <= 5):
                                    if j["monsterType"] == "DRAGON":
                                        team_1_6min["Dragons"] += 1
                                    elif j["monsterType"] == "RIFTHERALD":
                                        team_1_6min["Heralds"] += 1
                                    elif j["monsterType"] == "BARON_NASHOR":
                                        team_1_6min["Barons"] += 1
                                    
                                    
                                if (j["type"] == "ELITE_MONSTER_KILL") and (j["killerId"] > 5):
                                    if j["monsterType"] == "DRAGON":
                                        team_2_6min["Dragons"] += 1
                                    elif j["monsterType"] == "RIFTHERALD":
                                        team_2_6min["Heralds"] += 1    
                                    elif j["monsterType"] == "BARON_NASHOR":
                                        team_1_6min["Barons"] += 1

            if match_data["info"]["teams"][0]["win"]:
                team_1_6min["Win"] = 1
                team_2_6min["Win"] = 0
            else:
                team_1_6min["Win"] = 0
                team_2_6min["Win"] = 1

            team_1_6min_data = team_1_6min.copy()
            team_2_6min_data = team_2_6min.copy()

            combined_data[max_frame_index-1].append(team_1_6min_data)
            combined_data[max_frame_index-1].append(team_2_6min_data)
            
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
            for i in range(1, max_frame_index+1):

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

            team_1_14min_data = team_1_14min.copy()
            team_2_14min_data = team_2_14min.copy()

            combined_data[max_frame_index-1].append(team_1_14min_data)
            combined_data[max_frame_index-1].append(team_2_14min_data)
            
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
            for i in range(1, max_frame_index+1):

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

            team_1_28min_data = team_1_28min.copy()
            team_2_28min_data = team_2_28min.copy()

            combined_data[max_frame_index-1].append(team_1_28min_data)
            combined_data[max_frame_index-1].append(team_2_28min_data)
            
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
            for i in range(1, max_frame_index+1):

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

            team_1_42min_data = team_1_42min.copy()
            team_2_42min_data = team_2_42min.copy()

            combined_data[max_frame_index-1].append(team_1_42min_data)
            combined_data[max_frame_index-1].append(team_2_42min_data)


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