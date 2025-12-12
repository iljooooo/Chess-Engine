'''Here we store info and manage the status of game, determine valid mover, etc. This is basically the backend'''
import numpy as np
from typing import Union, Tuple, Dict, List, Callable, Optional, Any, Literal



class Move():
    
    #fixed dicts to use when translating moves in a more standard notation
    RANKS_TO_ROWS: Dict[str, int] = {f'{i}': 8-i for i in range(1,9)}
    ROWS_TO_RANKS: Dict[int, str] = {v: k for k,v in RANKS_TO_ROWS.items()}
    FILES_TO_COLS: Dict[str, int] = {'abcdefgh'[i]: i for i in range(8)}
    COLS_TO_FILES: Dict[int, str] = {v: k for k,v in FILES_TO_COLS.items()}

    def __init__(self, start_square: Tuple[int, int], end_square: Tuple[int, int], game, en_passant: Optional[bool] = False, short_castle: Optional[bool] = False, long_castle: Optional[bool] = False, pawn_promotion: Tuple[bool, Literal['--', 'wQ', 'wR', 'wN', 'wB', 'bQ', 'bR', 'bN', 'bB']] = (False, '--'), which_promotion: str = '') -> None:
        self.start_row = start_square[0]
        self.start_col = start_square[1]
        self.end_row = end_square[0]
        self.end_col = end_square[1]
        self.piece_moved = game.board[self.start_row, self.start_col]
        self.piece_captured = game.board[self.end_row, self.end_col]
        self.move_id = self.start_row * 1000 + self.start_col * 100 + self.end_row * 10 + self.end_col #ID creation like this basically means we only rely on moving from place A to place B, seems silly because we would likely like to record also which piece actually moves, but this is done by other pieces of code, and depend from time to time so there is no need to record such info.

        self.en_passant = en_passant
        self.short_castle = short_castle
        self.long_castle = long_castle
        self.pawn_promotion = pawn_promotion
        self.which_promotion = which_promotion
    ##

    def __repr__(self) -> str:
        return self.get_chess_notation()
    ##

    def get_chess_notation(self) -> str:
        if self.short_castle:
            return 'OO'
        
        if self.long_castle:
            return 'OOO'

        ep_string = 'ep' if self.en_passant else ''
        return self.get_rank_file(self.start_row, self.start_col) + self.get_rank_file(self.end_row, self.end_col) + ep_string
    ##

    def get_rank_file(self, r: int, c: int) -> str:
        return self.COLS_TO_FILES[c] + self.ROWS_TO_RANKS[r]
    ##

    '''Overriding the == operator for Moves, important to check whether two moves can be considered the same (we just check for equality in the hashed ID created)'''
    def __eq__(self, other):
        if isinstance(other, Move):
            return self.move_id == other.move_id
        else: 
            raise TypeError(f"Unable two compare {type(self)} and {type(other)}")
    ##
##




'''Wrapper to all of the functions calculating moves, needed in order to clean away any moves that do not respect the pins contrains. In order to do this we operate as follows: we store every move (initially) together with a direction. A piece is then to allowed to move if:
            - it is not pinned, and that is trivial to check
            - it's pinned, but moves along the direction it has been pinned on.
        
        By also storing the allowed directions in the first place, we then just need to operate a filtering operation which is then super easy to handle. It is important to observe that these two concat operation happen every time we call for such a method.

        Regarding the 'direction' storing, it may seem intuitive for some kind of pieces, specifically everything but the knights. In reality, inside the moves direction everything we handle this in a very general way that eases a lot the process of the filtering stage inside this wrapper
'''
def clean_pinned_moves(func: Callable) -> Callable[[Any, int, int], List[Move]]: #OBSERVE: Any is used just to avoid typing errors, it refers to a GameState object. Same below
    
    def wrapper(self: Any, *args: *Tuple[int, int]) -> List[Move]:

        moves: List[Move] = []
        r,c = args #we unwrap just to handle things better
        all_moves: List[Tuple[Move, Tuple[int, int]]] = func(self,r,c)

        #TODO: reformat self.pins as a dict to have an easier hashing time'''

        '''THIS IS THE ACTUAL DECORATION: takes all the moves and filters it based on directions information'''
        pins: Dict[Tuple[int, int], Tuple[int, int]] = {(pin[0], pin[1]) : (pin[2], pin[3]) for pin in self.pins}

        # Could be written as list comprehension but that format is less readable
        if ((r,c) in pins.keys()): #if the piece is pinned
            moves = [move for move, dir in all_moves if (pins[(move.start_row, move.start_col)] == dir) or pins[(move.start_row, move.start_col)] == (-dir[0], -dir[1])] #we filter
        else: 
            moves = [move for move, _ in all_moves]  #else nothing to filter, just a little refactoring
        return moves
    ##
    return wrapper
