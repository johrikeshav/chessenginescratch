# this is the driver file that runs the game
# it will handle all i/o
# it also displays the current gamestate

import chessengine
import pygame as p
import time

p.init()

width = height = 800
dimm = 8
sq_size = height/dimm
max_fps = 15
images = {} # dictionary which maps the piece rep to its image

bgcolor = (78,78,78)
light = (255,255,255)
dark = (78,120,55)
piece_highlight = (255,255,0)
move_highlight = (0,71,171)

# function to load images, computationally expensive, called only once
# eg. to load a white pawn, use images["wP"] 
def load_images():
    pieces = ["wP","wR","wN","wB","wQ","wK","bP","bR","bN","bB","bQ","bK"]
    for piece in pieces:
        images[piece] = p.transform.scale((p.image.load("images/"+ piece +".png")),(0.8*sq_size,0.8*sq_size))

# main driver (handles i/o, updates board and graphics)
def main():
    p.init()
    screen = p.display.set_mode((width,height)) # TO DO : set window title to chess game
    clock = p.time.Clock()
    screen.fill(bgcolor)
    gs = chessengine.chess_engine()
    valid_moves = gs.get_valid_moves() # list storing all allowed moves, costly to call
    move_made = False # when this var is true, a move has been made, gamestate changed and need to recalc valid moves

    #print(gs.board)

    load_images() # before gameloop

    running = True
    selected_sq = () # no square is selected at start, keeps track of last click of user (tuple: (row, col))
    player_clicks = [] # keep track of player's 1st and 2nd clicks [(6,4),(4,4)]

    while running:
        
        for e in p.event.get():
            
            if e.type == p.QUIT:
                running = False
            
            # KEYBOARD COMMANDS
            elif e.type == p.KEYDOWN:
                if e.key == p.K_z:
                    # print("z pressed") # debugging line
                    gs.undo_move()
                    move_made = True                    
            # MOUSE HANDLER
            elif e.type == p.MOUSEBUTTONDOWN: 
                location = p.mouse.get_pos() # getting the location of the mouse
                col = int(location[0]//sq_size)
                row = int(location[1]//sq_size) 
                # print(selected_sq)         # debugging line
                # print(player_clicks)       # debugging line
                if selected_sq == (row,col): # checking if the user selected the same square twice 
                    #print("selected sq is unselected") # debugging line
                    selected_sq = ()          # unselecting the square
                    player_clicks = []        # clearing player clicks
                else:
                    selected_sq = (row,col)
                    player_clicks.append(selected_sq)
                if len(player_clicks) == 2: # player has made the 2nd click
                    move = chessengine.Move(player_clicks[0],player_clicks[1],gs.board)
                    #print(type(gs.get_valid_moves))   # debugging line
                    #print(type(valid_moves))            # debugging line
                    #print(valid_moves)                  # debugging line
                    
                    for i in range(len(valid_moves)):
                        if move == valid_moves[i]:
                            print(move.get_chess_notation())
                            gs.make_move(valid_moves[i])
                            move_made = True
                            selected_sq = ()
                            player_clicks = []                 
                    if not move_made:
                            print("Invalid Move")
                            player_clicks = [selected_sq]  

                if gs.checkmate:
                    if gs.white_to_move:
                        print("BLACK WINS")
                    else:
                        print("WHITE WINS")       
                        

                    # print(gs.board) # debugging line
                    # print(gs.move_log[-1].piece_captured) # debugging line

        if move_made:
            valid_moves = gs.get_valid_moves()
            move_made = False
        
        draw_gamestate(screen,gs,valid_moves,selected_sq) 
        clock.tick(max_fps)
        p.display.flip()

# highligts all possible moves for a selected piece
def highlight_squares(screen, gs, valid_moves, selected_sq):

    if selected_sq != ():
        row,col = selected_sq # making sure that the selected square is same color as player supposed to move
        if (gs.board[row][col][0] == "w" and gs.white_to_move) or (gs.board[row][col][0] == "b" and not gs.white_to_move):
            # highlighting the selected square
            s = p.Surface((sq_size,sq_size))
            s.set_alpha(100) # transparency value (0:completely transparent, 255:completely opaque)
            s.fill(piece_highlight)
            screen.blit(s, (col*sq_size,row*sq_size))
            for move in valid_moves:
                if move.start_row == row and move.start_col == col:
                    sq = p.Surface((sq_size,sq_size))
                    sq.set_alpha(100)
                    sq.fill(move_highlight)
                    screen.blit(sq, (move.end_col*sq_size,move.end_row*sq_size))

    pass

# responsible for all graphics in a game
def draw_gamestate(screen,gs,valid_moves,selected_sq):
    draw_board(screen)           # draws the squares on the board
    highlight_squares(screen,gs,valid_moves,selected_sq)
    draw_pieces(screen,gs.board) # draws the pieces on the board
    pass

def draw_board(screen):
    for row in range(8):
        for col in range(8):
            if((row+col)%2): # dark squares
                p.draw.rect(screen, dark,(col * sq_size, row * sq_size, sq_size, sq_size))
            else:        # light squares
                p.draw.rect(screen, light,(col * sq_size, row * sq_size, sq_size, sq_size))
    pass

def draw_pieces(screen,board):
    for row in range(8):
        for col in range(8):
            if(board[row][col]!="__"):
                screen.blit(images[board[row][col]],((col * sq_size)+10, (row * sq_size)+10, sq_size, sq_size))
    pass


main()