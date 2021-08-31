import spacy 
import nltk
from itertools import combinations, chain
import numpy as np

class SpyMaster:
    
    nlp = spacy.load('en_core_web_lg')
    english_words = set([word.upper() for word in nltk.corpus.words.words()])
    vocab = set([word.upper() for word in nlp.vocab.strings]).intersection(english_words)
    vocab_nlp = list(nlp.pipe(vocab))
    
    @classmethod
    def set_vocab(cls, 
                  possible_words: set) -> None:
        
        cls.vocab = set([word.upper() for word in cls.nlp.vocab.strings if word in possible_words])
    
    def __init__(self, 
                 board_dict: dict, 
                 my_team: str, 
                 alpha1: float = 1,
                 alpha2: float = 1,
                 alpha3: float = 0.5, 
                 alpha4: float = 0.5,
                 alpha5: float = 0.5) -> None: 
        
#     Arguments
#     ------------
#     board_dict : dictionary of the form {'blue': ..., 'orange': ..., 'black': ..., 'orange': ...} with lists of words under each team
#     my_team : string, which team the bot is on (should be a key in board_dict)
#     beta : scoring model parameter beta
#     alpha : scoring model parameter alpha
        
        if my_team not in board_dict or (my_team != 'blue' and my_team != 'orange'):
            raise ValueError('Argument "my_team" should be a key in the dictionary argument "board_dict", and one of (blue, orange)')
            
        self.my_team = my_team
        self.other_team = 'orange' if my_team == 'blue' else 'blue' 
        
        # convert all letters to uppercase when setting instance board words variable
        self.board_dict = {team: [word.upper() for word in words] for team, words in board_dict.items()}
        
        # concatenate all board words into a single list
        self.board_words = list(chain(*self.board_dict.values()))
        self.individual_board_words = list(chain(*[word.split(' ') for word in self.board_words]))
           
        self.team_word_indices = [i for i, word in enumerate(self.board_words) if word in self.board_dict[self.my_team]]
        self.other_team_word_indices = [i for i, word in enumerate(self.board_words) if word in self.board_dict[self.other_team]]
        self.black_word_index = [i for i, word in enumerate(self.board_words) if word in self.board_dict['black']]
            
        # get list of all possible proposal words
        self.proposal_words = list(self.vocab.difference(self.individual_board_words))
            
        # initialise spacy NLP instances
        board_word_nlp = SpyMaster.nlp.pipe(self.board_words)
        
        # get embeddings for words on the board
        self.board_embeddings = np.array([word.vector for word in board_word_nlp])
        # calculate L2 norms for board word embeddings
        board_embedding_norms = np.linalg.norm(self.board_embeddings, axis = 1, ord = 2)
        # norm everything to 1
        self.board_embeddings = self.board_embeddings / board_embedding_norms[:, None]
        
        # get proposal word embeddings, calculate norms
        self.proposal_embeddings = np.array([word.vector for word in self.vocab_nlp if str(word) not in self.individual_board_words])
        proposal_embedding_norms = np.linalg.norm(self.proposal_embeddings, axis = 1, ord = 2)
        # remove words with zero-norm embeddings
        nonzero_norm_mask = proposal_embedding_norms != 0
        self.proposal_embeddings = self.proposal_embeddings[nonzero_norm_mask]
        self.proposal_embeddings = self.proposal_embeddings / proposal_embedding_norms[nonzero_norm_mask, None]
        self.proposal_words = np.array(self.proposal_words)[nonzero_norm_mask].tolist()
        
        # get cosine similarity between words on the board and all possible proposals
        self.proposal_board_similarities = self.proposal_embeddings @ self.board_embeddings.T
        
        self.alpha1 = alpha1
        self.alpha2 = alpha2
        self.alpha3 = alpha3
        self.alpha4 = alpha4
        self.alpha5 = alpha5
        
        self.my_team_score = 0
        self.other_team_score = 0
        
    def make_proposal(self) -> tuple:
        
        best_combination_score = 0
        # loop through possible numbers of words to propose
        for num_words in range(1, len(self.team_word_indices) + 1):
            # loop through unique combinations of those words
            for comb in combinations(self.team_word_indices, num_words):
                # get scores for each proposal
                proposal_scores = self.score(comb)
                highest_score_idx = np.argmax(proposal_scores)
                highest_score = proposal_scores[highest_score_idx]
                # if the best score is higher than the best score seen so far, save the highest scoring word
                if highest_score > best_combination_score:
                    best_combination_score = highest_score
                    target_words = np.array(self.board_words)[list(comb)].tolist()
                    highest_score_word = self.proposal_words[highest_score_idx]
                    
        return target_words, highest_score_word
    
    # score a set of target words
    def score(self, targets):
        
        target_similarities = self.proposal_board_similarities[:, targets]
        other_team_word_similarities = self.proposal_board_similarities[:, self.other_team_word_indices]
        mean_target_similarities = target_similarities.mean(axis = 1)
        mean_other_team_word_similarities = other_team_word_similarities.mean(axis = 1)
        var_other_team_word_similarities = (other_team_word_similarities**2).mean(axis = 1)
        black_word_similarities = self.proposal_board_similarities[:, self.black_word_index[0]]
        team_score_ratio = (self.other_team_score + 1) / (self.my_team_score + 1)
        scores = (self.alpha1 * mean_target_similarities + 
                  self.alpha2 * team_score_ratio * np.log2(len(targets)) -
                  self.alpha3 * mean_other_team_word_similarities -
                  self.alpha4 * var_other_team_word_similarities -
                  self.alpha5 * black_word_similarities)
        return scores