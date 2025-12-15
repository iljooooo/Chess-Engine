import pygame as p
import buttons

from typing import List, Tuple, Iterable, Callable

class Menu(p.sprite.Group):

    def __init__(self, *bts: Iterable[buttons.Button]) -> None:
        super().__init__(*bts)
    ##

    '''def add(self, *widgets: List[buttons.Button] | Tuple[buttons.ButtonGroup]) -> None:
        self.add(*widgets)
    ##'''

    def update(self, mouse_pos: Tuple[int, int]) -> None:
        for w in self.sprites():
            w.update(mouse_pos)
    ##

    def handle_event(self, e: p.event.Event) -> None:
        for w in self.sprites():
            w.get_event(e)
    ##

    def draw(self, surface: p.Surface, mouse_pos: Tuple[int, int], auto_display = True) -> None:

        if not auto_display:
            for w in self.widgets:
                w.draw(surface)

        else:
            surface_width, surface_height = surface.get_size()
            


    ##
##


class MenuManager():

    def __init__(self, start_menu: Menu) -> None:
        self.current = start_menu
    ##

    def set(self, menu: Menu) -> None:
        self.current = menu
    ##
##

#############
## TESTING ##
#############

if __name__ == "__main__":
    p.init()

    WIDTH = HEIGHT = 512
    BUTTONS_Y_SPACING = 100


    screen = p.display.set_mode((WIDTH, HEIGHT))
    clock = p.time.Clock()
    screen.fill("white")

    COMMON_ATTRIBUTES = {
        "button_size": (100,20),
        "fill_color": p.Color("white"),
        "hover_fill_color": p.Color("black"),
        "font": p.font.match_font('arial', bold=True),
        "font_size": 13,
        "text_color": 'black',
        "hover_text_color": 'white',
    }

    play_btn = buttons.Button(
        rect_attr = {"center": (WIDTH//2, HEIGHT//2 - BUTTONS_Y_SPACING)},
        text= 'PLAY',
        hover_text = "PLAY",
        **COMMON_ATTRIBUTES
    )
    play_btn.call = lambda: print(play_btn.get_size()) # bound method

    settings_btn = buttons.Button(
        rect_attr={"center": (WIDTH//2, HEIGHT//2)},
        text = "SETTINGS",
        hover_text = "SETTINGS",
        call = lambda: 0,
        **COMMON_ATTRIBUTES
    )

    credits_btn = buttons.Button(
        rect_attr={"center": (WIDTH//2, HEIGHT//2 + BUTTONS_Y_SPACING)},
        text= "CREDITS",
        hover_text= "CREDITS",
        call = lambda: 0,
        **COMMON_ATTRIBUTES
    )

    bts = buttons.ButtonGroup((
        play_btn,
        settings_btn,
        credits_btn
    )) 

    menu = Menu(bts)
    
    running = True
    while running:
        for e in p.event.get():

            bts.get_event(e)
            if e.type == p.QUIT:
                running = False
        
        mouse_pos = p.mouse.get_pos()
        bts.draw(screen, mouse_pos)
        menu.draw(screen, mouse_pos, auto_display=True)
        p.display.flip()