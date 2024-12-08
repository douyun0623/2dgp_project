from pico2d import *
from gfw import *
from enemy import Demon, DemonGen
from player import Knight


world = World(['bgi', 'bg', 'enemy', 'player', 'weapon','controller'])

canvas_width = 1152  # 1280
ㅁ = 648  # 720
shows_bounding_box = True
shows_object_count = True

knight_info = {
    "id": "1",
    "name": "Bandit Knight",
    "type": "15x8", 
    "size": 366
}

class CollisionChecker:
    def draw(self): pass
    def update(self):
        for obj in world.objects_at(world.layer.enemy):
            Knight.weapon.try_hit(obj)

def enter():
    world.append(HorzFillBackground('res/navy_theme_background.png', 0), world.layer.bgi)

    world.bg = MapBackground('res/map/floor1.tmj', tilesize=50)
    world.bg.margin = 210
    world.bg.x = 1400
    world.map_name = "floor1"
    world.bg.set_collision_tiles({2})
    world.append(world.bg, world.layer.bg)
    
    global Knight
    Knight = Knight(knight_info, world.bg)
    world.append(Knight, world.layer.player)
    world.append(Knight.weapon, world.layer.weapon)

    k = load_image(f'res/gun/AK47_Sprite.png')
    print(k.h)

    world.append(CollisionChecker(), world.layer.controller)

def exit():
    world.clear()

def pause(): pass

def resume(): pass

def handle_event(e):
    if e.type == SDL_KEYDOWN and e.key == SDLK_1:
        print(world.objects)
        return

    if e.type == SDL_KEYDOWN and e.key == SDLK_ESCAPE:
        return 0

    Knight.handle_event(e)

if __name__ == '__main__':
    gfw.start_main_module()