##




class GameState():
    def __init__(self):

        '''
        We save our board as a list-of-list: nested strings np.ndarray([], dtype=str) to store data. First order data are chessboard rows, so that we access those with self.board[i]. For pieces, first token represents the player, second one represent their class. Also, we use '--' to represent an empty space in the board
        '''

        self.board = np.array([
            np.array(["bR", "bN", "bB", "bQ", "bK", "bB", "bN", "bR"], dtype=str),
            np.array(['bP', 'bP', 'bP', 'bP', 'bP', 'bP', 'bP', 'bP'], dtype=str),
            np.array(['--', '--', '--', '--', '--', '--', '--', '--'], dtype=str),
            np.array(['--', '--', '--', '--', '--', '--', '--', '--'], dtype=str),
            np.array(['--', '--', '--', '--', '--', '--', '--', '--'], dtype=str),
            np.array(['--', '--', '--', '--', '--', '--', '--', '--'], dtype=str),
            np.array(['wP', 'wP', 'wP', 'wP', 'wP', 'wP', 'wP', 'wP'], dtype=str),
            np.array(['wR', 'wN', 'wB', 'wQ', 'wK', 'wB', 'wN', 'wR'], dtype=str)
        ])

        self.white_to_move: bool = True
        self.move_log: List[Move] = []
        self.white_king_pos: Tuple[int, int] = (7,4) #we store as Tuple[int, int] so that it is coherent within Moves construction
        self.black_king_pos: Tuple[int, int] = (0,4)
        self.checkmate = False
        self.stalemate = False
        self.in_check = False #store whether one of the player is in check
        self.pins = [] #store pinned pieces
        self.checks = [] #store check squares

        self.MOVES_FUNCTIONS: Dict[str, Callable] = {
            'P': self.get_pawn_moves,
            'R': self.get_rook_moves,
            'B': self.get_bishop_moves,
            'N': self.get_knight_moves,
            'Q': self.get_queen_moves,
            'K': self.get_king_moves,
        }

        self.en_passant: List[List[Tuple[int, int]]] = []         #this is used to store the (eventual) squares that are allowed to catch en Passant.

        self._WHITE_ROOKS_SPOTS = {(7,0): 'long', (7,7): 'short'}
        self._BLACK_ROOKS_SPOTS = {(0,0): 'long', (0,7): 'short'}
        self.white_long_castle = 0   #these will serve as flags for castling opportunities. They vanish whether the specific rook moves, or the king.
        self.white_short_castle = 0
        self.black_long_castle = 0
        self.black_short_castle = 0
    ##

    '''Copying the object by allocating new memory (these are separate objects)'''
    def __deepcopy__(self):
        g: GameState = GameState()
        for name, value in self.__dict__.items():
            g.__setattr__(name, value)
        return g
    ##

    def make_move(self, move: Move) -> None:
        '''We assume the move is always valid. Further on, we will generate a snippet that only generates valid moves. Also, this currently does not work for special cases like en-passant, castling, or pawn promotion'''
        self.board[move.start_row, move.start_col] = '--'
        self.board[move.end_row, move.end_col] = move.piece_moved
        
        self.move_log.append(move)

        #update king position(s) if needed
        if move.piece_moved == 'wK':
            self.white_king_pos = (move.end_row, move.end_col)
            self.white_long_castle += 1 #useful for castling
            self.white_short_castle += 1
        elif move.piece_moved == 'bK':
            self.black_king_pos = (move.end_row, move.end_col)
            self.black_long_castle += 1
            self.black_short_castle += 1

        ### EN PASSANT LOGIC ###
        #check if en-passant is possible next turn?
        (col, i) = ('w', 1) if self.white_to_move else ('b', -1)
        if move.piece_moved == (f'{col}P') and (abs(move.end_row-move.start_row) == 2): 
            self.en_passant = [[(move.end_row, move.end_col+j), (i,-j)] for j in [-1,1] if 0 <= move.end_col+j <= 7]
        else:
            self.en_passant = []

        if move.en_passant:
            self.board[move.start_row, move.end_col] = '--'
                        
        ### CASTLING LOGIC ###
        for i,j in [(move.start_row, move.start_col), (move.end_row, move.end_col)]:
            if (i,j) in self._WHITE_ROOKS_SPOTS.keys():
                param = f'white_{self._WHITE_ROOKS_SPOTS[(i,j)]}_castle'
                self.__setattr__(param, self.__getattribute__(param)+1) #TODO: understand this syntax
            elif (i,j) in self._BLACK_ROOKS_SPOTS.keys():
                param = f'black_{self._BLACK_ROOKS_SPOTS[(i,j)]}_castle'
                self.__setattr__(param, self.__getattribute__(param)+1)

        if move.long_castle:
            rook_row = 7 if self.white_to_move else 0
            self.board[rook_row, 0] = '--'
            self.board[rook_row, 3] = f'{col}R'
            #full_col = 'white' if self.white_to_move else 'black'
            #self.__setattr__(f'{full_col}_long_castle', self.__getattribute__(f'{full_col}_long_castle')+1) #maybe this is reduntant because castling is already considered a king move
        elif move.short_castle:
            rook_row = 7 if self.white_to_move else 0
            self.board[rook_row, 7] = '--'
            self.board[rook_row, 5] = f'{col}R'
            #full_col = 'white' if self.white_to_move else 'black'
            #self.__setattr__(f'{full_col}_long_castle', self.__getattribute__(f'{full_col}_short_castle')+1)

        ## PROMOTION LOGIC ##
        if move.pawn_promotion[0]:
            self.board[move.end_row, move.end_col] = move.pawn_promotion[1]

        #last operation to do is to pass the turn to the other player
        self.white_to_move = not self.white_to_move 
    ##

    def undo_move(self) -> None:
        '''We take the last move done and simply undo, or reverse that. We are not interested in making the method general since undoing a move only make sense if we previously have done that'''
        if len(self.move_log) > 0:  #ensure there actually is a move to undo
            move: Move = self.move_log.pop()
            self.board[move.start_row, move.start_col] = move.piece_moved
            self.board[move.end_row, move.end_col] = move.piece_captured

            if move.piece_moved == 'wK':
                self.white_king_pos = (move.start_row, move.start_col)
                self.white_long_castle -= 1 #useful for castling
                self.white_short_castle -= 1
            elif move.piece_moved == 'bK':
                self.black_king_pos = (move.start_row, move.start_col)
                self.black_long_castle -=1
                self.black_short_castle -=1

            ### EN PASSANT LOGIC ###
            (col, opp_col, i) = ('w', 'b', -1) if self.white_to_move else ('b', 'w', 1) 
            if move.en_passant:
                self.en_passant = [[(move.end_row+i, move.end_col+j), (-i,-j)] for j in [-1,1] if 0<=move.end_col+j<=7]
                self.board[move.start_row, move.end_col] = col+'P'

            try:
                prev_move = self.move_log[-1] #we check for prev move to understand if we have to restore some en-passant rights
                if prev_move.piece_moved == (opp_col+'P') and (abs(prev_move.end_row - prev_move.start_row) == 2): 
                    self.en_passant = [[(prev_move.end_row, prev_move.end_col+j), (i,-j)] for j in [-1,1] if 0 <= prev_move.end_col+j <= 7]
                else: self.en_passant = []
            
            except IndexError: #this handles the case in which we undo the very first move of the game
                pass


            ### CASTLING LOGIC ###
            for i,j in [(move.start_row, move.start_col), (move.end_row, move.end_col)]:
                if (i,j) in self._WHITE_ROOKS_SPOTS.keys():
                    param = f'white_{self._WHITE_ROOKS_SPOTS[(i,j)]}_castle'
                    self.__setattr__(param, self.__getattribute__(param)-1) #TODO: understand this syntax
                elif (i,j) in self._BLACK_ROOKS_SPOTS.keys():
                    param = f'black_{self._BLACK_ROOKS_SPOTS[(i,j)]}_castle'
                    self.__setattr__(param, self.__getattribute__(param)-1)

            if move.long_castle:
                rook_row = 0 if self.white_to_move else 7
                self.board[rook_row, 3] = '--'
                self.board[rook_row, 0] = f'{opp_col}R'
                #full_col = 'black' if self.white_to_move else 'white'
                #self.__setattr__(f'{full_col}_long_castle', self.__getattribute__(f'{full_col}_short_castle')-1)
            elif move.short_castle:
                rook_row = 0 if self.white_to_move else 7
                self.board[rook_row, 5] = '--'
                self.board[rook_row, 7] = f'{opp_col}R'
                #full_col = 'black' if self.white_to_move else 'white'
                #self.__setattr__(f'{full_col}_long_castle', self.__getattribute__(f'{full_col}_long_castle')-1)


            #return the move to the previous player
            self.white_to_move = not self.white_to_move


    '''LIST OF MOVE FILTERING METHODS. THESE ENABLE CONTROL OVER THE BOARD, LOOK FOR CHECKS, STALEMATE, CASTLING, ETC...
    THEY ARE ALL ICLUDED IN THIS CHUNK TO LET THE CODE ORDERED'''

    def check_for_pins_and_checks(self) -> Tuple[bool, List[Tuple[int, int, int, int]], List[List[Tuple[int,int]]]]: 
        in_check = False; pins = []; checks = []

        #check for initial king's and general PAWNS_CONDITIONS: initialization
        if self.white_to_move:
            opp_color = 'b'; ally_color = 'w'
            start_row = self.white_king_pos[0]
            start_col = self.white_king_pos[1]
        else:
            opp_color = 'w'; ally_color = 'b'
            start_row = self.black_king_pos[0]
            start_col = self.black_king_pos[1]

        #utilities needed in the loop afterward
        potential_pin = ()
        directions: List[Tuple[int, int]] = [(i,j) for i in [-1,0,1] for j in [-1,0,1]]
        directions.remove((0,0))
        
        #these consts are used to access check conditions in an easier way
        CONDITIONS: Dict[str, Callable] = {
            'R': lambda i,j,k,opp_color: (i,j) in [(-1,0), (0,-1), (1,0), (0,1)],
            'B': lambda i,j,k,opp_color: (i,j) in [(-1,-1), (-1,1), (1,-1), (1,1)],
            'Q': lambda i,j,k,opp_color: True,
            'K': lambda i,j,k,opp_color: k==1,
            'P': lambda i,j,k,opp_color: all([k==1, (i,j) in [(-1,-1), (-1,1)]]) if opp_color == 'b' else all([k==1, (i,j) in [(1,1), (1,-1)]]),
            'N': lambda i,j,k,opp_color: False
        }

        ### CHECKS/PINS OF ANY KIND EXCEPT FOR THE KNIGHT ONES ###
        for i,j in directions:

            potential_pin = () #cache
            current_dir_cells: List[Tuple[int, int]] = [] #cache

            for k in range(1,8): #we move along one of the possible directions, by max 8 places (I think this could be changed)
                end_row = start_row + k*i
                end_col = start_col + k*j

                if all([0<=end_row<=7, 0<=end_col<=7]): #ensure the square is valid
                    current_dir_cells.append((end_row, end_col))
                    end_piece = self.board[end_row, end_col]

                    if end_piece[0] == ally_color: #if we find an ally piece, we look behind it to check for eventual pins
                        if potential_pin == ():
                            potential_pin = (end_row, end_col, i,j)
                        else: #we found another ally piece along the direction, so we have no pin in that direction
                            break #hence the break of the for cycle
                    
                    elif end_piece[0] == opp_color: #if we find a piece of the opponent, we investigate

                        opp_piece_type = end_piece[1] #we store the piece type
                        if CONDITIONS[opp_piece_type](i,j,k,opp_color): #we look if the check can indeed attack our king
                            if potential_pin == (): #if it is the first piece along the direction, it is indeed a check
                                in_check = True
                                #checks.append((end_row, end_col, i, j)) 
                                checks.append(current_dir_cells)

                            else: #if we have a piece that blocked it, that is indeed pinned
                                pins.append(potential_pin)
                        
                        break #If we found an harmful piece, we added it as check/pin. Nonetheless, we do not need to investigate further along that specific diagonal, regardless of the fact that we found a check/pin, because the piece we found shadows the rest of the direction.


        ### KNIGHT CHECKS ###
        #IMPORTANT: KNIGHTS DO NOT CREATE ANY KIND OF PINS
        directions: List[Tuple[int,int]] = []
        for i in [-2,-1,1,2]:
            j = 3 - abs(i)
            directions.append((start_row+i, start_col-j))
            directions.append((start_row+i, start_col+j))

        KNIGHTS_CONDITIONS: Callable = lambda i,j: (self.board[i,j][0] == opp_color) and self.board[i,j][1] == 'N'
        for i,j in directions:
            if all([0<=i<=7, 0<=j<=7]) and KNIGHTS_CONDITIONS(i,j): #if the square is valid and is indeed occupied by a night
                in_check = True
                #checks.append((i,j, i-start_row, j-start_col))
                checks.append([(i,j)])


        #everything added, return
        return (in_check, pins, checks)
    ##

    ''' Get all possible moves considering checks.
    
        Some of the parts of this method need to be discussed. Observe how global handling of pins and checks conditions is done at the beginning in order to update global costraints. This is done because the moves calculation actually require to be cleaned, specifically we want to avoid certain pinning directions. We can handle this thanks to an appropriate decorator, but we need global conditions to be updated BEFORE we calculate for valid moves.

        TODO: handle the update of checkmate and stalemate update at the end of turn
    '''
    def get_valid_moves(self) -> List[Move]:
        self.in_check, self.pins, self.checks = self.check_for_pins_and_checks()
        moves: List[Move] = self.get_all_possible_moves()

        #TODO: Update Kings moves calculation when in check. Very rusty at the moment.

        if self.in_check: #we need to operate some filtering
            if len(self.checks) == 1:
                all_cells_check_direction: List[Tuple[int, int]] = self.checks[0]
                check_cell: Tuple[int, int] = all_cells_check_direction[-1]
                piece_checking: str = self.board[check_cell[0], check_cell[1]][1]

                valid_squares: List[Tuple[int, int]] = [] 

                if piece_checking == 'N':
                    valid_squares.append((check_cell[0], check_cell[1]))

                else: #literally every other piece, we need to cover the direction from which the check is coming
                    valid_squares += all_cells_check_direction

                '''TODO: revise this logic, currently we allow our king to move in spots that are indeed check but in another direction from the one that is holding the check when we detect it'''
                moves =  [move for move in moves if ((move.end_row, move.end_col) in valid_squares) ^ (move.piece_moved in ['wK', 'bK'])]
            ##

            if len(self.checks) >= 2: #here we navigate double (or even more complex) checks. Basically, if you are under double check you are forced to move your king
                king_row = self.white_king_pos[0] if self.white_to_move else self.black_king_pos[0]
                king_col = self.white_king_pos[1] if self.white_to_move else self.black_king_pos[1]
                moves = self.get_king_moves(king_row, king_col) #if we are given double checks, we are forced to move our king
            ##
        

        ## STALEMATE AND CHECKMATE UPDATE ##
        if len(moves)==0:
            if self.in_check:
                self.checkmate = True
            else:
                self.stalemate = True
        else:
            self.checkmate = False
            self.stalemate = False

        return moves
    ##

    '''Get all possible moves without considering checks. This method returns all of the valid moves based solely on our pieces positions. It does account for pins, thanks to the wrapping to all of the singular methods, but not for checks. These are handled in the get_valid_moves method'''
    def get_all_possible_moves(self) -> List[Move]:
        moves = []

        #go through the board to check for pieces
        for r, row in enumerate(self.board):
            for c, cell in enumerate(row):
                turn = cell[0] #this basically is either 'w', 'b', or '-'
                if (turn=='w' and self.white_to_move) or (turn=='b' and not self.white_to_move): #this basically checks for valid pieces
                    piece = cell[1] #we get what kind of piece we are tracking
                    moves += self.MOVES_FUNCTIONS[piece](r,c)
 
        return moves
    ##


    '''LIST OF MOVE FINDER METHODS. HERE WE PROVIDE A LIST, PIECE BY PIECE, OF ALL THE POSSIBLE DIFFERENT MOVES. All of the methods below use a wrapper defined at the top of the class to filter moves from the pinned pieces from the list of the available moves. So in this method we actually return a list of object of the kind:
            
            (Move, dir)
            
        Where dir = Tuple[int, int] stores informations about the move directions in order for the wrapper to operate more smoothly. This really allows for the wrapper to operate with trivial logic. For further info, see clean_pinned_moves informations together with its docstring.
    '''

    '''We get all the possible pawn moves from pawn located at square [r,c]'''
    @clean_pinned_moves
    def get_pawn_moves(self, r:int, c:int) -> List[Tuple[Move, Tuple[int, int]]]:
        moves: List[Tuple[Move, Tuple[int, int]]] = []

        dir: Tuple[int, int]= (-1,0) if self.white_to_move else (1,0)
        i, j = dir[0], dir[1]
        pawns_starting_row: int = 6 if self.white_to_move else 1
        opp_color: str = 'b' if self.white_to_move else 'w'

        if self.board[r+i,c] == '--':
            promotion = (True, '--') if r+i in [0,7] else (False, '--')
            moves.append((Move((r,c), (r+i,c), self, pawn_promotion=promotion), dir))

            if (r == pawns_starting_row) and (self.board[r+(2*i), c] == '--'):
                moves.append((Move((r,c), (r+(2*i), c), self), dir)) #double pushes can never result in promotion
            
        diags = [(i,1), (i,-1)]
        for diag_i, diag_j in diags:
            if all([0<=r+diag_i<=7, 0<=c+diag_j<=7]):
                promotion = (True, '--') if r+diag_i in [0,7] else (False, '--')
                if (self.board[r+diag_i, c+diag_j][0] == opp_color): 
                    moves.append((Move((r,c), (r+diag_i, c+diag_j), self, pawn_promotion=promotion), (diag_i, diag_j)))

                if [(r,c), (diag_i, diag_j)] in self.en_passant: #if en-passant is allowed, we add
                    moves.append((Move((r,c), (r+diag_i, c+diag_j), self, en_passant=True), (diag_i, diag_j))) #en passant can never result in a promotion
                    pass

        #TODO: add en-passant and pawn promotion (probably pawn promotion needs to be added in the move module, at the end of the turn?)
        return moves
    ##

    @clean_pinned_moves
    def get_rook_moves(self, start_row:int, start_col:int) -> List[Tuple[Move, Tuple[int, int]]]:
        moves: List[Tuple[Move, Tuple[int, int]]]= []
        ROOK_DIRECTIONS = [(i,j) for i in (-1,0,1) for j in (-1,0,1) if abs(i+j) == 1]

        for (i,j) in ROOK_DIRECTIONS:
            for k in range(1,8):
                end_row = start_row + k*i
                end_col = start_col + k*j
                opp_color = 'b' if self.white_to_move else 'w'

                if all([0<=end_row<=7, 0<=end_col<=7]):
                    if self.board[end_row, end_col][0] == opp_color: #if we find an opponent, we add the move but can't move further, hence the break
                        moves.append((Move((start_row, start_col), (end_row, end_col), self), (i,j)))
                        break

                    elif self.board[end_row,end_col][0] == '-': #if we find an empty space, we add the move and keep goind
                        moves.append((Move((start_row, start_col), (end_row, end_col), self), (i,j)))

                    else: #if we find an ally, nothing we can do!
                        break
                else: #if we are here we are out of the board, so we can directly pass at next iter
                    break
        
        return moves
    ##

    '''We get all the possible bishop moves from bishop located at square [r,c]'''
    @clean_pinned_moves
    def get_bishop_moves(self, start_row:int, start_col: int) -> List[Tuple[Move, Tuple[int, int]]]:
        moves: List[Tuple[Move, Tuple[int, int]]] = []
        BISHOP_DIRECTIONS = [(i,j) for i in (-1,0,1) for j in (-1,0,1) if abs(i)+ abs(j) == 2] #check for this logic

        for (i,j) in BISHOP_DIRECTIONS:
            for k in range(1,8):
                end_row = start_row + k*i
                end_col = start_col + k*j
                opp_color = 'b' if self.white_to_move else 'w'

                if all([0<=end_row<=7, 0<=end_col<=7]):
                    if self.board[end_row, end_col][0] == opp_color:
                        moves.append((Move((start_row, start_col), (end_row, end_col), self), (i,j)))
                        break

                    elif self.board[end_row,end_col][0] == '-':
                        moves.append((Move((start_row, start_col), (end_row, end_col), self), (i,j)))

                    else:
                        break
                else:
                    break
        return moves
    ##

    '''We get all the possible knight moves from knight located at square [r,c]'''
    @clean_pinned_moves
    def get_knight_moves(self,r:int ,c:int) -> List[Tuple[Move, Tuple[int, int]]]:
        moves: List[Tuple[Move, Tuple[int, int]]] = []

        directions: List[Tuple[int,int]] = []
        for i in [-2,-1,1,2]:
            j = 3 - abs(i)
            directions.append((r+i, c-j))
            directions.append((r+i, c+j))
        
        for i,j in directions:
            if all([0<=i<=7, 0<=j<=7]): #if the square is on the board
                if self.board[i,j] == '--': #if the square is free
                    moves.append((Move((r,c), (i,j),self), (i,j))) #add the move

                elif (self.white_to_move) and (self.board[i,j][0] == 'b'): #if the square is occupied but there's a black piece and white moves
                    moves.append((Move((r,c), (i,j), self), (i,j)))

                elif (not self.white_to_move) and (self.board[i,j][0] == 'w'): #same flipped
                    moves.append((Move((r,c), (i,j), self), (i,j)))
        return moves
    ##

    '''We get all the possible queen moves from queen located at square [r,c]. IMPORTANT: queen moves do not need the wrapping since they use results from bishop and rook (already cleaned up by the wrapper itself when called)'''
    def get_queen_moves(self,r:int ,c:int) -> List[Move]:
        # Queen moves as rook + bishop so we can recycle already written gode
        return self.get_rook_moves(r,c) + self.get_bishop_moves(r,c)
    ##

    '''We get all the possible king moves from king located at square [r,c]'''
    @clean_pinned_moves
    def get_king_moves(self, start_row:int, start_col:int) -> List[Tuple[Move, Tuple[int, int]]]:
        moves: List[Tuple[Move, Tuple[int, int]]] = []
        directions: List[Tuple[int, int]] = [(i,j) for i in [-1,0,1] for j in [-1,0,1] if (i,j)!=(0,0)]

        for i,j in directions:
            if all([0<=start_row+i<=7, 0<=start_col+j<=7]):
                if self.board[start_row+i, start_col+j] == '--':
                    moves.append((Move((start_row, start_col), (start_row+i, start_col+j), self), (i,j)))

                elif (self.white_to_move) and (self.board[start_row+i,start_col+j][0] == 'b'):
                    moves.append((Move((start_row, start_col), (start_row+i, start_col+j), self), (i,j)))

                elif (not self.white_to_move) and (self.board[start_row+i,start_col+j][0] == 'w'):
                    moves.append((Move((start_row, start_col), (start_row+i, start_col+j), self), (i,j)))

            
            #ADD CASTLING MOVES
            if (self.white_to_move) and (not self.in_check):
                if not self.white_short_castle: #if we are still able to castle-short
                    if all([self.board[7,5] == '--', self.board[7,6] == '--']):
                        moves.append((Move(self.white_king_pos, (7,6), self, short_castle=True), (0,1)))
                if not self.white_long_castle: #if we are still able to castle-long
                    if all([self.board[7,1] == '--', self.board[7,2] == '--', self.board[7,3] == '--']):
                        moves.append((Move(self.white_king_pos, (7,2), self, long_castle=True), (0,-1)))
            
            if (not self.white_to_move) and (not self.in_check):
                if not self.black_short_castle: #if we are still able to castle-short
                    if all([self.board[0,5] == '--', self.board[0,6] == '--']):
                        moves.append((Move(self.black_king_pos, (0,6), self, short_castle=True), (0,1)))
                if not self.black_long_castle: #if we are still able to castle-long
                    if all([self.board[7,1] == '--', self.board[7,2] == '--', self.board[7,3] == '--']):
                        moves.append((Move(self.black_king_pos, (0,2), self, long_castle=True), (0,-1)))


        return moves
    ##

    def get_castling_moves(self):
        pass
    ##
##



'''Calculate how many possible moves combination are possible within the next `turns`. Serves as a check to understand whether our engine calculates the moves in the right manner, we can use lists available online to verify our results.

    TODO: Understand recursion logic because right now we are not able to handle things in a good manner for our memory.
'''
def calc_moves_number(turns: int, gs: Optional[GameState] = None, tot: int = 0) -> int:
    if gs is None:
        gs = GameState()
    
    moves = gs.get_valid_moves()
    if turns == 1: 
        return len(moves)
    return sum([calc_moves_number(turns-1, gs.__deepcopy__().make_move(move)) for move in moves])
##

if __name__ == '__main__':
    #print(calc_moves_number(5))
    #gs = GameState()
    #print(gs.__dict__)
    pass