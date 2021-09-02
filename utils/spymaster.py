import spacy 
import nltk
from itertools import combinations, chain
import numpy as np
from utils.game import Game

class SpyMaster(Game):
    
    nlp = spacy.load('en_core_web_lg')
    
    with open('../data/vocab.txt', 'r') as file:
        english_words = set([word.strip('\n').upper() for word in file.readlines()])

    vocab = list(set([word.upper() for word in nlp.vocab.strings]).intersection(english_words))
    vocab_nlp = list(nlp.pipe(vocab))
    vocab_embeddings = np.array([word.vector for word in vocab_nlp])
    vocab_embedding_norms = np.linalg.norm(vocab_embeddings, axis = 1, ord = 2)
    vocab_embeddings = vocab_embeddings[vocab_embedding_norms != 0]
    vocab_embeddings = vocab_embeddings / vocab_embedding_norms[vocab_embedding_norms != 0, None]
    vocab = np.array(vocab)[vocab_embedding_norms != 0].tolist()
    
    @classmethod
    def set_vocab(cls, 
                  possible_words: set) -> None:
        
        cls.vocab = list(set([word.upper() for word in cls.nlp.vocab.strings if word in possible_words]))
        cls.vocab_nlp = list(nlp.pipe(cls.vocab))
        cls.vocab_embeddings = np.array([word.vector for word in cls.vocab_nlp])
        cls.vocab_embedding_norms = np.linalg.norm(cls.vocab_embeddings, axis = 1, ord = 2)
        cls.vocab_embeddings = cls.vocab_embeddings[cls.vocab_embedding_norms != 0]
        cls.vocab_embeddings = cls.vocab_embeddings / cls.vocab_embedding_norms[cls.vocab_embedding_norms != 0, None]
        cls.vocab = np.array(cls.vocab)[cls.vocab_embedding_norms != 0].tolist()
    
    @property
    def word_indices(self):
        indices = {}
        for team in [self.my_team, self.other_team, 'white', 'black']:
            indices[team] = [i for i, word in enumerate(self.board_words) if 
                             word in self.board_dict[team] and not self.revealed[word]]
        return indices
    
    def __init__(self, 
                 board_dict: dict, 
                 board_words: list, 
                 my_team: str, 
                 alpha1: float = 1,
                 alpha2: float = 1,
                 alpha3: float = 0.5, 
                 alpha4: float = 0.5,
                 alpha5: float = 0.5) -> None: 
        
#     Arguments
#     ------------
#     board_dict : dictionary of the form {'blue': ..., 'orange': ..., 'black': ..., 'white': ...} with lists of words under each team
#     my_team : string, which team the bot is on (should be a key in board_dict)
#     beta : scoring model parameter beta
#     alpha : scoring model parameter alpha
        
    
        # convert all letters to uppercase when setting instance board words variable
        self.board_dict = {team: [word.upper() for word in words] for team, words in board_dict.items()}
        
        # concatenate all board words into a single list
        super().__init__(my_team, board_words)
        
        self.individual_board_words = list(chain(*[word.split(' ') for word in self.board_words]))
           
        # get list of all possible proposal words
        self.proposal_word_indices = [(i, word) for i, word in enumerate(self.vocab) if word not in self.board_words]
        
        # initialise spacy NLP instances
        board_word_nlp = SpyMaster.nlp.pipe(self.board_words)
        
        # get embeddings for words on the board
        self.board_embeddings = np.array([word.vector for word in board_word_nlp])
        # calculate L2 norms for board word embeddings
        board_embedding_norms = np.linalg.norm(self.board_embeddings, axis = 1, ord = 2)
        # norm everything to 1
        self.board_embeddings = self.board_embeddings / board_embedding_norms[:, None]
        
        # get proposal word embeddings, norm everything
        self.proposal_embeddings = self.vocab_embeddings[[i for i, word in self.proposal_word_indices]]
        self.proposal_words = [word for i, word in self.proposal_word_indices]
        
        # get cosine similarity between words on the board and all possible proposals
        self.proposal_board_similarities = self.proposal_embeddings @ self.board_embeddings.T
        
        self.alpha1 = alpha1
        self.alpha2 = alpha2
        self.alpha3 = alpha3
        self.alpha4 = alpha4
        self.alpha5 = alpha5
        
        self.my_team_score = 8 - len(self.word_indices[self.my_team])
        self.other_team_score = 8 - len(self.word_indices[self.other_team])
        
    def make_proposal(self) -> tuple:
        
        best_combination_score = -100
        # loop through possible numbers of words to propose
        for num_words in range(1, len(self.word_indices[self.my_team]) + 1):
            # loop through unique combinations of those words
            for comb in combinations(self.word_indices[self.my_team], num_words):
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
    def score(self, targets: list) -> np.ndarray:
        
        target_similarities = self.proposal_board_similarities[:, targets]
        non_team_word_similarities = self.proposal_board_similarities[:, self.word_indices['white'] + self.word_indices[self.other_team]]
        mean_target_similarities = target_similarities.mean(axis = 1)
        mean_non_team_word_similarities = non_team_word_similarities.mean(axis = 1)
        var_non_team_word_similarities = (non_team_word_similarities**2).mean(axis = 1)
        black_word_similarities = self.proposal_board_similarities[:, self.word_indices['black'][0]]
        team_score_ratio = (self.other_team_score + 1) / (self.my_team_score + 1)
        scores = (self.alpha1 * mean_target_similarities + 
                  self.alpha2 * np.exp(-len(targets)) * len(targets)**2.7 - 
                  self.alpha3 * mean_non_team_word_similarities -
                  self.alpha4 * var_non_team_word_similarities -
                  self.alpha5 * black_word_similarities)
