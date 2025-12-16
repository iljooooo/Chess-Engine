import sys
from typing import List, Tuple, Iterable, Callable
import pygame as p
from utils_interfaces.buttons import Button, ButtonGroup, _parse_color
p.init()


class Menu(p.sprite.Group):

    def __init__(
            self, 
            *bts: Iterable[Button], 
            background_color: p.Color|str|Tuple[int, int, int] = p.Color('white'),
    ) -> None:
        super().__init__(*bts)
        self.background_color = _parse_color(background_color)

        '''if self.background_image:
            if isinstance(self.background_image, str):
                self.background_image = p.transform.scale(p.image.load(self.background_image), self.screen.get_size()).convert_alpha(self.screen)
            elif isinstance(self.background_image, p.Surface):
                self.background_image.convert_alpha(self.screen)'''
    ##
        

    def update(self, mouse_pos: Tuple[int, int]) -> None:
        for w in self.sprites():
            w.update(mouse_pos)
    ##

    def get_event(self, e: p.event.Event) -> None:
        for w in self.sprites():
            w.get_event(e)
    ##

    def draw(self, surface: p.Surface, auto_display = True) -> None:

        surface.fill(self.background_color)

        if not auto_display:
            for w in self.sprites():
                w.draw(surface)

        else:
            pass
            #TODO: COMPLETE HERE
    ##
##

class MenuManager():

    def __init__(self, start_menu: Menu|None = None) -> None:
        self.current = start_menu
    ##

    def set(self, menu: Menu) -> None:
        self.current = menu
    ##

    def get_event(self, e: p.event.Event):
        if self.current is not None:
            self.current.get_event(e)
    ##

    def update(self, mouse_pos: Tuple[int, int]):
        if self.current is not None:
            self.current.update(mouse_pos)
    ##

    def draw(self, screen: p.Surface, auto_display: bool = True) -> None:
        if self.current is not None:
            self.current.draw(screen, auto_display)
    ##
##