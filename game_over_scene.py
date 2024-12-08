from pico2d import * 
from gfw import *

import sys
self = sys.modules[__name__]

world = World(1)
transparent = True

def enter():
    world.append(Background('res/scene_image/game_over.png'), 0)

    global font
    font = gfw.font.load('res/ENCR10B.TTF')

def exit():
    world.clear()

def handle_event(e):
    if e.type == SDL_KEYDOWN and e.key == SDLK_ESCAPE:
        gfw.pop()
        return True

def draw(): pass
    # gfw.font.draw_centered_text(font, msg, center_x, center_y + 30, (63, 0, 0))

def update(): pass

if __name__ == '__main__':
    gfw.start_main_module()


