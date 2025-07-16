# this file stores info about current state of game
# we store all valid moves here 
# we also store a move log in here

class chess_engine():
    def __init__(self):
        
        # board is a 2D 8x8 list
        # blank spaces are represented by __
        # a 'w' prefix indicates a white piece, a 'b' prefix indicates a black one
        # R = rook, N = knight, B = bishop, Q = queen, K = king, P = pawn

        self.board = [
            ["bR","bN","bB","bQ","bK","bB","bN","bR"],
            ["bP","bP","bP","bP","bP","bP","bP","bP"],
            ["__","__","__","__","__","__","__","__"],
            ["__","__","__","__","__","__","__","__"],
            ["__","__","__","__","__","__","__","__"],
            ["__","__","__","__","__","__","__","__"],
            ["wP","wP","wP","wP","wP","wP","wP","wP"],
            ["wR","wN","wB","wQ","wK","wB","wN","wR"]
            ]
        
        self.move_functions = {'P':self.get_pawn_moves,'R':self.get_rook_moves,'N':self.get_knight_moves,
                               'B':self.get_bishop_moves,'Q':self.get_queen_moves,'K':self.get_king_moves}
        self.white_to_move = True 
        self.move_log = [] # storing all previous moves in a list
    
        self.white_king_location = (7,4)
        self.black_king_location = (0,4)

        self.checkmate = False
        self.stalemate = False

        self.enpassant_possible = ()

        self.current_castling_rights = castling_rights(True,True,True,True)
        self.castling_rights_log = [castling_rights(self.current_castling_rights.white_king_side,self.current_castling_rights.black_king_side
                                                   ,self.current_castling_rights.white_queen_side,self.current_castling_rights.black_queen_side)]

    def make_move(self,move): # takes a move and executes it(no work for castling, en-passant & promotion)
        
        self.board[move.start_row][move.start_col] = "__"         # removing piece from original pos
        self.board[move.end_row][move.end_col] = move.piece_moved # moving the piece to new pos
        self.move_log.append(move)                                # logging the move 
        self.white_to_move = not self.white_to_move               # switching turns
    
        # updating the king's location if moves
        if move.piece_moved[1] == "K":     # checking if a king moved
            if move.piece_moved[0] == "w": # white king moved        
                self.white_king_location = (move.end_row,move.end_col)
            else:                          # black king moved
                self.black_king_location = (move.end_row,move.end_col)

        # pawn promotion
        if move.is_pawn_promotion:
            self.board[move.end_row][move.end_col] = move.piece_moved[0] + 'Q' # TO DO : allow for promotion to R/N/B/Q and generate valid moves for all those in testing as well
        
        # en passant
        if move.is_enpassant_move:
            self.board[move.start_row][move.end_col] = "__"

        if move.piece_moved[1] == "P" and abs(move.start_row-move.end_row) == 2:
            self.enpassant_possible = ((move.start_row+move.end_row)//2,move.start_col)
        else:
            self.enpassant_possible = ()
        
        # castling rights (need to be updated whenever king/rook moves)
        self.update_castling_rights(move)    
        self.castling_rights_log.append(castling_rights(self.current_castling_rights.white_king_side,self.current_castling_rights.black_king_side
                                                   ,self.current_castling_rights.white_queen_side,self.current_castling_rights.black_queen_side))
        
        # making the castling move
        if move.is_castling_move:

            if move.end_col-move.start_col == 2: # this is a king side castle
                self.board[move.end_row][move.end_col-1] = self.board[move.end_row][move.end_col+1] # placing a rook beside the king
                self.board[move.end_row][move.end_col+1] = "__"     # removing the king side rook

            else: # this is a queen side castle
                self.board[move.end_row][move.end_col+1] = self.board[move.end_row][move.end_col-2] # placing a rook beside the king 
                self.board[move.end_row][move.end_col-2] = "__"     # removing the queen side rook 

        pass

    def undo_move(self): # reverses the last move
        if len(self.move_log) != 0:
            last_move = self.move_log.pop()
            self.board[last_move.end_row][last_move.end_col] = last_move.piece_captured  # replacing the captured piece 
            self.board[last_move.start_row][last_move.start_col] = last_move.piece_moved # placing the moved piece at its original square
            self.white_to_move = not self.white_to_move # switching turns back

            if last_move.piece_moved[1] == "K": # a king move is to be undone

                if last_move.piece_moved[0] == "w": # white king move is to be undone
                    self.white_king_location = (last_move.start_row,last_move.start_col)

                else:   # black king move is to be undone
                    self.black_king_location = (last_move.start_row,last_move.start_col)

            # undoing an enpassant move
            if last_move.is_enpassant_move:
                self.board[last_move.end_row][last_move.end_col] = "__"
                self.board[last_move.start_row][last_move.end_col] = last_move.piece_captured
                self.enpassant_possible = (last_move.end_row,last_move.end_col)
            if last_move.piece_moved[1] == "P" and abs(last_move.start_row-last_move.end_row) == 2:
                self.enpassant_possible = ()

            # undoing castling rights
            self.castling_rights_log.pop()
            new_rights = self.castling_rights_log[-1] # getting rid of old castling rights and setting the current castling rights to what they were prior
            self.current_castling_rights = castling_rights(new_rights.white_king_side, new_rights.black_king_side, new_rights.white_queen_side, new_rights.black_queen_side) 

            # undoing a castle
            if last_move.is_castling_move:
                
                if last_move.end_col - last_move.start_col == 2: # undoing a king side castle

                    self.board[last_move.end_row][last_move.end_col+1] = self.board[last_move.end_row][last_move.end_col-1] # placing the rook back in the corner
                    self.board[last_move.end_row][last_move.end_col-1] = "__" # removing the rook that moved

                else: # undoing a queen side castle

                    self.board[last_move.end_row][last_move.end_col-2] = self.board[last_move.end_row][last_move.end_col+1] # placing the rook back in the corner
                    self.board[last_move.end_row][last_move.end_col+1] = "__" # removing the rook that moved
        pass

    def update_castling_rights(self,move):
        
        if move.piece_moved == "wK": # if white king is moved, white looses all castling rights
            self.current_castling_rights.white_king_side = False
            self.current_castling_rights.white_queen_side = False

        if move.piece_moved == "bK": # if black king is moved, black looses all castling rights
            self.current_castling_rights.black_king_side = False
            self.current_castling_rights.black_queen_side = False

        if move.piece_moved == "wR": # white rook moved, need to check which side white rook

            if move.start_row == 7: # making sure that if the pawn in front of the rook promotes, doesnt trigger the castling rights off
                if move.start_col == 0: # queen side rook moved
                    self.current_castling_rights.white_queen_side = False
                if move.start_col == 7: # king side rook moved
                    self.current_castling_rights.white_king_side = False

        if move.piece_moved == "bR": # black rook moved, need to check which one

            if move.start_row == 0: # making sure that if the pawn in front of the rook promotes, doesnt trigger the castling rights off
                if move.start_col == 0: # queen side rook moved
                    self.current_castling_rights.black_queen_side = False
                if move.start_col == 7: # king side rook moved
                    self.current_castling_rights.black_king_side = False

        if move.piece_captured == "wR":

            if move.end_row == 7: # white rook captured
                if move.end_col == 7: # king side rook captured
                    self.current_castling_rights.white_king_side = False

                if move.end_col == 0: # queen side rook captured
                    self.current_castling_rights.white_queen_side = False

            if move.end_row == 0: # black rook captured
                if move.end_col == 7: # king side rook captured
                    self.current_castling_rights.black_king_side = False
                
                if move.end_col == 0: # queen side rook captured
                    self.current_castling_rights.black_queen_side = False
        pass

    def get_valid_moves(self): # moves that can be actually made without walking into a check
        
        # debugging lines
        """ for log in self.castling_rights_log:    
            print(log.white_king_side, log.white_queen_side, log.black_king_side, log.black_queen_side, end=",")
        print()
        print("current castling rights : ")
        print(self.current_castling_rights.white_king_side,self.current_castling_rights.white_queen_side,self.current_castling_rights.black_king_side,self.current_castling_rights.black_queen_side)
         """
        
        temp_enpassant_possible = self.enpassant_possible
        temp_castling_rights = castling_rights(self.current_castling_rights.white_king_side,self.current_castling_rights.black_king_side
                                              ,self.current_castling_rights.white_queen_side,self.current_castling_rights.black_queen_side)
        # generating all of our possible moves regardless of legality

        moves = self.get_possible_moves()

        if self.white_to_move:
            self.get_castling_moves(self.white_king_location[0],self.white_king_location[1],moves)
        else:
            self.get_castling_moves(self.black_king_location[0],self.black_king_location[1],moves)

        # make each move

        for i in range(len(moves)-1,-1,-1):     # iterating through list of moves in reverse such that removal
                                                # of elements(and the subsequent change in indices) does not 
                                                # cause elements to get skipped
            self.make_move(moves[i])            # going to each of our moves and making them
                                                # making the move also shifts the turn to the opp, so flipping that
            self.white_to_move = not self.white_to_move
            if self.in_check():                 # if the current move we are evaluating puts us in check then it is discarded
                moves.remove(moves[i])
            self.white_to_move = not self.white_to_move # calling the in_check method also flips the white_to_move variable
            self.undo_move()

        if len(moves)==0:
            if self.in_check(): # no more possible moves and player in check
                self.checkmate = True
            else:               # no more possible moves and player not in check
                self.stalemate = True
        else:                   # done to make sure undoing a move allows the game to come out of stale/checkmate
            self.checkmate = False
            self.stalemate = False
        self.enpassant_possible = temp_enpassant_possible
        self.current_castling_rights = temp_castling_rights
        return moves
        pass

    def in_check(self): # evaluates if we are in check right now
        
        if self.white_to_move: # white's turn to move
            return self.square_under_attack(self.white_king_location[0],self.white_king_location[1])
        else:
            return self.square_under_attack(self.black_king_location[0],self.black_king_location[1])
        
        pass    

    def square_under_attack(self,row,col):  # evaluates if the current square is under attack

        self.white_to_move = not self.white_to_move
        opp_moves = self.get_possible_moves()

        for move in opp_moves:
            if move.end_row == row and move.end_col == col:
                self.white_to_move = not self.white_to_move
                return True
        self.white_to_move = not self.white_to_move
        return False
        pass

    def get_possible_moves(self): # all possible moves that can be made regardless of if they end up in a check
        moves = []
        for row in range(len(self.board)):
            for col in range(len(self.board[row])):
                turn = self.board[row][col][0]
                if (turn == 'w' and self.white_to_move) or (turn == 'b' and not self.white_to_move):
                    piece = self.board[row][col][1]

                    self.move_functions[piece](row,col,moves) # calls appropriate move functions for each piece   
        return moves
        pass    

    def get_pawn_moves(self,row,col,moves): # gets all pawn moves for pawn at row, col and appends to list
        
        if self.white_to_move: # getting white pawn moves
            
            # one sq forward
            if row != 0: # making sure pawn is not at last row
                if self.board[row-1][col] == "__": # the square in front is empty
                    moves.append(Move((row,col),(row-1,col),self.board))
            
            # two sq forward
            if row == 6: # making sure pawn is at starting positon
                if self.board[row-1][col] == "__" and self.board[row-2][col] == "__": # checking both squares in front
                    moves.append(Move((row,col),(row-2,col),self.board))

            # 1 sq diagnal right
            if col != 7: # checking if pawn is at right edge
                if self.board[row-1][col+1][0] == "b": # making sure diag sq has a black piece
                    moves.append(Move((row,col),(row-1,col+1),self.board))
                elif (row-1,col+1) == self.enpassant_possible:
                    moves.append(Move((row,col),(row-1,col+1),self.board,is_enpassant_move=True))

            # 1 sq diag left
            if col != 0: # checking if pawn is at left edge
                if self.board[row-1][col-1][0] == "b": # making sure diag sq has a black piece
                    moves.append(Move((row,col),(row-1,col-1),self.board))
                elif (row-1,col-1) == self.enpassant_possible:
                    moves.append(Move((row,col),(row-1,col-1),self.board,is_enpassant_move=True))
        
        else: # getting black pawn moves
            
            # one sq forward
            if row != 7: # checking if pawn is at last row
                if self.board[row+1][col] == "__": # the square in front is empty
                    moves.append(Move((row,col),(row+1,col),self.board))
        
            # two sq forward
            if row == 1:
                if self.board[row+1][col] == "__" and self.board[row+2][col] == "__": # checking both squares in front and if pawn at starting pos
                    moves.append(Move((row,col),(row+2,col),self.board))

            # 1 sq diagnal right
            if col != 7: # checking if pawn is at right edge
                if self.board[row+1][col+1][0] == "w": # making sure diag sq has a white piece
                    moves.append(Move((row,col),(row+1,col+1),self.board))
                elif (row+1,col+1) == self.enpassant_possible:
                    moves.append(Move((row,col),(row+1,col+1),self.board,is_enpassant_move=True))

            # 1 sq diag left
            if col != 0: # checking if pawn is at left edge
                if self.board[row+1][col-1][0] == "w": # making sure diag sq has a white piece
                    moves.append(Move((row,col),(row+1,col-1),self.board))
                elif (row+1,col-1) == self.enpassant_possible:
                    moves.append(Move((row,col),(row+1,col-1),self.board,is_enpassant_move=True))
        pass

    def get_rook_moves(self,row,col,moves): # gets all rook moves for rook at row, col and appends to list
        
        # getting all moves moving north
        if row != 0: # making sure we arent at northmost rank
            for r in range(row-1,-1,-1): # going north one square at a time
            
                if self.board[r][col] == "__":  # square is unoccupied
                    moves.append(Move((row,col),(r,col),self.board))

                elif self.white_to_move and self.board[r][col][0] == "w": # white's turn and white piece in the way
                    break

                elif self.white_to_move and self.board[r][col][0] == "b": # white's turn and black piece in the way
                    moves.append(Move((row,col),(r,col),self.board))
                    break

                elif not self.white_to_move and self.board[r][col][0] == "w": # black's turn and white piece in the way
                    moves.append(Move((row,col),(r,col),self.board))
                    break

                elif not self.white_to_move and self.board[r][col][0] == "b": # black's turn and black piece in the way
                    break
        
        # getting all moves going south
        if row != 7: # checking that we arent that southmost rank
            for r in range(row+1,8,1):
                
                if self.board[r][col] == "__":  # square is unoccupied
                    moves.append(Move((row,col),(r,col),self.board))

                elif self.white_to_move and self.board[r][col][0] == "w": # white's turn and white piece in the way
                    break

                elif self.white_to_move and self.board[r][col][0] == "b": # white's turn and black piece in the way
                    moves.append(Move((row,col),(r,col),self.board))
                    break

                elif not self.white_to_move and self.board[r][col][0] == "w": # black's turn and white piece in the way
                    moves.append(Move((row,col),(r,col),self.board))
                    break

                elif not self.white_to_move and self.board[r][col][0] == "b": # black's turn and black piece in the way
                    break
        
        # getting all moves going east
        if col!= 7: # checking that we arent at eastmost file
            for c in range(col+1,8,1):

                if self.board[row][c] == "__":  # square is unoccupied
                    moves.append(Move((row,col),(row,c),self.board))

                elif self.white_to_move and self.board[row][c][0] == "w": # white's turn and white piece in the way
                    break

                elif self.white_to_move and self.board[row][c][0] == "b": # white's turn and black piece in the way
                    moves.append(Move((row,col),(row,c),self.board))
                    break

                elif not self.white_to_move and self.board[row][c][0] == "w": # black's turn and white piece in the way
                    moves.append(Move((row,col),(row,c),self.board))
                    break

                elif not self.white_to_move and self.board[row][c][0] == "b": # black's turn and black piece in the way
                    break
        
        # getting all moves going west
        if col!=0: # checking we arent at westmost file
            for c in range(col-1,-1,-1):

                if self.board[row][c] == "__":  # square is unoccupied
                    moves.append(Move((row,col),(row,c),self.board))

                elif self.white_to_move and self.board[row][c][0] == "w": # white's turn and white piece in the way
                    break

                elif self.white_to_move and self.board[row][c][0] == "b": # white's turn and black piece in the way
                    moves.append(Move((row,col),(row,c),self.board))
                    break

                elif not self.white_to_move and self.board[row][c][0] == "w": # black's turn and white piece in the way
                    moves.append(Move((row,col),(row,c),self.board))
                    break

                elif not self.white_to_move and self.board[row][c][0] == "b": # black's turn and black piece in the way
                    break
        
        pass

    def get_bishop_moves(self,row,col,moves): # gets all bishop moves for bishop at row, col and appends to list
        
        # getting moves going northeast
        r = row-1
        c = col+1
        while(r >= 0 and c <= 7):
            
            if self.board[r][c] == "__":  # square is unoccupied
                moves.append(Move((row,col),(r,c),self.board))

            elif self.white_to_move and self.board[r][c][0] == "w": # white's turn and white piece in the way
                break

            elif self.white_to_move and self.board[r][c][0] == "b": # white's turn and black piece in the way
                moves.append(Move((row,col),(r,c),self.board))
                break

            elif not self.white_to_move and self.board[r][c][0] == "w": # black's turn and white piece in the way
                moves.append(Move((row,col),(r,c),self.board))
                break

            elif not self.white_to_move and self.board[r][c][0] == "b": # black's turn and black piece in the way
                break
            
            r -= 1
            c += 1
        
        # getting moves going southeast
        r = row+1
        c = col+1
        while(r <= 7 and c <= 7):
            
            if self.board[r][c] == "__":  # square is unoccupied
                moves.append(Move((row,col),(r,c),self.board))

            elif self.white_to_move and self.board[r][c][0] == "w": # white's turn and white piece in the way
                break

            elif self.white_to_move and self.board[r][c][0] == "b": # white's turn and black piece in the way
                moves.append(Move((row,col),(r,c),self.board))
                break

            elif not self.white_to_move and self.board[r][c][0] == "w": # black's turn and white piece in the way
                moves.append(Move((row,col),(r,c),self.board))
                break

            elif not self.white_to_move and self.board[r][c][0] == "b": # black's turn and black piece in the way
                break
            
            r += 1
            c += 1
        
        # getting moves going southwest
        r = row+1
        c = col-1
        while(r <= 7 and c >= 0):
            
            if self.board[r][c] == "__":  # square is unoccupied
                moves.append(Move((row,col),(r,c),self.board))

            elif self.white_to_move and self.board[r][c][0] == "w": # white's turn and white piece in the way
                break

            elif self.white_to_move and self.board[r][c][0] == "b": # white's turn and black piece in the way
                moves.append(Move((row,col),(r,c),self.board))
                break

            elif not self.white_to_move and self.board[r][c][0] == "w": # black's turn and white piece in the way
                moves.append(Move((row,col),(r,c),self.board))
                break

            elif not self.white_to_move and self.board[r][c][0] == "b": # black's turn and black piece in the way
                break
            
            r += 1
            c -= 1
        
        # getting moves going northwest
        r = row-1
        c = col-1
        while(r >= 0 and c >= 0):
            
            if self.board[r][c] == "__":  # square is unoccupied
                moves.append(Move((row,col),(r,c),self.board))

            elif self.white_to_move and self.board[r][c][0] == "w": # white's turn and white piece in the way
                break

            elif self.white_to_move and self.board[r][c][0] == "b": # white's turn and black piece in the way
                moves.append(Move((row,col),(r,c),self.board))
                break

            elif not self.white_to_move and self.board[r][c][0] == "w": # black's turn and white piece in the way
                moves.append(Move((row,col),(r,c),self.board))
                break

            elif not self.white_to_move and self.board[r][c][0] == "b": # black's turn and black piece in the way
                break
            
            r -= 1
            c -= 1
        
        pass

    def get_knight_moves(self,row,col,moves): # gets all knight moves for knight at row, col and appends to list
        
        if self.white_to_move: # knight is white

            # moving 2 north and 1 east
            if row >= 2 and col <= 6 and self.board[row-2][col+1][0]!="w":
                moves.append(Move((row,col),(row-2,col+1),self.board))
        
            # moving 1 north and 2 east
            if row >= 1 and col <= 5 and self.board[row-1][col+2][0]!="w":
                moves.append(Move((row,col),(row-1,col+2),self.board))
        
            # moving 1 south and 2 east
            if row <= 6 and col <= 5 and self.board[row+1][col+2][0]!="w":
                moves.append(Move((row,col),(row+1,col+2),self.board))
            
            # moving 2 south and 1 east
            if row <= 5 and col <= 6 and self.board[row+2][col+1][0]!="w":
                moves.append(Move((row,col),(row+2,col+1),self.board))
            
            # moving 2 south and 1 west
            if row <= 5 and col >= 1 and self.board[row+2][col-1][0]!="w":
                moves.append(Move((row,col),(row+2,col-1),self.board))
            
            # moving 1 south and 2 west
            if row <= 6 and col >= 2 and self.board[row+1][col-2][0]!="w":
                moves.append(Move((row,col),(row+1,col-2),self.board))

            # moving 1 north and 2 west
            if row >= 1 and col >= 2 and self.board[row-1][col-2][0]!="w":
                moves.append(Move((row,col),(row-1,col-2),self.board))
            
            # moving 2 north and 1 west
            if row >= 2 and col >= 1 and self.board[row-2][col-1][0]!="w":
                moves.append(Move((row,col),(row-2,col-1),self.board))
        else: # knight is black

            # moving 2 north and 1 east
            if row >= 2 and col <= 6 and self.board[row-2][col+1][0]!="b":
                moves.append(Move((row,col),(row-2,col+1),self.board))
        
            # moving 1 north and 2 east
            if row >= 1 and col <= 5 and self.board[row-1][col+2][0]!="b":
                moves.append(Move((row,col),(row-1,col+2),self.board))
        
            # moving 1 south and 2 east
            if row <= 6 and col <= 5 and self.board[row+1][col+2][0]!="b":
                moves.append(Move((row,col),(row+1,col+2),self.board))
            
            # moving 2 south and 1 east
            if row <= 5 and col <= 6 and self.board[row+2][col+1][0]!="b":
                moves.append(Move((row,col),(row+2,col+1),self.board))
            
            # moving 2 south and 1 west
            if row <= 5 and col >= 1 and self.board[row+2][col-1][0]!="b":
                moves.append(Move((row,col),(row+2,col-1),self.board))
            
            # moving 1 south and 2 west
            if row <= 6 and col >= 2 and self.board[row+1][col-2][0]!="b":
                moves.append(Move((row,col),(row+1,col-2),self.board))

            # moving 1 north and 2 west
            if row >= 1 and col >= 2 and self.board[row-1][col-2][0]!="b":
                moves.append(Move((row,col),(row-1,col-2),self.board))
            
            # moving 2 north and 1 west
            if row >= 2 and col >= 1 and self.board[row-2][col-1][0]!="b":
                moves.append(Move((row,col),(row-2,col-1),self.board))
        
        pass

    def get_queen_moves(self,row,col,moves): # gets all queen moves for queen at row, col and appends to list
        
        self.get_rook_moves(row,col,moves)

        self.get_bishop_moves(row,col,moves)

        pass

    def get_king_moves(self,row,col,moves): # gets all king moves for king at row, col and appends to list
        
        if self.white_to_move: # white king moves
            
            # moving north
            if row != 0 and self.board[row-1][col][0]!="w":
                moves.append(Move((row,col),(row-1,col),self.board))

            # moving northeast
            if row != 0 and col != 7 and self.board[row-1][col+1][0]!="w":
                moves.append(Move((row,col),(row-1,col+1),self.board))

            # moving east
            if col != 7 and self.board[row][col+1][0]!="w":
                moves.append(Move((row,col),(row,col+1),self.board))

            # moving southeast
            if row != 7 and col != 7 and self.board[row+1][col+1][0]!="w":
                moves.append(Move((row,col),(row+1,col+1),self.board))

            # moving south
            if row != 7 and self.board[row+1][col][0]!="w":
                moves.append(Move((row,col),(row+1,col),self.board))

            # moving southwest
            if row != 7 and col != 0 and self.board[row+1][col-1][0]!="w":
                moves.append(Move((row,col),(row+1,col-1),self.board))

            # moving west
            if col != 0 and self.board[row][col-1][0]!="w":
                moves.append(Move((row,col),(row,col-1),self.board))

            # moving northwest
            if row != 0 and col != 0 and self.board[row-1][col-1][0]!="w":
                moves.append(Move((row,col),(row-1,col-1),self.board))    
            pass
        else: # black king moves
            
            # moving north
            if row != 0 and self.board[row-1][col][0]!="b":
                moves.append(Move((row,col),(row-1,col),self.board))

            # moving northeast
            if row != 0 and col != 7 and self.board[row-1][col+1][0]!="b":
                moves.append(Move((row,col),(row-1,col+1),self.board))

            # moving east
            if col != 7 and self.board[row][col+1][0]!="b":
                moves.append(Move((row,col),(row,col+1),self.board))

            # moving southeast
            if row != 7 and col != 7 and self.board[row+1][col+1][0]!="b":
                moves.append(Move((row,col),(row+1,col+1),self.board))

            # moving south
            if row != 7 and self.board[row+1][col][0]!="b":
                moves.append(Move((row,col),(row+1,col),self.board))

            # moving southwest
            if row != 7 and col != 0 and self.board[row+1][col-1][0]!="b":
                moves.append(Move((row,col),(row+1,col-1),self.board))

            # moving west
            if col != 0 and self.board[row][col-1][0]!="b":
                moves.append(Move((row,col),(row,col-1),self.board))

            # moving northwest
            if row != 0 and col != 0 and self.board[row-1][col-1][0]!="b":
                moves.append(Move((row,col),(row-1,col-1),self.board))    
            pass

        pass

    def get_castling_moves(self,row,col,moves): # gets all castling moves and appends to list
        
        # if king is under check, it cannot castle
        if self.square_under_attack(row,col):
            return

        if self.white_to_move:
        
            if self.current_castling_rights.white_king_side:
                self.get_king_side_castles(row,col,moves)

            if self.current_castling_rights.white_queen_side:
                self.get_queen_side_castles(row,col,moves)
        else:

            if self.current_castling_rights.black_king_side:
                self.get_king_side_castles(row,col,moves)

            if self.current_castling_rights.black_queen_side:
                self.get_queen_side_castles(row,col,moves)
        pass

    def get_king_side_castles(self,row,col,moves):
        
        if self.board[row][col+1] == "__" and self.board[row][col+2] == "__": # making sure the squares in bw king and rook are empty

            if not self.square_under_attack(row,col+1) and not self.square_under_attack(row,col+2): # making sure neither square in the middle is under attack

                moves.append(Move( (row,col), (row,col+2), self.board, is_castling_move = True))
        pass

    def get_queen_side_castles(self,row,col,moves):
        
        if self.board[row][col-1] == "__" and self.board[row][col-2] == "__" and self.board[row][col-3] == "__":
        
            if not self.square_under_attack(row,col-1) and not self.square_under_attack(row,col-2) and not self.square_under_attack(row,col-3):   
        
                moves.append(Move( (row,col), (row,col-2), self.board, is_castling_move = True))
        pass

class castling_rights():

    def __init__(self, wks, bks, wqs, bqs):
        self.white_king_side = wks
        self.black_king_side = bks
        self.white_queen_side = wqs
        self.black_queen_side = bqs
        pass

class Move():

    # mapping chess notation to its computer representation
    ranks_to_rows = {"1":7,"2":6,"3":5,"4":4,"5":3,"6":2,"7":1,"8":0}
    files_to_cols = {"a":0,"b":1,"c":2,"d":3,"e":4,"f":5,"g":6,"h":7}
    rows_to_ranks = {value:key for key, value in ranks_to_rows.items()}
    cols_to_files = {value:key for key, value in files_to_cols.items()}

    def __init__(self, start_sq, end_sq, board, is_enpassant_move = False, is_castling_move = False): # enpassant possible is an optional parameter and does not need to be always passed
        self.start_row = start_sq[0]
        self.start_col = start_sq[1]
        self.end_row = end_sq[0]
        self.end_col = end_sq[1]
        self.piece_moved = board[self.start_row][self.start_col]
        self.piece_captured = board[self.end_row][self.end_col]
        
        # generates a move id bw 0000 and 7777 which is unique for every possible move
        self.move_id =  self.start_row*1000 + self.start_col*100 + self.end_row*10 + self.end_col
        #print(self.move_id)

        # pawn promotion stuff
        self.is_pawn_promotion = False
        if (self.piece_moved == "wP" and self.end_row == 0) or (self.piece_moved == "bP" and self.end_row == 7):
            self.is_pawn_promotion = True

        # enpassant stuff
        self.is_enpassant_move = is_enpassant_move
        if self.is_enpassant_move:
            self.piece_captured = "wP" if self.piece_moved == "bP" else "bP"

        # castling stuff
        self.is_castling_move = is_castling_move

    def __eq__(self, value): # overriding the equals method(telling the comp how to compare two objects of class move)
        if isinstance(value,Move):
            return self.move_id == value.move_id

    def get_chess_notation(self): # TO DO : convert to actual chess notation
        return self.get_rank_file(self.start_row,self.start_col) + self.get_rank_file(self.end_row,self.end_col)

    def get_rank_file(self,row,col): # returns the position in format : rankfile (eg a6)
        return self.cols_to_files[col] + self.rows_to_ranks[row]