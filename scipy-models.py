# load all json files with wildcard matching stats_*.json

import json
import glob
import pprint
from api import *

import numpy as np
import pandas as pd
import scipy
import random

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, RobustScaler
from sklearn.linear_model import LogisticRegression, LinearRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.neighbors import KNeighborsClassifier as KNear
from sklearn.svm import SVC
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score

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

def comp_to_vector(character_ids: list[int]) -> list[int]:
    """Converts a list of character IDs to a vector where the left half is team 1 and the right half is team 2
    IDs are instead based on their index in all_heroes()"""
    hero_ids = all_heroes()
    # act as if the first index is 0 in the result vector
    # for the first half of the characters, add 1 to the index
    # for the second half of the characters, add 1 to the index + len(hero_ids)
    # this way, the first half of the vector is team 1 and the second half is team 2
    res = [1] * len(hero_ids) * 2
    team1 = character_ids[:6]
    team2 = character_ids[6:]

    for hero in team1:
        res[hero_ids.index(hero)] = 1

    for hero in team2:
        res[hero_ids.index(hero) + len(hero_ids)] = 1

    return res

def comp_to_binary_matrix_vector(character_ids: list[int]) -> list[list[int]]:
    """
    Instead of a vector of all the heroes, return a matrix of all_heroes() X all_heroes()
    where a 1 in the matrix indicates those two heroes are pitted against eachother
    """
    hero_ids = all_heroes()
    res = [[0] * len(hero_ids) for _ in range(len(hero_ids))]

    team1 = character_ids[:6]
    team2 = character_ids[6:]

    for hero1 in team1:
        for hero2 in team2:
            res[hero_ids.index(hero1)][hero_ids.index(hero2)] = 1

    # convert to 1d vector
    res = [item for sublist in res for item in sublist]
    return res

def vectorize_match(players, team1_win) -> tuple[list[int], int]:
    # vec = comp_to_vector([player['hero_id'] for player in players])
    vec = comp_to_binary_matrix_vector([player['hero_id'] for player in players])
    return vec, team1_win

def preprocess_data(data_glob, split=0.2):
    files = glob.glob(data_glob)
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

    print(f'X shape: {X.shape}')
    print(f'y shape: {y.shape}')

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=split, random_state=42)
    return X_train, X_test, y_train, y_test

def train_model(model, X_train, y_train, X_test, y_test):
    """returns trained model"""
    print(model)

    scaler = StandardScaler()
    X_train = scaler.fit_transform(X_train)
    X_test = scaler.transform(X_test)

    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    precision = precision_score(y_test, y_pred, average='macro', zero_division=0)
    recall = recall_score(y_test, y_pred, average='macro')
    f1 = f1_score(y_test, y_pred, average='macro')
    return {
        'model': model,
        'scaler': scaler,
        'accuracy': accuracy,
        'precision': precision,
        'recall': recall,
        'f1': f1
    }

def recommend_greedy_team(enemy_team, hero_pool, model, scaler, selected_team=None, num_iterations=3):
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

def train_and_save_model(model, X_train, y_train, X_test, y_test):
    res = train_model(model, X_train, y_train, X_test, y_test)

    #store the model
    import pickle
    with open('model.pkl', 'wb') as f:
        pickle.dump(res, f)


if __name__ == '__main__':
    X_train, X_test, y_train, y_test = preprocess_data('match_data_*.json', split=0.2)

    # write data to files
    np.save('X_train.npy', X_train)
    np.save('X_test.npy', X_test)
    np.save('y_train.npy', y_train)
    np.save('y_test.npy', y_test)
    
    #load model
    import pickle
    with open('model.pkl', 'rb') as f:
        model = pickle
        model = pickle.load(f)

    # fit scaler
    scaler = StandardScaler()
    X_train = scaler.fit_transform(X_train)
    X_test = scaler.transform(X_test)


    coef_df = pd.DataFrame(model['model'].coef_, index=model['model'].classes_)

    probs = model['model'].predict_proba(X_train[:5])  # First 5 predictions
    # print the probs to 3 decimal places
    # print(np.round(probs, 3))

    
    # print(f"Model: {model['model']}")
    # print(f"Accuracy: {model['accuracy']}")
    # print(f"Precision: {model['precision']}")
    # print(f"Recall: {model['recall']}")
    # print(f"F1: {model['f1']}")
    # print()

    matrices = []
    for coef in coef_df.iterrows():
        matrices.append(np.array(coef[1]).reshape(len(all_heroes()), len(all_heroes())))
    
    win_matrix = matrices[1]  # Win matrix
    loss_matrix = matrices[0]  # Loss matrix
    tie_matrix = matrices[2]  # Tie matrix

    # Get the hero names
    hero_names = all_heroes() # list index is ID in matrix, but value is hero ID
    hero_names = [id_to_hero(hero) for hero in hero_names]
    
    # print table of Their pick | Our pick | Win %
    print(f'{"Their Pick":<20} {"Our Pick":<20} {"Win %":<5}')
    print('-' * 45)
    for i in range(len(all_heroes())):
        matchup = win_matrix[i]
        best_pick = np.argmax(matchup)
        print(f"{hero_names[i]:<20} {hero_names[best_pick]:<20} {matchup[best_pick]:.2f}")