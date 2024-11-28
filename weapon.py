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
        self.active = False
        self.initX, self.initY = initX, initY
        
        # 위치
        self.x, self.y = self.owner.x, self.owner.y + self.initY

        # 총알을 관리할 리스트
        self.bullets = []  # 총알 리스트

    def update(self):
        if self.cooldown > 0:
            self.cooldown -= gfw.frame_time

        # 무기 위치를 주인(캐릭터)와 함께 이동
        self.x, self.y = self.owner.x, self.owner.y + self.initY

        # 애니메이션 업데이트
        if self.active == True:
            self.time_acc += gfw.frame_time
            if self.time_acc >= 1 / self.fps:
                self.current_frame = (self.current_frame + 1) % self.frame_count
                self.time_acc -= 1 / self.fps
                if self.current_frame == 0:
                    self.active = False

        # 총알 업데이트
        for bullet in self.bullets:
            bullet.update()  # 각 총알의 업데이트 호출

        # if self.cooldown <= 0:  # 쿨다운이 0이면 공격
        #     self.attack()  # 공격 실행

    def handle_event(self, event):
        # 특정 키로 무기 활성화
        if event.type == SDL_KEYDOWN:
            if event.key == SDLK_k:  # K 키로 무기 활성화
                self.shoot()
                self.active = True
                # 공격이 바로 시작되도록 하기 위해 attack을 한 번만 호출

        elif event.type == SDL_KEYUP:
            if event.key == SDLK_k:
                pass

    def attack(self):
        if self.cooldown <= 0:
            self.shoot()  # 총알 발사
            print(f"Attack with {self.damage} damage!")
            self.cooldown = 1 / self.attack_speed  # 쿨다운 초기화

    def shoot(self):
        # 총알의 방향을 설정합니다.
        direction = 1 if self.owner.flip else -1  # 플레이어가 오른쪽을 보면 오른쪽으로, 왼쪽을 보면 왼쪽으로

        # 총알을 생성하고, 총알 리스트에 추가합니다.
        bullet = Bullet(self.x, self.y, self.owner, direction, self.range, self.damage, 'res/gun/AK47_Bullet.png', 16, 16, 15)
        self.bullets.append(bullet)  # 총알을 리스트에 추가

    def draw(self):
        # 현재 프레임에 해당하는 src_rect 계산
        src_x = self.current_frame * self.width
        flip = 'h' if self.owner.flip == False else ''  # 방향에 따라 뒤집기 설정
        if self.owner.flip == True:
            self.x += self.initX
        else:
            self.x -= self.initX

        screen_pos = self.owner.bg.to_screen(self.x, self.y)
        self.image.clip_composite_draw(src_x, 0, self.width, self.height, 0, flip, *screen_pos, self.width, self.height)

        # 총알을 화면에 그리기
        for bullet in self.bullets:
            bullet.draw()  # 각 총알의 draw 메소드를 호출하여 화면에 그리기


class Bullet:
    def __init__(self, x, y,owner, direction, range, damage, fg_fname, width, height, initY):
        self.x, self.y = x, y + initY
        self.range = range
        self.owner = owner
        self.damage = damage
        self.speed = 500  # 총알 속도
        self.mag = 2  # 크기 배율을 설정
        self.direction = direction  # 1이면 오른쪽, -1이면 왼쪽
        self.distance_traveled = 0  # 이동한 거리
        self.width, self.height = width, height  # width와 height로 수정
        self.image = load_image(fg_fname)  # 총알 이미지 로드

    def update(self):
        # 총알이 이동하는 코드
        self.x += self.speed * gfw.frame_time * self.direction  # 방향에 따라 x축 이동
        self.distance_traveled += self.speed * gfw.frame_time

    def draw(self):
        # 총알을 화면에 그리는 코드
        screen_pos = self.owner.bg.to_screen(self.x, self.y)
        self.image.clip_composite_draw(0, 0, self.width, self.height, 0, '', *screen_pos, self.width * self.mag, self.height * self.mag)
