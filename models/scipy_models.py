import json
import glob
import numpy as np
import pandas as pd
import random
import pickle
from pathlib import Path

from data.hero_data import hero_to_id, id_to_hero

from data.match_extraction import get_match_composition
from data.vectorizing import comp_to_vector, comp_to_binary_matrix_vector

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier

def vectorize_match(players, team1_win):
    """Transforms match data into a vector and label."""
    vec = comp_to_vector([player['hero_id'] for player in players])
    return vec, team1_win

def preprocess_data(data_glob, split=0.2):
    """Loads and vectorizes match data."""
    files = glob.glob(data_glob)
    X, y = [], []
    
    for file in files:
        with open(file) as f:
            data = json.load(f)
            players, team1_win = get_match_composition(data)
            if len(players) != 12:
                continue
            vX, vy = vectorize_match(players, team1_win)
            X.append(vX)
            y.append(vy)

    X, y = np.array(X), np.array(y)
    print(f'X shape: {X.shape}, y shape: {y.shape}')
    return train_test_split(X, y, test_size=split, random_state=42)

def train_model(model, X_train, y_train, X_test, y_test):
    """Trains and evaluates a model."""
    scaler = StandardScaler()
    X_train, X_test = scaler.fit_transform(X_train), scaler.transform(X_test)

    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)

    return {
        'model': model,
        'scaler': scaler,
        'accuracy': accuracy_score(y_test, y_pred),
        'precision': precision_score(y_test, y_pred, average='macro', zero_division=0),
        'recall': recall_score(y_test, y_pred, average='macro'),
        'f1': f1_score(y_test, y_pred, average='macro')
    }

def save_model(model_data):
    """Saves a trained model to a file."""
    with open('model.pkl', 'wb') as f:
        pickle.dump(model_data, f)

def load_model():
    """Loads a trained model from a file."""
    with open('model.pkl', 'rb') as f:
        return pickle.load(f)

if __name__ == '__main__':
    X_train, X_test, y_train, y_test = preprocess_data('data/raw/match_data_*.json', split=0.2)
    model_data = train_model(RandomForestClassifier(), X_train, y_train, X_test, y_test)
    
    scaler = model_data['scaler']
    model = model_data['model']

    team1 = ['namor', 'thor', 'scarlet witch', 'the thing', 'invisible woman', 'luna snow']
    team2 = ['magneto', 'hawkeye', 'black widow', 'black panther', 'mantis', 'cloak & dagger']

    team1_ids = [hero_to_id(hero) for hero in team1]
    team2_ids = [hero_to_id(hero) for hero in team2]

    example_match = np.array([comp_to_vector(team1_ids + team2_ids)])
    prob = model.predict_proba(scaler.transform(example_match))[0][1]

    print(f"Probability of winning: {prob:.3f}")

    print(f"Model: {model}")
    print(f"Accuracy: {model_data['accuracy']}")
    print(f"Precision: {model_data['precision']}")
    print(f"Recall: {model_data['recall']}")
    print(f"F1 Score: {model_data['f1']}")
