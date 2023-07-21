def get_minute_stats(min, match_timeline):
  team_1_stats = {"Gold": 0, "Level": 0, "Minions": 0, "Kills": 0, "Assists": 0, "Deaths": 0, "Towers": 0, "Dragons": 0, "Heralds": 0, "Barons": 0}
  team_2_stats = {"Gold": 0, "Level": 0, "Minions": 0, "Kills": 0, "Assists": 0, "Deaths": 0, "Towers": 0, "Dragons": 0, "Heralds": 0, "Barons": 0}
  max_frame_index = min
  # Get the length of the frames in the match timeline
  timeline_frames_length = len(match_timeline["info"]["frames"])
  # Calculate the frame index, ensuring it does not exceed the maximum frame index
  frame_index = min(max_frame_index, timeline_frames_length - 1)

  


  return team_1_stats, team_2_stats