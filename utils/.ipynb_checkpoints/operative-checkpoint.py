import spacy 
import numpy as np
from collections import OrderedDict

class Operative:
    
    nlp = spacy.load('en_core_web_lg')
    
    def __init__(self, board_words: list) -> None: 
        
        ##     Arguments
        ##     ------------
        ##     board_words : list of the form [] with remaining board words
        ##     my_team : string, which team the bot is on (should be a key in board_dict)
            
        self.board_words = board_words
        # initialise spacy NLP instances
        board_word_nlp = Operative.nlp.pipe(self.board_words)
        
        # get embeddings for words on the board
        self.board_embeddings = np.array([word.vector for word in board_word_nlp])
        
        # calculate L2 norms for board word embeddings
        board_embedding_norms = np.linalg.norm(self.board_embeddings, axis=1, ord=2)
        
        # norm everything to 1
        self.board_embeddings = self.board_embeddings / board_embedding_norms[:, None]

        self.my_team_score = 0
        self.other_team_score = 0
     
    def Guess(self, clue_word, guess_num: int):
    
        ## clue_word (token) - The word given to the Operative as a clue
        ## board_wors (list of token) - Words remaining on the board
        ## guess_num (int) - Number of board_words linked to this clue_word    

        # Create dictionary to hold distance of board words to clue word
        word_dict = OrderedDict()
        clue_word = Operative.nlp(clue_word)

        # Calculate distances and add to dictionary
        for word, emb in zip(self.board_words, self.board_embeddings):

            word_dict[word] = emb @ (clue_word.vector / np.linalg.norm(clue_word.vector, ord = 2))
            
        # Order dictionary
        words = [k for k, v in sorted(word_dict.items(), key=lambda item: item[1])]
        
        guess = words[-guess_num:]       
        
        return guess