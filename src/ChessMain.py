'''This is gonna be the driver file, displying GameState, receiving user inputs, ...'''

import pygame as p
import ChessEngine
from typing import Tuple, Optional, Union, List, Callable, Literal

import sys
sys.path.append('/Users/simone/Library/Python/3.13/lib/python/site-packages')

import pygamepopup # pyright: ignore[reportMissingImports]
from pygamepopup.menu_manager import MenuManager  # pyright: ignore[reportMissingImports]
from pygamepopup.components import Button, InfoBox # pyright: ignore[reportMissingImports]


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
    pygamepopup.init()
    screen = p.display.set_mode((WIDTH, HEIGHT))
    clock = p.time.Clock()
    screen.fill(p.Color("white"))
    pawn_promotion_scene = None

    game = ChessEngine.GameState() #we initialize game as our primary object
    valid_moves: List[ChessEngine.Move] = game.get_valid_moves() #these are moves possible at the very beginning
    move_made: bool = False #This little exit_flag logic is used to avoid generating moves after every loop, saving time
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
            if pawn_promotion_scene:
                pass

            elif e.type == p.MOUSEBUTTONDOWN:
                location = p.mouse.get_pos() 
                col, row = location[0]//SQ_SIZE, location[1]//SQ_SIZE 
                
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
                            if engine_move.pawn_promotion[0]:
                                engine_move.pawn_promotion = (True, handle_pawn_promotion(screen, game, engine_move)) # we first want to handle pawn promotion separately in order to interact correctly with the game

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


def promotion(func: Callable):
    def wrapper() -> Optional[Callable]:
        pass
    return wrapper
##


'''Method that is needeed to print to screen the choices in order to let the player decide what to promote the pawn to'''
class PawnPromotionScreen():

    def __init__(self, screen: p.Surface, gs: ChessEngine.GameState, move: ChessEngine.Move) -> None:
        self.screen = screen
        self.menu_manager = MenuManager(screen)
        self.exit_request = False

        self.create_main_menu_interface()
    ##

    def create_main_menu_interface(self):
        main_menu = InfoBox(
            "Test Menu", 
            [
                [Button(title="Q",callback=lambda: self.promote_to_queen())],
                [Button(title="N", callback=lambda: self.promote_to_rook())],
                [Button(title='B', callback= lambda: self.promote_to_bishop())],
                [Button(title='R')]
            ],

            has_close_button=False,
        )
        self.menu_manager.open_menu(main_menu)
    ##

    def promote_to_queen(self):
        pass
    ##

    def promote_to_rook(self):
        pass
    ##

    def promote_to_bishop(self):
        pass
    ##

    def display(self) -> None:
        self.menu_manager.display()
        p.display.update()
    ##

    def click(self, button: int, position: p.Vector2) -> bool:
        self.menu_manager.click(button, position)
        return self.exit_request
##

PAWN_PROMOTION_HEIGHT = HEIGHT // 8
PAWN_PROMOTION_WIDTH = PAWN_PROMOTION_HEIGHT * 4
BOX_HEIGHT = 3*PAWN_PROMOTION_HEIGHT
BOX_WIDTH =  PAWN_PROMOTION_WIDTH + 2*PAWN_PROMOTION_HEIGHT

BOX_INIT_X =  (WIDTH - BOX_WIDTH) // 2
BOX_INIT_Y = ((WIDTH - BOX_HEIGHT - PAWN_PROMOTION_HEIGHT) // 2)
PAWN_PROMOTION_INIT_X = (WIDTH - PAWN_PROMOTION_WIDTH) // 2
PAWN_PROMOTION_INIT_Y = (HEIGHT - PAWN_PROMOTION_HEIGHT) // 2


def handle_pawn_promotion(screen: p.Surface, game: ChessEngine.GameState, move: ChessEngine.Move) -> Literal['--', 'wQ', 'wR', 'wN', 'wB', 'bQ', 'bR', 'bN', 'bB']:
    
    pieces = ['Q', 'R', 'B', 'N']
    col: Literal['w', 'b'] = move.piece_moved[0]
    promotion_figures: List[Literal['--', 'wQ', 'wR', 'wN', 'wB', 'bQ', 'bR', 'bN', 'bB']] = [col + i for i in pieces]  # pyright: ignore[reportAssignmentType]

    # drawing the panel
    #screen.fill('white')
    p.draw.rect(screen, 'black', p.Rect(BOX_INIT_X, BOX_INIT_Y, BOX_WIDTH, BOX_HEIGHT))

    for i, piece in enumerate(promotion_figures):
         p.draw.rect(screen, GRAPHICS_PALETTE[i%2], p.Rect(PAWN_PROMOTION_INIT_X + i*PAWN_PROMOTION_HEIGHT, PAWN_PROMOTION_INIT_Y, PAWN_PROMOTION_HEIGHT, PAWN_PROMOTION_HEIGHT))

         screen.blit(IMAGES[piece], p.Rect(PAWN_PROMOTION_INIT_X + i*PAWN_PROMOTION_HEIGHT, PAWN_PROMOTION_INIT_Y, PAWN_PROMOTION_HEIGHT, PAWN_PROMOTION_HEIGHT))

    p.display.update()

    # handling the exit event
    exit_request: bool = False
    while not exit_request:
        for e in p.event.get():
            if e.type == p.MOUSEBUTTONDOWN:
                loc = p.mouse.get_pos()
                x, y = loc[0], loc[1]

                x = loc[0] - PAWN_PROMOTION_INIT_X
                y = loc[1] - PAWN_PROMOTION_INIT_Y

                if(all([0<=x<=PAWN_PROMOTION_WIDTH, 0<=y<=PAWN_PROMOTION_HEIGHT])):
                    x:int = x//PAWN_PROMOTION_HEIGHT
                    return promotion_figures[x]
                    exit_request = not exit_request
##


## MAIN RUNNING
if __name__ == "__main__":
    print('PROCESS INIT')
    main()
#print("PROCESS ENDED CORRECTLY")

