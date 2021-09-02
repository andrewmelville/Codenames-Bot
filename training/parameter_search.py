import spacy 
import nltk
import subprocess
import optuna
import sys
import numpy as np
import pkg_resources
import pickle
sys.path.insert(0, '..')

from utils.game import Game

try:
    pkg_resources.get_distribution('en_core_web_lg')
except pkg_resources.DistributionNotFound:
    subprocess.call(['python', '-m', 'spacy', 'download', 'en_core_web_lg'])

from utils.spymaster import SpyMaster
from utils.operative import Operative
    
with open('../data/wordlist-eng.txt', 'r') as file:
    words = [word.strip('\n') for word in file.readlines()]

def objective(trial):
    
    alpha2 = trial.suggest_float(low = 0.0001, high = 1, log = True, name = 'alpha2')
    alpha3 = trial.suggest_float(low = 0.0001, high = 1, log = True, name = 'alpha3')
    alpha4 = trial.suggest_float(low = 0.0001, high = 1, log = True, name = 'alpha4')
    alpha5 = trial.suggest_float(low = 0.0001, high = 1, log = True, name = 'alpha5')
    alpha6 = trial.suggest_float(low = 0.0001, high = 1, log = True, name = 'alpha6')
    beta1 = trial.suggest_float(low = 0.0001, high = 1, log = True, name = 'beta1')
    
    np.random.seed(123)

    scores = []
    for i in range(1000):
        board_dict, board_words = Game.simulate_board(words)
        spymaster = SpyMaster(board_dict, 
                              board_words,
                              my_team = 'blue', 
                              alpha2 = alpha2, 
                              alpha3 = alpha3, 
                              alpha4 = alpha4, 
                              alpha5 = alpha5, 
                              alpha6 = alpha6,
                              beta1 = beta1)
        operative = Operative(board_words)
        targets, proposal = spymaster.make_proposal()
        guess = operative.Guess(proposal, len(targets))
        score = 0
        for word in reversed(guess):
            if word in targets:
                score += 1
            elif word in spymaster.board_dict[spymaster.other_team]:
                score -= 1
                break
            elif word in spymaster.board_dict['black']:
                score = -8
                break
            elif word in spymaster.board_dict['white']:
                break
        scores.append(score)
        
    mean_score = np.mean(scores)
    
    return mean_score

study = optuna.create_study(direction = 'maximize',
                            pruner = optuna.pruners.MedianPruner(), 
                            sampler = optuna.samplers.TPESampler(seed = 123))
study.optimize(objective, n_trials = 50)

trials = study.trials_dataframe()
    
trials.to_csv('../data/hyperparameter_search_results.csv', index = False)

pickle.dump(study, open('../data/study.pkl', 'wb'))
