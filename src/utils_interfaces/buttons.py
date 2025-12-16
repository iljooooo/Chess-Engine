import pygame as p
from typing import Iterable, Tuple, Dict
import copy
p.init()

LOADED_FONTS = {}

LABEL_DEFAULTS = {}

BUTTON_DEFAULTS = {
        "button_size": (128, 32),
        "call": None,
        "args": None,
        "call_on_up": True,
        "font": None,
        "font_size": 36,
        "text": None,
        "hover_text": None,
        "disable_text": None,
        "text_color": p.Color("white"),
        "hover_text_color": None,
        "disable_text_color": None,
        "fill_color": None,
        "hover_fill_color": None,
        "disable_fill_color": None,
        "idle_image": None,
        "hover_image": None,
        "disable_image": None,
        "hover_sound": None,
        "click_sound": None,
        "visible": True,
        "active": True,
        "bindings": ()
}

'''Helper function: accepts as input different ways of color formatting and always returns a pygame.Color object'''
def _parse_color(col: str | p.Color | Tuple[int, int, int]) -> p.Color:
    if col is not None:
        try:
            return p.Color(str(col))
        except ValueError as e:
            return p.Color(*col)
    return col
##

class _KwargMixin(object):
    """
    Useful for classes that require a lot of keyword arguments for customization. Used as an inheritance for most of the objects we instntiate.
    """

    def process_kwargs(self, name, defaults, kwargs):
        """
        Arguments are a name string (displayed in case of invalid keyword);
        a dictionary of default values for all valid keywords;
        and the kwarg dict.
        """
        settings = copy.deepcopy(defaults)
        for kwarg in kwargs:
            if kwarg in settings:
                if isinstance(kwargs[kwarg], dict):
                    settings[kwarg].update(kwargs[kwarg])
                else:
                    settings[kwarg] = kwargs[kwarg]
            else:
                message = "{} has no keyword: {}"
                raise AttributeError(message.format(name, kwarg))
        for setting in settings:
            setattr(self, setting, settings[setting])
##

#TODO: add some options to handle more complex graphical features: dropdown buttons menu, ecc...

#TODO: adding hovering animations effect

class Button(p.sprite.Sprite, _KwargMixin):
    
    """
    INSTANTIATE A BUTTON OBJECT. We basically overwrite the p.Sprite object in order to have a better comprehension of what is happening
    """
    #_invisible = p.Surface.convert_alpha(surface=_invisible)
    #_invisible.fill((0,0,0,0))

    def __init__(self, rect_attr, *groups, **kwargs):
        super(Button, self).__init__(*groups)
        color_args = (
            'text_color',
            'hover_text_color',
            'disable_text_color',
            'fill_color',
            'hover_fill_color',
            'disable_fill_color'
        )

        for c in color_args:
            if c in kwargs and kwargs[c] is not None:
                kwargs[c] = _parse_color(kwargs[c])
        self.process_kwargs("Button", BUTTON_DEFAULTS, kwargs)
        
        # self.button_size gets instanciated by self.process_kwargs
        self.rect = p.Surface(self.button_size).get_rect(**rect_attr) # type: ignore #
        rendered = self.render_text()

        self.idle_image = self.make_image(
            self.fill_color,    # type: ignore #
            self.idle_image,
            rendered["text"]    # type: ignore #
        )
        self.hover_image = self.make_image(
            self.hover_fill_color,   # type: ignore #
            self.hover_image,
            rendered["hover"],  # type: ignore #
        )
        self.disable_image = self.make_image(
            self.disable_fill_color, # type: ignore #
            self.disable_image,
            rendered["text"]    # type: ignore #
        )

        self.image = self.idle_image
        self.clicked = False
        self.hover = False
    ##        
    
    def render_text(self) -> Dict[str, p.Surface | None]:
        font, size = self.font, self.font_size # type: ignore #
        if (font, size) not in LOADED_FONTS:
            LOADED_FONTS[font, size] = p.font.Font(font, size)
        self.font: p.font.Font = LOADED_FONTS[font, size]

        '''These return boolean expressions. However by using such conditionals (with and) we also edit such char in-place if the first expression is not Null. Same logic is used in make_image() method below'''
        text: p.Surface | None = self.text and self.font.render(self.text, 1, self.text_color) # type: ignore #
        hover: p.Surface | None = self.hover_text and self.font.render(self.hover_text, 1, self.hover_text_color) # type: ignore #
        disable: p.Surface | None = self.disable_text and self.font.render(self.disable_text, 1, self.disable_text_color) # type: ignore #

        return {"text": text, "hover": hover, "disable": disable}
    ##

    def make_image(self, fill: p.Color | None, image: p.Surface | None, text: p.Surface | None) -> None | p.Surface:

        if not any((fill, image, text)):
            return None
        
        final_image = p.Surface(self.rect.size)
        #final_image = final_image.convert_alpha()
        final_image.fill((0,0,0,0))

        rect = final_image.get_rect()
        fill and final_image.fill(fill, rect)
        image and final_image.blit(image, rect)
        text and final_image.blit(text, text.get_rect(center=rect.center))

        return final_image
    ##

    def get_event(self, event: p.event.Event):
        if self.active and self.visible:
            if event.type == p.MOUSEBUTTONUP and event.button == 1:
                self.on_up_event(event)
            elif event.type == p.MOUSEBUTTONDOWN and event.button == 1:
                self.on_down_event(event)
            elif event.type == p.KEYDOWN and event.key in self.bindings:
                self.on_down_event(event, True)
            elif event.type == p.KEYUP and event.key in self.bindings:
                self.on_up_event(event, True)
    ##

    def on_up_event(self, event, onkey=False):
        if self.clicked and self.call_on_up:
            self.click_sound and self.click_sound.play()
            self.call and self.call()
        self.clicked = False
    ##

    def on_down_event(self, event, onkey=False):
        if self.hover or onkey:
            self.clicked = True
            if not self.call_on_up:
                self.click_sound and self.click_sound.play()
                self.call and self.call()
    ##

    '''Handles hovering'''
    def update(self, prescaled_mouse_pos):
        hover = self.rect.collidepoint(prescaled_mouse_pos)
        pressed = p.key.get_pressed()
        if any(pressed[key] for key in self.bindings):
            hover = True
        if not self.visible:
            pass
            #self.image = Button._invisible
        elif self.active:
            self.image = (hover and self.hover_image) or self.idle_image
            if not self.hover and hover:
                self.hover_sound and self.hover_sound.play()
            self.hover = hover
        else:
            self.image = self.disable_image or self.idle_image
    ##

    def draw(self, surface):
        surface.blit(self.image, self.rect)
    ##

    def get_size(self) -> Tuple[int, int]:
        return self.button_size
    ##
##

class ButtonGroup(p.sprite.Group):
    '''Same as Button, here we overwrite sprite.Group calls for the specifics we need'''

    def __init__(self, *sprites: Iterable[Button]) -> None:
        super().__init__(*sprites)

    def get_event(self, e: p.event.Event):
        for button in self.sprites():
            button.get_event(e)
    ##

    def draw(self, screen: p.Surface , mouse_pos: Tuple[int, int]):
        for button in self.sprites():
            button.update(mouse_pos)
            button.draw(screen)
    ##