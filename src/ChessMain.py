'''This is gonna be the driver file, displying GameState, receiving user inputs, ...'''

import pygame as p
import ChessEngine
from typing import Tuple, Optional, Union, List, Callable, Literal

import sys
sys.path.append('/Users/simone/Library/Python/3.13/lib/python/site-packages')

WIDTH = 512
HEIGHT = 512 #if got some problem just use 400
MAX_FPS = 15
DIMENSION = 8
SQ_SIZE = HEIGHT // DIMENSION


GRAPHICS_PALETTE = [p.Color("white"), p.Color("gray")]
HIGHLIGHT_COLOR = p.Color("chocolate4")
LIGHT_HIGHLIGHT_COLOR = [p.Color("burlywood1"), p.Color("burlywood")]
CHECK_HIGHLIGHT_COLOR = p.Color("red")

PAWN_PROMOTION_HEIGHT = HEIGHT // 8
PAWN_PROMOTION_WIDTH = PAWN_PROMOTION_HEIGHT * 4
BOX_HEIGHT = 3*PAWN_PROMOTION_HEIGHT
BOX_WIDTH =  PAWN_PROMOTION_WIDTH + 2*PAWN_PROMOTION_HEIGHT

BOX_INIT_X =  (WIDTH - BOX_WIDTH) // 2
BOX_INIT_Y = ((WIDTH - BOX_HEIGHT - PAWN_PROMOTION_HEIGHT) // 2)
PAWN_PROMOTION_INIT_X = (WIDTH - PAWN_PROMOTION_WIDTH) // 2
PAWN_PROMOTION_INIT_Y = (HEIGHT - PAWN_PROMOTION_HEIGHT) // 2


'''ALL OF THE FOLLOWING CODE MUST BE INTENDED AS PSEUDOCODE, AND YET HAS TO BE ADAPTED TO OUR NEEDS'''
DEFAULT_SETTINGS = {}
class Game():

    def __init__(
            self,
            player1: int = 0,
            player2: int = 0,
            themes_settings: dict = DEFAULT_SETTINGS,
            IMAGES = {},
    ) -> None:
        
        # control flow and logic
        '''Player are flagged as player/AI by an integer spanning from 0 to xx (yet to be defined), where 0 identifies human player, while numbers 1 to xx identify AIs at different levels. It is still unknown whether these values describe the network model at different stages of training, or if different algorithms will be used to distinguish between different levels. Maybe, a mixture of the 2 approaches will be present, even though this is still unclear. The 0/int design option allows for an easier flow control with basic ifs.'''
        self.player1: int
        self.player2: int
        self.game: ChessEngine.GameState = ChessEngine.GameState()
        self.move_made: bool = True #has to be instantiated as true so we first draw the board
        self.valid_moves: List[ChessEngine.Move] = []
        

        # graphical elements
        self.WIDTH = WIDTH,
        self.HEIGHT = HEIGHT,
        self.MAX_FPS = MAX_FPS,
        
        self.IMAGES = {}; self.load_images()
        self.pawn_promotion_animation = False

        self.selected_square: Tuple[int, int] | Tuple[()] = ()
        self.player_clicks: List[Tuple[int, int]] = []
        pass
    ##

    def load_images(self) -> None:
        PATH = '/Users/simone/Desktop/projects/Chess Engine/images/'
        for piece in ['wP', 'wR', 'wN', 'wB', 'wQ', 'wK', 'bP', 'bR', 'bN', 'bB', 'bQ', 'bK']:
            self.IMAGES[piece] = p.image.load(PATH+piece+'.png')
    ##

    def play(self) -> None:
        pass
    ##

    '''We use this method to collect eventual events. We use this method to store changes, while self.update() to actually update the graphical features inside the surface. This is coherent to everything we have done up to date, also with the other GUI elements.'''
    def get_event(
            self,
            e: p.event.Event
    ) -> None:
        
        if e.type == p.QUIT:
            self.game.checkmate = True #TODO: edit this, rn just to avoid infinite looping
        ##
         
        if e.type == p.MOUSEBUTTONDOWN:
            location = p.mouse.get_pos() 
            col, row = location[0]//SQ_SIZE, location[1]//SQ_SIZE #TODO: ADD SELECTED ROW, SELECTED COL
            
            if self.selected_square == (row,col):
                self.selected_square = () #we deselect if the same click is given as an input twice
                self.player_clicks = []
            
            else:
                self.selected_square = (row, col)
                self.player_clicks.append(self.selected_square) #record the values
        ##

        if e.type == p.KEYDOWN and e.key == p.K_z:
            self.game.undo_move()
            self.move_made = True
            self.selected_square = ()
            self.player_clicks = []
        ##
    ##

    '''See self.get_event() for further details about what we have done'''
    def update(
            self,
            mouse_pos: Tuple[int, int]      # introduced just to add consistency with menu_manager type objects
    ) -> None:
        
        #if a move has been made, we handle the case in which next move must be made by AI, etc...
        if self.move_made:
            self.valid_moves = self.game.get_valid_moves()

            if 'AI_TO_MOVE':
                self.game.make_random_move(self.valid_moves)
            else:
                self.move_made = False
        
        ## if a move has been done, we need to monitor the output and do graphical handling
        else:
            if (len(self.player_clicks) == 1):
                if self.game.board[self.player_clicks[0][0], self.player_clicks[0][1]] == '--':
                    self.selected_square = ()
                    self.player_clicks = []
            
            #still a bad pawn promotion logic!!
            if len(self.player_clicks) == 2:
                    move = ChessEngine.Move(
                        self.player_clicks[0], 
                        self.player_clicks[1], 
                        self.game
                    )
                    
                    for engine_move in self.valid_moves:
                        if move == engine_move:
                            if engine_move.pawn_promotion[0]:
                                #engine_move.pawn_promotion = (True, handle_pawn_promotion(screen, self.game, engine_move)) # we first want to handle pawn promotion separately in order to interact correctly with the game
                                pass

                            self.game.make_move(engine_move)
                            print(engine_move)
                            self.move_made = True
                            self.selected_square = ()
                            self.player_clicks = []

                            break

                    else:
                        self.player_clicks = [self.selected_square] if self.selected_square else []
    ##

    def draw(
            self,
            surface: p.surface.Surface,
            **kwargs
    ) -> None:
        #TODO: when we are in pawn promotion animation we do not need to redraw everything 
        self.draw_board(surface)
        self.draw_pieces(surface)

        if self.pawn_promotion_animation:
            self.draw_pawn_promotion()
    ##

    def draw_pieces(
            self,
            surface: p.surface.Surface
    ) -> None:
        for r in range(DIMENSION):
            for c in range(DIMENSION):
                piece = self.game.board[r,c]
                if piece != '--': #if the cell is not empty
                    surface.blit(self.IMAGES[piece], p.Rect(c*SQ_SIZE, r*SQ_SIZE, SQ_SIZE, SQ_SIZE))
        pass
    ##

    def draw_board(
            self,
            surface: p.surface.Surface
    ) -> None:
        
        highlighted: Tuple[int, int] | None = self.selected_square if self.selected_square else None
        possible_reaching_squares = [(move.end_row, move.end_col) for move in self.valid_moves if (move.start_row, move.start_col)==highlighted]

        check_square = None
        if self.game.in_check:
            check_square = self.game.white_king_pos if self.game.white_to_move else self.game.black_king_pos

        for r in range(DIMENSION):
            for c in range(DIMENSION):
                color = GRAPHICS_PALETTE[((r+c)%2)]
                HIGHLIGHT_COLOR = LIGHT_HIGHLIGHT_COLOR[((r+c)%2)]                

                # highlighted square
                if (r,c) == highlighted: 
                    if self.game.board[r,c][0] == self.game.col(): #if selected square is one of the pieces to move
                        p.draw.rect(surface, HIGHLIGHT_COLOR, p.Rect(c*SQ_SIZE, r*SQ_SIZE, SQ_SIZE, SQ_SIZE))
                    else:
                        p.draw.rect(surface, color, p.Rect(c*SQ_SIZE, r*SQ_SIZE, SQ_SIZE, SQ_SIZE))

                # possible moves squares
                elif (r,c) in possible_reaching_squares:
                    p.draw.rect(surface, HIGHLIGHT_COLOR, p.Rect(c*SQ_SIZE, r*SQ_SIZE, SQ_SIZE, SQ_SIZE))

                elif (r,c) == check_square:
                    p.draw.rect(surface, CHECK_HIGHLIGHT_COLOR, p.Rect(c*SQ_SIZE, r*SQ_SIZE, SQ_SIZE, SQ_SIZE))

                # all the remainder
                else:
                    p.draw.rect(surface, color, p.Rect(c*SQ_SIZE, r*SQ_SIZE, SQ_SIZE, SQ_SIZE))
    ##

    def draw_pawn_promotion(self):
        pass
    ##
##



## MAIN RUNNING
if __name__ == "__main__":
    print('PROCESS INIT')
    #main()
    p.init()
    screen = p.display.set_mode((HEIGHT, WIDTH))
    game = Game(0,0)


    while not(game.game.checkmate or game.game.stalemate):

        for e in p.event.get():

            game.get_event(e)
            if e.type == p.QUIT:
                running = False

        mouse_pos = p.mouse.get_pos()
        game.update(mouse_pos)
        game.draw(screen, auto_display=False)
        p.display.flip()

#print("PROCESS ENDED CORRECTLY")