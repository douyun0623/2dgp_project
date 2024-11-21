from pico2d import *
from gfw import *
from player import Knight
from AK47 import AK47

#import pause_scene

world = World(['bg', 'player', 'weapon']);

canvas_width = 1152 #1280
canvas_height = 648 #720
shows_bounding_box = True
shows_object_count = True

knight_info = {
    "id": "1",
    "name": "Bandit Knight",
    "type": "15x8", 
    "size": 366
}

def enter():
    world.append(HorzFillBackground('res/Plan5.png', 0), world.layer.bg)
    world.append(HorzFillBackground('res/Plan4.png', 0), world.layer.bg)
    world.append(HorzFillBackground('res/Plan3.png', 0), world.layer.bg)
    world.append(HorzFillBackground('res/Plan2.png', 0), world.layer.bg)
    world.append(HorzFillBackground('res/Plan1.png', 0), world.layer.bg)


    global Knight
    Knight = Knight(knight_info)
    world.append(Knight, world.layer.player)

    # 무기 장착
    global ak47
    ak47 = AK47(Knight)
    world.append(ak47, world.layer.weapon)

def exit():
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
        return 0
        #gfw.push(pause_scene)
        return True

    Knight.handle_event(e)
    ak47.handle_event(e)

if __name__ == '__main__':
    gfw.start_main_module()