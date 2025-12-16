import sys
from typing import Iterable
import pygame as p
from utils_interfaces.buttons import Button
from utils_interfaces.menu import Menu, MenuManager
p.init()


WIDTH = HEIGHT = 512
BUTTONS_Y_SPACING = 100

open_menu = Menu()
settings_menu = Menu()
credits_menu = Menu()
menu_manager = MenuManager(start_menu=open_menu)

COMMON_ATTRIBUTES = {
        "button_size": (100,20),
        "fill_color": p.Color("white"),
        "hover_fill_color": p.Color("black"),
        "font": p.font.match_font('arial', bold=True),
        "font_size": 13,
        "text_color": 'black',
        "hover_text_color": 'white',
}

open_menu.add(
    [
        Button(
            rect_attr = {"center": (WIDTH//2, HEIGHT//2 - BUTTONS_Y_SPACING)},
            text= 'PLAY',
            hover_text = "PLAY",
            call = lambda: print(0),
            **COMMON_ATTRIBUTES
        ),

        Button(
            rect_attr={"center": (WIDTH//2, HEIGHT//2)},
            text = "SETTINGS",
            hover_text = "SETTINGS",
            call = lambda: menu_manager.set(settings_menu),
            **COMMON_ATTRIBUTES
        ),

        Button(
            rect_attr={"center": (WIDTH//2, HEIGHT//2 + BUTTONS_Y_SPACING)},
            text= "CREDITS",
            hover_text= "CREDITS",
            call = lambda: menu_manager.set(credits_menu),
            **COMMON_ATTRIBUTES
        )
    ]
)

settings_menu.add(
    [
        Button(
            rect_attr = {"center": (WIDTH//2, HEIGHT//2 - BUTTONS_Y_SPACING)},
            text= 'BACK',
            hover_text = "BACK",
            call = lambda: menu_manager.set(open_menu),
            **COMMON_ATTRIBUTES
        )
    ]
)

credits_menu.add(
    [
        Button(
            rect_attr = {"center": (WIDTH//2, HEIGHT//2 - BUTTONS_Y_SPACING)},
            text= 'BACK',
            hover_text = "BACK",
            call = lambda: menu_manager.set(open_menu),
            **COMMON_ATTRIBUTES
        )
    ]
)


#############
## TESTING ##
#############

if __name__ == '__main__':
    p.init()
    screen = p.display.set_mode((WIDTH, HEIGHT))
    clock = p.time.Clock()
    screen.fill("white")

    running = True
    while running:
        for e in p.event.get():

            menu_manager.get_event(e)
            if e.type == p.QUIT:
                running = False

        mouse_pos = p.mouse.get_pos()
        menu_manager.update(mouse_pos)
        menu_manager.draw(screen, auto_display=False)
        p.display.flip()