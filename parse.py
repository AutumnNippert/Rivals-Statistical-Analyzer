# load all json files with wildcard matching stats_*.json

import json
import glob
import pprint
from api import *

import numpy as np
import pandas as pd
import scipy
import random
from deap import base, creator, tools, algorithms

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression, LinearRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.neighbors import KNeighborsClassifier as KNear
from sklearn.svm import SVC
from sklearn.naive_bayes import GaussianNB, BernoulliNB
from xgboost import XGBClassifier
from sklearn.metrics import accuracy_score

def getPlayers():
    pattern = 'stats_*.json'
    files = glob.glob(pattern)

    allPlayers = [] # list of json dicts from the files
    for file in files:
        with open(file) as f:
            allPlayers.append(json.load(f))

    # pprint.pprint(allPlayers)


    # sort by level (player['player]['level]) and print player name (player['player']['name']) next to level
    # sort by level
    allPlayers.sort(key=lambda x: x['player']['level'], reverse=True)


    # print name, level as a table
    print(f'{"Name":<20} {"Level":<5}')
    for player in allPlayers:
        print(f'{player["player"]["name"]:<20} {player["player"]["level"]:<5}')

def getComp(match_json):
    """
    "match_details": {
       "match_players": [
           {
                "player_heroes": [
                    {
                        "hero_id": 1029,
                        "play_time": 535.6576271597296,
                        "kills": 15,
                        "deaths": 6,
                        "assists": 0,
                        "session_hit_rate": 0.53125,
                        "hero_icon": "/heroes/transformations/magik-headbig-0.webp"
                    }
                ]
"""
    players = []
    for player in match_json['match_details']['match_players']:
        player_heroes = player['player_heroes']
        # get hero with highest playtime
        player_heroes.sort(key=lambda x: x['play_time'], reverse=True)
        if len(player_heroes) == 0:
            continue
        hero = player_heroes[0]
        players.append({'player_uid': player['player_uid'], 'nick_name': player['nick_name'], 'hero_id': hero['hero_id']})
    
    # get if team 1 won; (get first player, then get "is_win = 1")
    is_win = match_json['match_details']['match_players'][0]['is_win']
    return players, is_win

# read match_data_6714268_1741148338_454_11001_10.json
# get the heroes for each player
# print the player name and hero name

def pprint_match(players, team1_win):
    # print first 6 on the left and last 6 on the right
    print(f'{"Team 1":<20} {"Heroes":<5} {"Team 2":<20} {"Heroes":<5}')
    for i in range(6):
        print(f'{players[i]["nick_name"]:<20} {players[i]["hero_id"]:<5} {players[i+6]["nick_name"]:<20} {players[i+6]["hero_id"]:<5}')

    print(f'Team 1 {"won" if team1_win else "lost"}')

def comp_to_vector(characters):
    ids = get_hero_id_to_name()
    unique_heroes = list(ids.keys())

    vec = [0] * len(unique_heroes*2)

    for player in characters:
        if player in unique_heroes:
            idx = unique_heroes.index(player)
            vec[idx] = 1
    return vec

def vectorize_match(players, team1_win) -> tuple[list[int], int]:
    # X = []
    # y = team1_win
    # for player in players:
    #     X.append(player['hero_id'])
    # return X, y
    
    # Instead of this, we can use a unigram model
    # 1. get all unique heroes
    # 2. for each player, create a vector of 0s and 1s
    # 3. concatenate all vectors to get a single vector for the match
    # 4. return X, y
    
    ids = get_hero_id_to_name()
    unique_heroes = list(ids.keys())

    # create a vector for each team
    team1 = [0] * len(unique_heroes)
    team2 = [0] * len(unique_heroes)

    for player in players:
        if player['hero_id'] in unique_heroes:
            idx = unique_heroes.index(player['hero_id'])
            if players.index(player) < 6:
                team1[idx] = 1
            else:
                team2[idx] = 1

    # concatenate the two vectors
    return team1 + team2, team1_win

def preprocess_data():
    files = glob.glob('match_data_*.json')
    X = []
    y = []
    for file in files:
        with open(file) as f:
            data = json.load(f)
            players, team1_win = getComp(data)
            if len(players) != 12:
                continue # skip matches with players that left and got replaced as it breaks size stuff
            vX, vy = vectorize_match(players, team1_win)
            X.append(vX)
            y.append(vy)

    X = np.array(X)
    y = np.array(y)

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    return X_train, X_test, y_train, y_test

