from pico2d import *
from gfw import *
import time

class Bullet(Sprite):
    def __init__(self, player, fg_fname, power, speed):
        super().__init__(fg_fname, -100, -100)
        self.player = player
        self.power = power
        self.speed = speed  # 총알 속도
        self.mag = 4  # 크기 배율을 설정
        self.angle = 0
        self.dx, self.dy = 0, 0
        self.reset()
    def reset(self):
        self.valid = False
    def fire(self):
        world = gfw.top().world
        if world.count_at(world.layer.enemy) == 0: return False
        demons = world.objects_at(world.layer.enemy)
        self.x, self.y = self.player.x, self.player.y
        INF = float('inf')
        nearest = min(demons, key=lambda d: INF if d.is_stunned() else (d.x - self.x) ** 2 + (d.y - self.y) ** 2)
        if nearest.is_stunned(): return False
        self.angle = math.atan2(nearest.y - self.y, nearest.x - self.x)
        self.dx = math.cos(self.angle) * self.speed
        self.dy = math.sin(self.angle) * self.speed
        self.valid = True
        return True
    def draw(self):
        bg = self.player.bg
        x, y = bg.to_screen(self.x, self.y)
        self.image.clip_composite_draw(0, 0, self.width, self.height, self.angle, '', x, y, self.width* self.mag, self.height* self.mag)
    
    def update(self):
        self.angle += self.speed * TWO_PI * gfw.frame_time
        if self.angle >= TWO_PI:
            self.angle -= TWO_PI
        self.x = self.player.x + self.radius * math.cos(self.angle)
        self.y = self.player.y + self.radius * math.sin(self.angle)
    def update(self):
        self.x += self.dx * gfw.frame_time
        self.y += self.dy * gfw.frame_time

        l, b = self.player.bg.from_screen(0, 0)
        cw, ch = get_canvas_width(), get_canvas_height()
        r, t = self.player.bg.from_screen(cw, ch)
        if self.x < l or r < self.x or \
            self.y < b or t < self.y:
            self.reset()
    def try_hit(self, obj): # returns False if obj is removed
        if not gfw.collides_box(self, obj):
            return False
        if obj.is_stunned():
            return False

        dead = obj.hit(self.power)
        if dead:
            main_scene = gfw.top()
            main_scene.world.remove(obj)

        self.reset()
        return dead
    def get_bb(self):
        r = 12 # radius
        return self.x-r, self.y-r, self.x+r, self.y+r

class AK47(AnimSprite):
    COOL_TIME = 1.0
    def __init__(self, player):  # width = 96, height 48    attack_speed=1.5, range=100, damage=c, fps=10, initX = 25, initY = -80
        super().__init__(f'res/gun/AK47_Sprite.png', player.x, player.y, 10, 12)
        self.player = player
        self.bullets = []
        self.power = 25
        self.speed = 200
        self.time = self.COOL_TIME
        self.append()
    def get_pos(self):
        if self.player.flip:
            self.x = self.player.x + 25
            self.y = self.player.y - 80
        else:
            self.x = self.player.x - 25
            self.y = self.player.y - 80
    def append(self):
        bullet = Bullet(self.player, f'res/gun/AK47_Bullet.png', self.power, self.speed)
        self.bullets.append(bullet) # 총알 이미지 추가
    def fire(self):  # fire() 메서드 추가
        # 발사할 총알이 준비되었는지 확인하고 발사
        for b in self.bullets:
            if not b.valid:  # 총알이 발사되지 않은 상태일 때
                fired = b.fire()  # 총알을 발사
                if fired:
                    self.time = self.COOL_TIME  # 발사 후 쿨타임 초기화
                return
    def update(self):
        fires = False 
        if self.time > 0:
            self.time -= gfw.frame_time
        else:
            fires = True
        for b in self.bullets: 
            if b.valid: 
                b.update()
            elif fires:
                fires = False
                fired = b.fire()
                if fired:
                    self.time = self.COOL_TIME

    def draw(self):
        index = self.get_anim_index()
        bg = self.player.bg
        self.get_pos()
        screen_pos = bg.to_screen(self.x, self.y)

        # 디버깅을 위해 index와 화면 좌표를 출력해봄

        # print(f"Anim Index: {index}, Screen Pos: {screen_pos}")
        
        
        # 좌우 반전 여부에 따라 그리기
        flip_scale = '' if self.player.flip else 'h'

        self.image.clip_composite_draw(
            index * self.width, 0, self.width, self.height, 
            0, flip_scale,  # 좌우 반전을 위한 flip_scale
            *screen_pos, 
            self.width, self.height
        )


        for b in self.bullets: 
            if b.valid: b.draw()
    def try_hit(self, obj):
        for b in self.bombs:
            if b.valid and b.try_hit(obj):
                return True
        return False

class Weapons:
    def __init__(self, player):
        self.weapons = []
    def append(self, weapon):
        self.weapons.append(weapon)
    def update(self):
        for w in self.weapons: w.update()
    def draw(self):
        for w in self.weapons: w.draw()
    def try_hit(self, obj):
        for w in self.weapons:
             if w.try_hit(obj):
                return True
        return False
    def attack(self):
        for weapon in self.weapons:
            weapon.fire()  # 각 무기의 fire 메서드 호출