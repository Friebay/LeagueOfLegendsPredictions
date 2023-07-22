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