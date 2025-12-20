import sys
from typing import Iterable
import pygame as p
from utils_interfaces.buttons import Button, LOADED_FONTS
from utils_interfaces.menu import Menu, MenuManager
p.init()


def _change_button_theme(btn: Button, **kwargs):
    
    DEFAULTS = {
        'fill_color': btn.fill_color,
        'hover_fill_color': btn.hover_fill_color,
        'disable_fill_color': btn.disable_fill_color,
        'text_color': btn.text_color,
        'hover_text_color' : btn.hover_text_color,
        'disable_text_color': btn.disable_text_color 
    }

    print(f'{btn.fill_color,}, {btn.hover_fill_color}, {btn.disable_fill_color}')
    print(f'{btn.text_color}, {btn.hover_text_color}')

    for key, val in DEFAULTS.items():
        btn.__setattr__(key, kwargs.get(key, val))
    
    '''text: p.Surface | None = btn.text and btn.font.render(btn.text, 1, btn.text_color) # type: ignore #
    hover: p.Surface | None = btn.hover_text and btn.font.render(btn.hover_text, 1, btn.hover_text_color) # type: ignore #
    disable: p.Surface | None = btn.disable_text and btn.font.render(btn.disable_text, 1, btn.disable_text_color)

    rendered = {"text": text, "hover": hover, "disable": disable}'''
    rendered = btn.render_text()

    btn.idle_image = btn.make_image(
        btn.fill_color,    # type: ignore #
        None,
        rendered["text"]    # type: ignore #
    )
    btn.hover_image = btn.make_image(
        btn.hover_fill_color,   # type: ignore #
        None,
        rendered["hover"],  # type: ignore #
    )
    btn.disable_image = btn.make_image(
        btn.disable_fill_color, # type: ignore #
        None,
        rendered["text"]    # type: ignore #
    )
##



'''Helper function that is needed for debug purposes only, add a breakpoint at print() line to have a debug waiting point'''
def _wait():
    print('WAITED!')
##



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


theme_button = Button(
    rect_attr = {"center": (WIDTH//2, HEIGHT//2 + BUTTONS_Y_SPACING)},
    text = "THEME",
    hover_text = "THEME",
    call = lambda: 0,
    **COMMON_ATTRIBUTES
)
theme_button.call = lambda: _change_button_theme(
    theme_button,
    fill_color =  p.Color('black'),
    hover_fill_color = p.Color('white'),
    text_color = p.Color('white'),
    hover_text_color = p.Color('black')
)

settings_menu.add(
    [
        theme_button,

        Button(
            rect_attr = {"center": (WIDTH//2, HEIGHT//2)},
            text= 'WAIT',
            hover_text = "WAIT",
            call = _wait,
            **COMMON_ATTRIBUTES
        ),

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