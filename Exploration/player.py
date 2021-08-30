class Player:
    
    def __init__(self):
        
        self.my_team_colour = ''
        
        while self.my_team_colour not in ['Orange', 'Blue']:
            
            cand_colour = input("Which team am I on?") 
            
            if cand_colour in ['Orange', 'Blue']:
                self.my_team_colour = cand_colour
            else:
                cand_colour = input("That's not a valid team colour. Please enter Blue or Orange.")
        
        self.blue_score = 0
        self.orange_score = 0
        self.board_words = set([])
        
        while len(self.board_words) < 25:
            
            cand_board_word = input("Which cards are on the board? {}/25".format(len(self.board_words)+1))
            self.board_words = self.board_words.union(set([cand_board_word]))
        
        input("Who plays first, US/THEM?")
        
    def __call__(self):
        
        cand_board_word = ''
        
        
        
#     def update_from_opp_turn(self):
        
#         # Take input on which cards were flipped
#         cards_revealed = set([])
#         while cand_card not in board_words and card_revealed not "None":
            
#             cand_card = input("Which cards did the opposition team guess? If no more, type 'None'.")
            
#         cards_revealed.union(set(cand_card))
            
#         # Remove revealed cards from board
        
        
        
#         # Change to opposition score
        
#         # Change to our score
        
        
        
        
#         score_to_update = input("What score did they get?")
        
#         for 
    
player = Player()
player()