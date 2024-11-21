# weapon.py
from pico2d import *
from gfw import *

class Weapon:
    def __init__(self, owner, fg_fname, attack_speed, range, damage, fps):
        self.owner = owner
        self.attack_speed = attack_speed
        self.range = range
        self.damage = damage
        self.cooldown = 0  # 쿨다운 타이머
        
        # SheetSprite 사용하여 무기 이미지 로드
        self.weapon_sprite = SheetSprite(fg_fname, self.owner.x, self.owner.y, fps)  # 이미지 로드 및 스프라이트 설정
        self.weapon_sprite.src_rects = [(i * self.weapon_sprite.width, 0, self.weapon_sprite.width, self.weapon_sprite.height) for i in range(5)]  # 예시로 5 프레임 애니메이션 설정

    def update(self):
        if self.cooldown > 0:
            self.cooldown -= gfw.frame_time
        self.weapon_sprite.update()  # 애니메이션 업데이트

        # 무기 위치를 주인(캐릭터)와 함께 이동
        self.x, self.y = self.owner.x, self.owner.y
        self.weapon_sprite.x, self.weapon_sprite.y = self.x, self.y

    def attack(self):
        if self.cooldown <= 0:
            print(f"Attack with {self.damage} damage!")
            self.cooldown = 1 / self.attack_speed  # 쿨다운 초기화
    
    def draw(self):
        self.weapon_sprite.draw()  # 애니메이션 그리기


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
