import numpy as np

class GameBoard:
    
    def __init__(self, board_words):
        
        if len(board_words) != 25:
            raise ValueError('There should be exactly 25 board words. Try again')
        
        self.board_words = board_words
        self.revealed = {word: False for word in self.board_words}
    
    def print_row(self, row_num, col_width = 30, row_height = 10):
        
        # get words that will be in the row, based on the row number provided
        row_words = self.board_words[(5*row_num):(5*(row_num+1))]
        # get the length of each word in the row
        num_letters_per_word = [len(word) for word in row_words]
        # initialise dictionary for storing row lines
        row_lines = {}
        # loop through individual lines in the row (each row will consist of "row_height" lines)
        for row_line in range(row_height):
            # each row line will be created from a list of "cell_lines" (lines within each cell)
            row_lines[row_line] = []
            # within each row line, loop over the five columns
            for col in range(5):
                # if we are in the first column, we need a border | on the left
                if col == 0:
                    # if we are in the middle of the row, the row line should contain the word
                    if row_line == row_height // 2:
                        # get the word that we are putting in the column
                        word = row_words[col]
                        # get how many letters are in the word, to determine how many spaces we need to pad the cell
                        num_letters = num_letters_per_word[col]
                        # get the total number of spaces we will need in the cell
                        num_spaces = col_width - num_letters
                        # partition the total number of spaces between the left and right sides of the cell
                        num_spaces_left, num_spaces_right = int(np.ceil(num_spaces / 2)), int(np.floor(num_spaces / 2))
                        # create the string for the line of the cell
                        cell_line = '|' + (' '*num_spaces_left) + word + (' '*num_spaces_right) + '|'
                    else:
                        # if we are not in the middle of the row, we just want the line of the cell to be empty
                        cell_line = '|' + (' '*col_width) + '|'
                # exactly the same as above but without adding a left border to the cell_line
                else:
                    if row_line == row_height // 2:
                        word = row_words[col]
                        num_letters = num_letters_per_word[col]
                        num_spaces = col_width - num_letters
                        num_spaces_left, num_spaces_right = int(np.ceil(num_spaces / 2)), int(np.floor(num_spaces / 2))
                        cell_line = (' '*num_spaces_left) + word + (' '*num_spaces_right) + '|'
                    else:
                        cell_line = (' '*col_width) + '|'
                # append each of the cell lines to the row lines list for that row
                row_lines[row_line].append(cell_line)
            # join all the cell lines into a single string
            row_lines[row_line] = ''.join(row_lines[row_line])
            # add a new line character
            row_lines[row_line] = row_lines[row_line]
            
        # once the entire dictionary has been assembled, print the row lines
        for row_line in row_lines:
            print(row_lines[row_line])
        
    def print_board(self, board_size = 120):
        
        print('-'*(board_size+5))
        for row in range(5):
            self.print_row(row, col_width = board_size // 5)
            print('-'*(board_size+5))