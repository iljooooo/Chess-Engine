import src.ChessMain as ChessMain
import src.ChessEngine as ChessEngine
import pygame as p
from src.utils_interfaces.buttons import Button, ButtonGroup


WIDTH = HEIGHT = 512


def main():
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
        "call": lambda:print(0)
    }

    play_btn = Button(
        rect_attr = {"center": (WIDTH//2, HEIGHT//2 - BUTTONS_Y_SPACING)},
        text= 'PLAY',
        hover_text = "PLAY",
        **COMMON_ATTRIBUTES
    )

    settings_btn = Button(
        rect_attr={"center": (WIDTH//2, HEIGHT//2)},
        text = "SETTINGS",
        hover_text = "SETTINGS",
        **COMMON_ATTRIBUTES
    )

    credits_btn = Button(
        rect_attr={"center": (WIDTH//2, HEIGHT//2 + BUTTONS_Y_SPACING)},
        text= "CREDITS",
        hover_text= "CREDITS",
        **COMMON_ATTRIBUTES
    )

    buttons = ButtonGroup((
        play_btn,
        settings_btn,
        credits_btn
    )) 
    
    running = True
    while running:
        for e in p.event.get():

            buttons.get_event(e)
            if e.type == p.QUIT:
                running = False
        
        mouse_pos = p.mouse.get_pos()
        buttons.draw(screen, mouse_pos)
        p.display.flip()
##

if __name__ == '__main__':
    main()
##