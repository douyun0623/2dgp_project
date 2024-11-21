from pico2d import *
from gfw import *
import time

class Weapon:
    def __init__(self, owner, fg_fname, attack_speed, range, damage, fps, initX, initY):
        self.owner = owner
        self.attack_speed = attack_speed
        self.range = range
        self.damage = damage
        self.cooldown = 0  # 쿨다운 타이머
        
        # 무기 이미지 및 애니메이션 설정
        self.image = load_image(fg_fname)
        self.width, self.height = 96, 48
        self.fps = fps
        self.frame_count = 0  # 총 프레임 수
        self.current_frame = 0
        self.time_acc = 0
        self.initX, self.initY = initX, initY
        
        # 위치
        self.x, self.y = self.owner.x - self.initX, self.owner.y + self.initY

    def update(self):
        if self.cooldown > 0:
            self.cooldown -= gfw.frame_time

        # 무기 위치를 주인(캐릭터)와 함께 이동
        self.x, self.y = self.owner.x, self.owner.y + self.initY
        #self.x, self.y = self.owner.x, self.owner.y,        + self.initX

        # 애니메이션 업데이트
        self.time_acc += gfw.frame_time
        if self.time_acc >= 1 / self.fps:
            self.current_frame = (self.current_frame + 1) % self.frame_count
            self.time_acc -= 1 / self.fps

    def attack(self):
        if self.cooldown <= 0:
            print(f"Attack with {self.damage} damage!")
            self.cooldown = 1 / self.attack_speed  # 쿨다운 초기화

    def draw(self):
        # 현재 프레임에 해당하는 src_rect 계산
        src_x = self.current_frame * self.width
        flip = 'h' if self.owner.flip == False else ''  # 방향에 따라 뒤집기 설정
        if self.owner.flip == True:
            self.x += self.initX
        else:
            self.x -= self.initX
        self.image.clip_composite_draw(src_x, 0, self.width, self.height, 0, flip, self.x, self.y, self.width, self.height)


class Bullet:
    def __init__(self, x, y, range, damage, direction):
        self.x, self.y = x, y
        self.range = range
        self.damage = damage
        self.speed = 500
        self.direction = 1 if direction else -1
        self.distance_traveled = 0
        self.image = load_image('res/bullet.png')

    def update(self):
        self.x += self.speed * gfw.frame_time * self.direction
        self.distance_traveled += self.speed * gfw.frame_time
        if self.distance_traveled >= self.range:
            gfw.world.remove(self)

    def draw(self):
        self.image.draw(self.x, self.y)
