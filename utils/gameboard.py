import numpy as np

class GameBoard:
    
    def __init__(self, board_words):
        
        if len(board_words) != 25:
            raise ValueError('There should be exactly 25 board words. Try again')
        
        self.board_words = board_words
        self.revealed = {word: False for word in self.board_words}
    
    def print_row(self, row_num, row_width = 10):
        num_letters_per_word = [len(word) for word in self.board_words[(5*col_num):(5*(col_num+1))]]
        row = []
        for i in range(row_width * 5):
            if i == row_width // 2:
                num_letters = num_letters_per_word[i]
                num_spaces = (30 - num_letters) / 2
                num_spaces_left, num_spaces_right = int(np.ceil(num_spaces)), int(np.floor(num_spaces))
                column = '|' + (' '*num_spaces_left) + word + (' '*num_spaces_right) + '|\n'
            elif i < 10:
                column = '|' + (' '*30) + '|'
            else:
                column = '|' + (' '*30) + '|'
            row.append(column)
            row.append(('-'*30) + '\n')
        
        return ''.join(row)
        
    def print_board(self):
        
        print('-'*56)
        for col in range(5):
            self.print_column(col)