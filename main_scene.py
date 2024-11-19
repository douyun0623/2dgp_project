from pico2d import *
from gfw import *
from player import Knight
#import floor
#import pause_scene

world = World(['bg', 'player']);

canvas_width = 1152 #1280
canvas_height = 648 #720
shows_bounding_box = True
shows_object_count = True

knight_info = {
    "id": "107572",
    "name": "Coffee Cookie",
    "type": "13x6", 
    "size": 320
}

def enter():
    world.append(HorzFillBackground('res/Plan5.png', 0), world.layer.bg)
    world.append(HorzFillBackground('res/Plan4.png', 0), world.layer.bg)
    world.append(HorzFillBackground('res/Plan3.png', 0), world.layer.bg)
    world.append(HorzFillBackground('res/Plan2.png', 0), world.layer.bg)
    world.append(HorzFillBackground('res/Plan1.png', 0), world.layer.bg)

   # floor.init()
   	#world.append(floor, world.layer.controller)

    global Knight
    Knight = Knight(knight_info)
    world.append(Knight, world.layer.player)

def exit():
    music.stop()
    world.clear()

def pause():
    print('[main.pause()]')
    music.pause()

def resume():
    print('[main.resume()]')
    music.resume()

def handle_event(e):
    if e.type == SDL_KEYDOWN and e.key == SDLK_1:
        print(world.objects)
        return

    if e.type == SDL_KEYDOWN and e.key == SDLK_ESCAPE:
        gfw.push(pause_scene)
        return True

    #cookie.handle_event(e)

if __name__ == '__main__':
    gfw.start_main_module()

