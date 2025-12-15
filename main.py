import src.ChessMain as ChessMain
import src.ChessEngine as ChessEngine
import pygame as p
from src.UI import GeneralMenu, Button, Text, NewGameMenu, SettingsMenu


WIDTH = HEIGHT = 512


def main():
    p.init()
    screen = p.display.set_mode((WIDTH, HEIGHT))
    #clock = p.time.Clock()
    #screen.fill(p.Color('white'))

    menu = GeneralMenu(
        screen=screen,
        bg_color='black',
        elements=[
            Button(
                x = 100, 
                y = 100, 
                color='white',
                text='NEW GAME',
                width=100,
                height=20,
                callback = lambda:0
            ),
            
            Button(
                x = 100,
                y = 200,
                color = 'white',
                text='SETTINGS',
                width=100,
                height=20,
                callback = lambda: 0
            ),

            Button(
                x = 100,
                y = 200,
                color = 'white',
                text = 'CREDITS',
                width = 100,
                height = 20,
                callback= lambda: 0
            )
                
        ]
    )
##

if __name__ == '__main__':
    main()
##