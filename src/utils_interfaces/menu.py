from typing import Dict, Iterable, Literal, Tuple
import pygame as p
from utils_interfaces.buttons import Button, _parse_color
p.init()


_THEMES_SPECIFICS: Dict[str, Dict[str, p.Color | str | None]] = {
    'light': {
        'background_color': p.Color('white')
    },

    'dark': {
        'background_color': p.Color('black')
    }
}
##

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

    def _get_theme(self) -> Literal['light', 'dark'] | None:
        if all([
            self.background_color == p.Color('white'),
            all([i._get_theme()=='light' for i in self.sprites()])
        ]):
            return 'light'
        
        elif all([
            self.background_color == p.Color('black'),
            all([i._get_theme()=='dark' for i in self.sprites()])
        ]):
            return 'dark'
    ##



    def _set_theme(self, theme: Literal['light', 'dark']) -> None:
        
        _THEMES_SPECIFICS['default'] = {
            'background_color': self.background_color
        }

        for key,val in _THEMES_SPECIFICS.get(theme, 'default').items():
            setattr(self, key, val)
        ##

        for btn in self.sprites():
            btn._change_theme()
        ##

        self.update(p.mouse.get_pos())
    ##


    def _change_theme(self) -> None:
        if self._get_theme() == 'light':
            self._set_theme('dark')
        elif self._get_theme() == 'dark':
            self._set_theme('light')
    ##
##



'''MenuManager class: implemented in order to have an easier control on different graphical elements in a game. It becomes useful since we basically can run a minimal main code, and do not have to always display different menus with overlapping elements in order to obtain the result. The main feature of the MenuManager are two command:
    
    - update() reads events thanks to pygame'''
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

    def _get_theme(self) -> Literal['light', 'dark'] | None:
        pass
    ##

    def _set_theme(self, theme) -> None:
        pass
    ##

    def _change_theme(self) -> None:
        pass
    ##
##

## THEMES HANDLING
