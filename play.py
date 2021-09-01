# Greet player
print("Hi I'm Codenames-Bot, but you can call me Codey! Let's play codenames!")
time.sleep(2)

# Only accept valid team colours
while my_team_colour not in ['Orange', 'Blue']:
    
    # Ask for input of team colour
    cand_colour = input("Which team am I on?").lower()
    
    # Capitalise first letter of team name
    cand_colour = cand_colour[0].upper() + cand_colour[1:]
    print(cand_colour)
    
    # Check input and advice on issues
    if cand_colour in ['Orange', 'Blue']:
        self.my_team_colour = cand_colour
    else:
        cand_colour = input("That's not a valid team colour. Please enter 'Blue' or 'Orange'.")

# Confirm team assignment
print("Great, go {} team!".format(self.my_team_colour))

role = input("Am I the Spymaster or an Operative?")

while role not in ['Spymaster', 'Operative']:
    
    role = input("Please enter either 'Spymaster' or 'Operative'.")
    
board_dict, board_words = Game.simulate_board(
    
if role == 'Spymaster':
    
    