from pico2d import * 
from gfw import *

import sys
self = sys.modules[__name__]

world = World(1)
transparent = True

def enter():
    world.append(Background('res/scene_image/game_clear.png'), 0)
    # world.append(self, 1)

def exit():
    world.clear()

def handle_event(e):
    if e.type == SDL_KEYDOWN and e.key == SDLK_ESCAPE:
        gfw.pop()
        return True

def draw():
    pass

def update():
    pass


if __name__ == '__main__':
    gfw.start_main_module()


