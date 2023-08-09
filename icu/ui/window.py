
from types import SimpleNamespace
import pygame
import os

SDL_VIDEO_WINDOW_POS = 'SDL_VIDEO_WINDOW_POS'

def new_window(window_position, window_size, name="icu"):
    assert len(window_position) == 2
    assert len(window_size) == 2 
    
    #if SDL_VIDEO_WINDOW_POS in os.environ:
    #    old_window_position = os.environ[SDL_VIDEO_WINDOW_POS]
    #else:
    #    old_window_position = window_position
    os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % (window_position[0], window_position[1])
    pygame.init()
    screen = pygame.display.set_mode(window_size)
    if name is not None:
        pygame.display.set_caption(name)
    return screen

def get_window_info():
    import pywinctl as pwc
    npw = pwc.getActiveWindow()
    return SimpleNamespace(window_size = (npw.width, npw.height), window_position=(npw.left, npw.top), window_title=npw.title)


