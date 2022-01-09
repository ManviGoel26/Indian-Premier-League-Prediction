from os import listdir
from json import load

import pandas as pd

FOLDER_PATH = './ipl_json/'

# get file names
file_names = listdir(FOLDER_PATH)
file_names.remove('README.txt')

# num of matches from year 2008 to 2021
# MATCH_NUM = len(file_names)

MATCHES = []
BALL_BY_BALL = []

for file_ in file_names:
    file_name = FOLDER_PATH + file_
    match_file = open(file_name)
    match_file_data = load(match_file)

    match_data = {}
    ball_by_ball_data = {}

    match_data['id'] = file_.split('.')[0]
    match_data['date'] = match_file_data['info']['dates'][0]
    if 'match_number' in match_file_data['info']['event'].keys():
        match_data['match_number'] = match_file_data['info']['event']['match_number']
        match_data['match_stage'] = 'NA'
    else:
        # stage
        match_data['match_number'] = 'NA'
        match_data['match_stage'] = match_file_data['info']['event']['stage']
    if 'city' in match_file_data['info'].keys():
        match_data['city'] = match_file_data['info']['city']
    else:
        # city is out of India
        CITY_FROM_VENUE = {
            "Dubai International Cricket Stadium": "Dubai (UAE)", 
            "Sharjah Cricket Stadium": "Sharjah (UAE)"
        }
        if match_file_data['info']['venue'] in CITY_FROM_VENUE.keys():
            match_data['city'] = CITY_FROM_VENUE[match_file_data['info']['venue']]
        else:
            print(file_name)
    match_data['venue'] = match_file_data['info']['venue']
    match_data['team1'] = match_file_data['info']['teams'][0]
    match_data['team2'] = match_file_data['info']['teams'][1]
    match_data['toss_winner'] = match_file_data['info']['toss']['winner']
    match_data['toss_decision'] = match_file_data['info']['toss']['decision']
    match_data['winner'] = match_file_data['info']['toss']['winner']
    if 'by' in match_file_data['info']['outcome'].keys():
        match_data['result'] = list(match_file_data['info']['outcome']['by'].keys())[0]
        match_data['result_margin'] = match_file_data['info']['outcome']['by'][match_data['result']]
    else:
        # match is tie
        match_data['result'] = match_file_data['info']['outcome']['result']
        match_data['result_margin'] = 'NA'
    MATCH_ID = file_.split('.')[0]
    MATCH_INNING = 1
    for inning in match_file_data['innings']:
        BOWLING_TEAM = inning['team']
        BATTING_TEAM =  match_data['team1'] if BOWLING_TEAM != match_data['team1'] else match_data['team2']
        for over in inning['overs']:
            OVER_NUM = over['over']
            for delivery in over['deliveries']:
                # print(delivery)
                ball_by_ball_data['id'] = MATCH_ID
                ball_by_ball_data['inning'] = MATCH_INNING
                ball_by_ball_data['over'] = OVER_NUM
                ball_by_ball_data['batsman'] = delivery['batter']
                ball_by_ball_data['non_striker'] = delivery['non_striker']
                ball_by_ball_data['bowler'] = delivery['bowler']
                ball_by_ball_data['batsman_runs'] = delivery['runs']['batter']
                ball_by_ball_data['extra_runs'] = delivery['runs']['extras']
                ball_by_ball_data['total_runs'] = delivery['runs']['total']
                ball_by_ball_data['bowling_team'] = BOWLING_TEAM
                ball_by_ball_data['batting_team'] = BATTING_TEAM
                if 'wickets' in delivery.keys():
                    ball_by_ball_data['is_wicket'] = 1
                    ball_by_ball_data['dismissal_kind'] = delivery['wickets'][0]['kind']
                    ball_by_ball_data['player_dismissed'] = delivery['wickets'][0]['player_out']
                    if 'fielders' in delivery['wickets'][0].keys():
                        ball_by_ball_data['fielder'] = delivery['wickets'][0]['fielders'][0]['name']
                    else:
                        ball_by_ball_data['fielder'] = 'NA'
                else:
                    ball_by_ball_data['is_wicket'] = 'NA'
                    ball_by_ball_data['dismissal_kind'] = 'NA'
                    ball_by_ball_data['player_dismissed'] = 'NA'
                    ball_by_ball_data['fielder'] = 'NA'
                BALL_BY_BALL.append(ball_by_ball_data)
            MATCH_INNING += 1

    MATCHES.append(match_data)

    match_file.close()

matches_df = pd.DataFrame(MATCHES)
ball_by_ball_df = pd.DataFrame(BALL_BY_BALL)

matches_df.to_csv('my_matches_data.csv')
ball_by_ball_df.to_csv('my_ball_by_ball_data.csv')
