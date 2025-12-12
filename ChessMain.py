'''This is gonna be the driver file, displying GameState, receiving user inputs, ...'''

import pygame as p
import ChessEngine
from typing import Tuple, Optional, Union, List

#fixing pixels related parameters
p.init() #just to be sure it gets initialized, probably redundant
WIDTH = HEIGHT = 512 #if got some problem just use 400
DIMENSION = 8 
SQ_SIZE = HEIGHT // DIMENSION
MAX_FPS = 15 #used for animations
IMAGES = {}

'''
Initialize a global dictionaries of images. We do this exactly one time because loading images with pygame is a kinda expensive feature, so we only want to do this once.
'''
def load_images():
    #TODO: adjust (SQ_SIZE, SQ_SIZE) with slightly refactored quantities
    for piece in ['wP', 'wR', 'wK', 'wQ', 'wN', 'wB', 'bP', 'bR', 'bN', 'bB', 'bK', 'bQ']:
        IMAGES[piece] = p.transform.scale(p.image.load(f'images/{piece}.png'), (SQ_SIZE, SQ_SIZE))
##


def main():
    p.init()
    screen = p.display.set_mode((WIDTH, HEIGHT))
    clock = p.time.Clock()
    screen.fill(p.Color("white"))

    game = ChessEngine.GameState() #we initialize game as our primary object
    valid_moves: List[ChessEngine.Move] = game.get_valid_moves() #these are moves possible at the very beginning
    move_made: bool = False #This little flag logic is used to avoid generating moves after every loop, saving time
    #print(game.board)

    load_images() #actually load the images 
    draw_game_state(screen, game) #draw initial board config
    
    #this loops basically keeps the game running, it handles events happening or whatever
    running = True
    sq_selected: Union[Tuple[int, int], Tuple[()]] = () #keeps track of the last click of the user
    player_clicks: List[Tuple] = [] #keeps track of couples of players input. Basically is needed to update pieces inside of the board

    while(running):
        for e in p.event.get():
            if e.type == p.QUIT:
                running = False

            ## MOUSE HANDLER
            elif e.type == p.MOUSEBUTTONDOWN:
                location = p.mouse.get_pos() #this returns (x,y) location of the mouse as a Tuple(int,int)
                col, row = location[0]//SQ_SIZE, location[1]//SQ_SIZE #and this translates it in row/col notation for the engine
                
                if sq_selected == (row,col):
                    sq_selected = () #we deselect if the same click is given as an input twice
                    player_clicks = []
                
                else:
                    sq_selected = (row, col)
                    player_clicks.append(sq_selected) #record the values

                if (len(player_clicks) == 1):
                    if game.board[row, col] == '--':
                        sq_selected = ()
                        player_clicks = []

                #update with the move if necessary, we move after the second input
                if len(player_clicks) == 2:
                    move = ChessEngine.Move(player_clicks[0], player_clicks[1], game)
                    
                    for engine_move in valid_moves:
                        if move == engine_move:
                            game.make_move(engine_move)
                            print(engine_move)
                            move_made = True
                            sq_selected = ()
                            player_clicks = []
                            break

                    else:
                        player_clicks = [sq_selected]

            ## KEYBOARD EVENTS HANDLER
            if e.type == p.KEYDOWN:
                if e.key == p.K_z:
                    game.undo_move()
                    move_made = True
                    sq_selected = ()
                    player_clicks = []

        if move_made:
            valid_moves = game.get_valid_moves()
            move_made = False
        
        draw_game_state(screen, game, highlighted=(sq_selected), moves=valid_moves)
        clock.tick(MAX_FPS)
        p.display.flip()
##

##############################
### GRAPHICS FEATURES CODE ###
##############################

#TODO: add a menu and some possibility to add some settings
#TODO: check animation (red highlighted king pos)

GRAPHICS_PALETTE = [p.Color("white"), p.Color("gray")]
HIGHLIGHT_COLOR = p.Color("chocolate4")
LIGHT_HIGHLIGHT_COLOR = [p.Color("burlywood1"), p.Color("burlywood")]
CHECK_HIGHLIGHT_COLOR = p.Color("red")


def draw_game_state(screen: p.Surface, gs: ChessEngine.GameState, highlighted: Optional[Union[Tuple[int, int], Tuple[()]]] = None, moves=None) -> None:
    '''
    Method that simply draws things down in a dynamical manner. Relies on the two helpers method cited below. It returns nothing, it just edits current status of the display provided as parameter.
    '''
    draw_board(screen, gs, highlighted, moves) #we first draw the skeleton
    draw_pieces(screen, gs) #and we place the pieces on top of it
    pass
##

def draw_board(screen: p.Surface, game: ChessEngine.GameState, highlighted: Optional[Union[Tuple[int, int], Tuple[()]]], moves: Optional[List[ChessEngine.Move]] = None) -> None:
    '''Handles the drawing board squares (basically the skeleton)'''

    possible_reaching_squares = [(move.end_row, move.end_col) for move in moves if (move.start_row, move.start_col)==highlighted] if moves is not None else []

    check_square: Tuple[int, int] = (-1,-1)
    if game.in_check:
        check_square = game.white_king_pos if game.white_to_move else game.black_king_pos

    for r in range(DIMENSION):
        for c in range(DIMENSION):
            color = GRAPHICS_PALETTE[((r+c)%2)]
            HIGHLIGHT_COLOR = LIGHT_HIGHLIGHT_COLOR[((r+c)%2)]                

            # highlighted square
            if (r,c) == highlighted: 
                col_to_move = 'w' if game.white_to_move else 'b'
                if game.board[r,c][0] == col_to_move: #if selected square is one of the pieces to move
                    p.draw.rect(screen, HIGHLIGHT_COLOR, p.Rect(c*SQ_SIZE, r*SQ_SIZE, SQ_SIZE, SQ_SIZE))
                else:
                    p.draw.rect(screen, color, p.Rect(c*SQ_SIZE, r*SQ_SIZE, SQ_SIZE, SQ_SIZE))

            # possible moves squares
            elif (r,c) in possible_reaching_squares:
                p.draw.rect(screen, HIGHLIGHT_COLOR, p.Rect(c*SQ_SIZE, r*SQ_SIZE, SQ_SIZE, SQ_SIZE))

            elif (r,c) == check_square:
                p.draw.rect(screen, CHECK_HIGHLIGHT_COLOR, p.Rect(c*SQ_SIZE, r*SQ_SIZE, SQ_SIZE, SQ_SIZE))

            # all the remainder
            else:
                p.draw.rect(screen, color, p.Rect(c*SQ_SIZE, r*SQ_SIZE, SQ_SIZE, SQ_SIZE))
    pass
##

def draw_pieces(screen: p.Surface, gs: ChessEngine.GameState) -> None:
    '''
    Draw the pieces on the board based on current GameState.board object passed as parameter.
    '''
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            piece = gs.board[r,c]
            if piece != '--': #if the cell is not empty
                screen.blit(IMAGES[piece], p.Rect(c*SQ_SIZE, r*SQ_SIZE, SQ_SIZE, SQ_SIZE))
    pass
##


## MAIN RUNNING
if __name__ == "__main__":
    print('PROCESS INIT')
    main()
#print("PROCESS ENDED CORRECTLY")