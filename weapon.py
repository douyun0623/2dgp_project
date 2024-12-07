from pico2d import *
from gfw import *
import time

class Bullet(Sprite):
    def __init__(self, player, fg_fname, power, speed):
        super().__init__(fg_fname, -100, -100)
        self.player = player
        self.power = power
        self.speed = speed  # 총알 속도
        self.mag = 3  # 크기 배율을 설정
        self.angle = 0
        self.dx, self.dy = 0, 0
        self.reset()
    def reset(self):
        self.valid = False
    def fire(self, weapon_x, weapon_y):
        world = gfw.top().world
        if world.count_at(world.layer.enemy) == 0: return False
        demons = world.objects_at(world.layer.enemy)
        self.x, self.y = weapon_x, weapon_y
        INF = float('inf')
        nearest = min(demons, key=lambda d: INF if d.is_stunned() else (d.x - self.x) ** 2 + (d.y - self.y) ** 2)
        # if nearest.is_stunned(): return False
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
        # if obj.is_stunned():
        #     return False

        dead = obj.hit(self.power)

        # if dead and obj.is_remove == True:
        #     main_scene = gfw.top()
        #     main_scene.world.remove(obj)

        self.reset()
        return dead
    def get_bb(self):
        r = 12 # radius
        return self.x-r, self.y-r, self.x+r, self.y+r

class AK47(AnimSprite):
    COOL_TIME = 0.0
    def __init__(self, player):
        super().__init__(f'res/gun/AK47_Sprite.png', player.x, player.y, 7, 12)
        self.player = player
        self.bullets = []
        self.power = 25
        self.speed = 200
        self.cooldown = 0.0
        self.is_firing = False  # 발사 상태를 추적
        self.index = 0
        for _ in range(6):
            self.append()

    def get_pos(self):
        if self.player.flip:
            self.x = self.player.x + 25
            self.y = self.player.y - 80
        else:
            self.x = self.player.x - 25
            self.y = self.player.y - 80
    def get_bullet_pos(self):
        if self.player.flip:
            return self.x + 35, self.y + 10
        else:
            return self.x - 35, self.y + 10
    def append(self):
        bullet = Bullet(self.player, f'res/gun/AK47_Bullet.png', self.power, self.speed)
        self.bullets.append(bullet) # 총알 이미지 추가
    def fire(self):  # fire() 메서드 추가
        if self.cooldown > 0:  # 쿨타임이 남아 있으면 발사하지 않음
            return
        # 발사할 총알이 준비되었는지 확인하고 발사
        for b in self.bullets:
            if not b.valid:  # 총알이 발사되지 않은 상태일 때
                bullet_x, bullet_y = self.get_bullet_pos()  # 총알 발사 위치 얻기
                fired = b.fire(bullet_x, bullet_y)  # 총알을 발사
                if fired:
                    self.time = self.COOL_TIME  # 발사 후 쿨타임 초기화
                    self.is_firing = True
                return
    def update(self):
        # 쿨타임 감소 처리
        if self.cooldown > 0:
            self.cooldown -= gfw.frame_time

        # 발사 상태라면 애니메이션 프레임 업데이트
        if self.is_firing:
            self.index += 1
            if self.index >= 12:  # 애니메이션 마지막 프레임에 도달하면 초기화
                self.index = 0
                self.is_firing = False  # 발사 상태 해제


        for b in self.bullets: 
            if b.valid:  # 이미 발사된 총알만 업데이트
                b.update()

    def draw(self):
        bg = self.player.bg
        self.get_pos()
        screen_pos = bg.to_screen(self.x, self.y)

        # 디버깅을 위해 index와 화면 좌표를 출력해봄
        # print(f"Anim Index: {self.index}, Screen Pos: {screen_pos}")
        
        # 좌우 반전 여부에 따라 그리기
        flip_scale = '' if self.player.flip else 'h'
        self.image.clip_composite_draw(self.index * self.width, 0, self.width, self.height, 0, flip_scale, *screen_pos, self.width, self.height)

        for b in self.bullets: 
            if b.valid: b.draw()

    def try_hit(self, obj):
        for b in self.bullets:
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