def perform_learn(model):
    """returns trained model"""
    print(model)
    X_train, X_test, y_train, y_test = preprocess_data()

    scaler = StandardScaler()
    X_train = scaler.fit_transform(X_train)
    X_test = scaler.transform(X_test)

    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    print(f'Accuracy: {accuracy:.2f}')

    # Example prediction
    # team1 = ['hulk', 'thor', 'iron man', 'hawkeye', 'cloak & dagger', 'mantis']
    # team2 = ['mantis', 'cloak & dagger', 'luna snow', 'black panther', 'adam warlock', 'black widow']
    # team1Ids = [hero_to_id(hero) for hero in team1]
    # team2Ids = [hero_to_id(hero) for hero in team2]

    # comp_vec = comp_to_vector(team1Ids + team2Ids)

    # example_match = np.array([comp_vec])
    # example_match = scaler.transform(example_match)

    # # get probability of each team winning
    # prob = model.predict_proba(example_match)
    # print(f'Team 1 win probability: {prob[0][1]:.2f}')
    # print(f'Team 2 win probability: {prob[0][0]:.2f}')
    return model, scaler

from itertools import combinations


def recommend_greedy_team(enemy_team, hero_pool, model, scaler, selected_team=None, num_iterations=10):
    """
    Runs the greedy team selection multiple times and picks the best one.
    Allows for a partially selected team.

    :param enemy_team: List of hero IDs for the opponent team
    :param hero_pool: List of all available hero IDs
    :param model: Trained ML model
    :param scaler: Trained StandardScaler
    :param selected_team: (Optional) List of currently selected heroes for Team 1
    :param num_iterations: Number of times to run the greedy selection
    :return: Best team composition for Team 1
    """

    best_team_overall = None
    best_prob_overall = 0

    if selected_team is None:
        selected_team = []  # If no heroes are pre-selected, start fresh

    for _ in range(num_iterations):
        current_team = selected_team[:]  # Copy the selected team
        available_heroes = [h for h in hero_pool if h not in current_team]  # Remove selected heroes

        while len(current_team) < 6:  # Fill the remaining slots
            best_hero = None
            best_prob = 0

            random.shuffle(available_heroes)  # Randomize selection order

            for hero in available_heroes:
                if hero in current_team:  # Skip already selected heroes
                    continue

                # Form a temporary team with this hero added
                temp_team = current_team + [hero]

                # If we don’t have enough heroes yet, pad with placeholders
                while len(temp_team) < 6:
                    temp_team.append(random.choice(available_heroes))  # Temporary padding

                # Convert team to vector format
                comp_vec = comp_to_vector(temp_team + enemy_team)  
                example_match = np.array([comp_vec])

                # Scale input
                example_match = scaler.transform(example_match)

                # Predict win probability
                prob = model.predict_proba(example_match)[0][1]

                # Keep track of the best hero to add
                if prob > best_prob:
                    best_prob = prob
                    best_hero = hero

            # Add the best hero to the team
            current_team.append(best_hero)
            available_heroes.remove(best_hero)  # Remove from available heroes

        # Evaluate the final team
        final_comp_vec = comp_to_vector(current_team + enemy_team)
        final_example_match = np.array([final_comp_vec])
        final_example_match = scaler.transform(final_example_match)
        final_prob = model.predict_proba(final_example_match)[0][1]

        # Keep track of the best overall team
        if final_prob > best_prob_overall:
            best_prob_overall = final_prob
            best_team_overall = current_team

    return best_team_overall, best_prob_overall



if __name__ == '__main__':
    enemy_team = ['venom', 'spider-man', 'black panther', 'captain america', 'cloak & dagger', 'rocket racoon']
    current_team = ['hulk', 'spider-man', 'namor']
    enemy_team_ids = [hero_to_id(hero) for hero in enemy_team]
    hero_pool = all_heroes()
    model, scaler = perform_learn(RandomForestClassifier(n_estimators=100, random_state=42))
    best_team, win_prob = recommend_greedy_team(enemy_team_ids, hero_pool, model, scaler, current_team)
    print(f"Recommended Team: {[id_to_hero(id)for id in best_team]} with {win_prob:.2f} probability of winning")
    # perform_learn(RandomForestClassifier(n_estimators=100, random_state=42))
    # print()
    # perform_learn(LogisticRegression())
    # print()
    # perform_learn(KNear(n_neighbors=3))
    # print()
    # perform_learn(SVC(probability=True))
    # print()
    # perform_learn(GaussianNB())
    # print()
    # perform_learn(BernoulliNB())
    # print()
    # perform_learn(XGBClassifier(use_label_encoder=False, eval_metric='logloss'))