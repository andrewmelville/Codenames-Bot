import spacy 
import nltk
import subprocess
import optuna
import sys
import numpy as np
sys.path.insert(0, '..')

if 'en_core_web_lg' not in sys.modules:
    subprocess.call(['python', '-m', 'spacy', 'download', 'en_core_web_lg'])
nltk.download('words')

from utils.spymaster import SpyMaster
from utils.operative import Operative

def simulate_board(possible_words):
    
    sampled_words = np.random.choice(possible_words, size = 25)
    sampling_probs = np.arange(1, 9) / np.arange(1, 9).sum()
    board = {'blue': list(sampled_words[:8][:np.random.choice(np.arange(1, 9), size = 1, p = sampling_probs)[0]]),
             'orange': list(sampled_words[8:16][:np.random.choice(np.arange(1, 9), size = 1, p = sampling_probs)[0]]),
             'white': list(sampled_words[16:24][:np.random.choice(9, size = 1, p = np.arange(1, 10) / np.arange(1, 10).sum())[0]]),
             'black': [sampled_words[24]]}
    
    return board
    
with open('../data/wordlist-eng.txt', 'r') as file:
    words = [word.strip('\n') for word in file.readlines()]

def objective(trial):
    
    alpha1 = trial.suggest_float(low = 0.0001, high = 1, log = True, name = 'alpha1')
    alpha2 = trial.suggest_float(low = 0.0001, high = 1, log = True, name = 'alpha2')
    alpha3 = trial.suggest_float(low = 0.0001, high = 1, log = True, name = 'alpha3')
    alpha4 = trial.suggest_float(low = 0.0001, high = 1, log = True, name = 'alpha4')
    alpha5 = trial.suggest_float(low = 0.0001, high = 1, log = True, name = 'alpha5')
    
    np.random.seed(123)

    scores = []
    for i in range(1000):
        game_board = simulate_board(words)
        spymaster = SpyMaster(game_board, my_team = 'blue', 
                              alpha1 = alpha1, alpha2 = alpha2,
                              alpha3 = alpha3, alpha4 = alpha4, 
                              alpha5 = alpha5)
        operative = Operative(spymaster.board_words)
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
                score = -len(spymaster.other_team_word_indices)
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