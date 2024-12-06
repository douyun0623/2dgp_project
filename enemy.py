import math
import random
from pico2d import * 
from gfw import *
# from map_helper import *

class Demon(AnimSprite):
    STUN_DURATION = 1.5
    STEP_BACK_TILL = STUN_DURATION - 0.2
    DEAD_DURATION = 2.0
    def __init__(self, type, x, y):
        self.info = INFO[type]
        frame_count = self.info.frame_info['idle']['frames']
        super().__init__(self.info.file, x, y, random.uniform(8, 10), frame_count)
        self.layer_index = gfw.top().world.layer.enemy
        self.speed = random.uniform(*self.info.speed)
        self.state = 'idle'  # 'idle' 상태로 초기화
        self.flip = ''
        self.is_remove = False
        self.is_attack = False
        self.mag = 2  # 이미지 크기를 배 확대
        self.max_life = self.info.life
        self.life = self.max_life
        self.stun_timer = 0
        self.score = self.info.score
        self.is_dead = False  # 죽음 상태 추가
        self.dead_timer = 0.0  # 사라지기까지 대기 시간

        world = gfw.top().world
        self.player = world.objects_at(world.layer.player)   # 플레이어의 위치 가져옴

    def check_stun(self):
        if self.stun_timer <= 0: return False
        self.stun_timer -= gfw.frame_time
        if self.stun_timer > self.STEP_BACK_TILL:
            self.x += self.waver_x * gfw.frame_time
            self.y += self.waver_y * gfw.frame_time
        else:
            self.set_anim('idle')
        return True

    def is_stunned(self):
        return self.stun_timer > 0

    def hit(self, damage): #return True if dead
        if self.stun_timer > 0:
            return False
        self.set_anim('stunned')
        self.life -= damage
        if self.life <= 0: 
            self.state = 'dead'
            self.is_dead = True
            self.dead_timer = self.DEAD_DURATION
            self.set_anim('dead')  # 죽음 애니메이션 설정
            return True

        self.stun_timer = self.STUN_DURATION
        world = gfw.top().world
        player = world.object_at(world.layer.player, 0)
        diff_x, diff_y = player.x - self.x, player.y - self.y
        dist = math.sqrt(diff_x ** 2 + diff_y ** 2)
        waver_distance = 20
        self.waver_x = -waver_distance * diff_x / dist
        self.waver_y = -waver_distance * diff_y / dist

        return False

    def is_dead(self):
        return self.life <= 0

    def update(self):
        if self.check_stun():
            return

        if self.is_dead:
            self.set_anim('dead')  # 죽음 상태 유지
            self.dead_timer -= gfw.frame_time
            if self.dead_timer <= 0:
                self.is_remove = True
            return

        world = gfw.top().world
        player = world.object_at(world.layer.player, 0)
        diff_x, diff_y = player.x - self.x, player.y - 70 - self.y
        dist = math.sqrt(diff_x ** 2 + diff_y ** 2)

        if dist >= self.info.attackRange and self.is_attack == False:
            self.set_anim('idle')
            dx = self.speed * diff_x / dist * gfw.frame_time
            self.x += dx
            self.y += self.speed * diff_y / dist * gfw.frame_time
            self.flip = 'h' if dx > 0 else ''
        else:
            self.is_attack = True
            self.set_anim('attack')

        # 공격하는 상태의 마지막 프레임 일때, 플레이어 위치와와 enemy의 위체에서 공격사거리와 겹치면 플에이어에게 데미지를 주고 싶다.
        if self.state == 'attack' and self.get_anim_index() == self.info.frame_info['attack']['frames'] - 1:  # 공격하는 상태에고, 
            self.set_anim('idle')
            self.is_attack = False
            if dist <= self.info.attackRange:   
                if player.is_invincible:    # 무적
                    print(f"플레이어 무적상태! 현재 HP: {player.hp}")
                else:   # 무적 x
                    player.hp -= self.info.attackDamage
                    print(f"플레이어 HP 감소! 현재 HP: {player.hp}")

    # 애니메이션 상태에 맞는 프레임을 설정하는 함수
    def set_anim(self, state):
        # 현재 상태에 맞는 프레임 수로 바꿔줌
        self.frame_count = self.info.frame_info[self.state]['frames']    

        if self.state != state:
            self.state = state
            self.created_on = time.time()

    # 예시: Demon 클래스의 draw 메서드에서 사용하기
    def draw(self):
        # 현재 상태에 맞는 프레임 정보를 가져옵니다.
        bg = gfw.top().world.bg
        screen_pos = bg.to_screen(self.x, self.y)

        frame_info = self.info.frame_info[self.state]

        index = self.get_anim_index()
        if self.state == 'dead' and self.is_dead:
            index = frame_info['frames'] - 1  # 마지막 프레임 고정


        # 애니메이션 프레임 인덱스를 출력
        # print(f"Drawing {self.state} frame {index}")
        
        # 각 프레임의 위치와 크기 정보
        l, b = frame_info['start_pos']
        w, h = frame_info['frame_size']

        # 각 프레임의 정확한 위치 계산 (index에 따른 x 위치)
        l = frame_info['start_pos'][0] + index * w
        
        
        # 이미지를 그릴 위치
        # screen_pos = (self.x, self.y)
        flip_scale = 1 if self.flip else -1  # self.is_flipped가 True일 때 좌우 반전, False일 때 정상

        # 이미지 그리기
        self.image.clip_composite_draw(
            l, b, w, h,  # 클립 영역
            0,  # 회전 각도
            'h',  # 수평 반전
            *screen_pos,  # 그려질 위치
            self.mag * w * flip_scale, self.mag * h  # 크기
        )  

        # 좌표를 출력하여 확인
        # print(f"Drawing at position: {self.x}, {self.y}")


    def get_bb(self):
        # 기존 bbox에서 오프셋 값 가져오기
        l, b, r, t = self.info.bbox
        if self.flip == 'h':
            l, r = -r, -l

        # 프레임 크기 계산
        w, h = self.info.frame_info[self.state]['frame_size']
        w, h = w * self.mag, h * self.mag

        # 중심 좌표를 기준으로 bbox 적용
        x_center = self.x
        y_center = self.y

        # 좌측 하단과 우측 상단 계산 (프레임 크기와 bbox 오프셋 포함)
        left = x_center - w / 2 - l
        bottom = y_center - h / 2 - b
        right = x_center + w / 2 - r
        top = y_center + h / 2 - t

        return left, bottom, right, top

    def is_on_obstacle(self):
        return False


class DemonInfo:
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

if __name__ == '__main__':
    a = DemonInfo(clazz=Demon, file='res/monster/crimson_wolf.png', frames=0, 
        speed=(50,100), bbox=(-15, -15, 15, 15), life=50)
    print(a.__dict__)
    print(a.bbox, a.life)


INFO = [
    # 늑대
    DemonInfo(
        clazz=Demon,
        file='res/monster/crimson_wolf.png',
        frame_info={
            'idle': {'frames': 4, 'start_pos': (0, 1197 - 72 * 2), 'frame_size': (72, 72)},   # 
            'attack': {'frames': 5, 'start_pos': (0, 1197 - 609), 'frame_size': (72, 73)},  # 
            'stunned': {'frames': 8, 'start_pos': (0, 1197 - 536), 'frame_size': (74, 73)},  # 한대 맞았을때
            'dead': {'frames': 3, 'start_pos': (0, 1197 - 650), 'frame_size': (72, 41)}  # 사망시 이미지
        },
        speed=(80, 90),
        attackDamage=2,
        attackRange=80,
        bbox=(-15, -15, 15, 15),
        life=60,
        score=10,
    ),

    # 새
    DemonInfo(
        clazz=Demon,
        file='res/monster/night_wing.png',
        frame_info={
            'idle': {'frames': 10, 'start_pos': (0, 1773 - 151), 'frame_size': (73, 79)},
            'attack': {'frames': 15, 'start_pos': (0, 1773 - 1166), 'frame_size': (82, 106)},
            'stunned': {'frames': 8, 'start_pos': (0, 1773 - 752), 'frame_size': (74, 74)},
            'dead': {'frames': 5, 'start_pos': (0, 1773 - 914), 'frame_size': (85, 89)}  # 사망시 이미지
        },
        speed=(40, 50),
        attackDamage=3,
        attackRange=80,
        bbox=(-28, -5, 8, 31),
        life=150,
        score=50,
    ),

    # 오크
    DemonInfo(
        clazz=Demon,
        file='res/monster/red_orc_warrior.png',
        frame_info={
            'idle': {'frames': 6, 'start_pos': (0, 1245 - 216), 'frame_size': (72, 74)},
            'attack': {'frames': 4, 'start_pos': (0, 1245 - 648), 'frame_size': (103, 89)},
            'stunned': {'frames': 5, 'start_pos': (0, 1245 - 314), 'frame_size': (78, 73)},
            'dead': {'frames': 12, 'start_pos': (0, 1245 - 559), 'frame_size': (78, 98)}  # 사망시 이미지
        },
        speed=(50, 60),
        attackDamage=4,
        attackRange=70,
        bbox=(-25, -14, 25, 14),
        life=100,
        score=30,
    ),

    # boss
    DemonInfo(
        clazz=Demon,
        file='res/monster/black_dragon.png',
        frame_info={
            'idle': {'frames': 6, 'start_pos': (0, 1857 - 216), 'frame_size': (140, 113)},
            'attack11': {'frames': 12, 'start_pos': (0, 1857 - 965), 'frame_size': (172, 146)},
            'stunned': {'frames': 15, 'start_pos': (0, 1857 - 444), 'frame_size': (138, 113)},
            'dead': {'frames': 10, 'start_pos': (0, 1857 - 688), 'frame_size': (145, 140)},  # 사망시 이미지
            'attack': {'frames': 12, 'start_pos': (0, 1857 - 1258), 'frame_size': (160, 141)}
        },
        speed=(50, 60),
        attackDamage=4,
        attackRange=150,
        bbox=(-25, -14, 25, 14),
        life=100,
        score=30,
    ),
]


def position_somewhere_outside_screen():
    # MARGIN = -100
    MARGIN = 50
    bg = gfw.top().world.bg
    cw, ch = get_canvas_width(), get_canvas_height()
    l, b = bg.from_screen(0, 0)
    r, t = bg.from_screen(cw, ch)
    side = random.randint(1, 4)
    if side == 1: # left
        x, y = l - MARGIN, b + random.random() * ch
    elif side == 2: # bottom
        x, y = l + random.random() * cw, b - MARGIN
    elif side == 3: # right
        x, y = r + MARGIN, b + random.random() * ch
    else: # side == 4, up
        x, y = l + random.random() * cw, t + MARGIN
    # print(f'{side=} {(x,y)=}')
    return x, y

def position_within_bounds(zone):
    # (l, b)는 좌하단, (r, t)는 우상단
    x = random.uniform(zone['l'], zone['r'])  # x는 좌측(l)과 우측(r) 사이에서 무작위 값
    y = random.uniform(zone['b'], zone['t'])  # y는 하단(b)과 상단(t) 사이에서 무작위 값
    return x, y

class DemonGen:
    def __init__(self, l,b,r,t, enemy_count):
        self.zone = {'l' : l, 'b' : b, 'r' : r,'t' : t}
        for _ in range(enemy_count):
            self.gen_boss()

    def draw(self): pass

    def gen(self):
        type = random.randrange(len(INFO))
        if type == 1:
            x, y = position_somewhere_outside_screen()
        else:
            x, y = position_within_bounds(self.zone)
        info = INFO[type]
        demon = info.clazz(type, x, y)
        if demon.is_on_obstacle():
            return
        world = gfw.top().world
        world.append(demon)

    def gen_boss(self):
        type = 3
        info = INFO[type]
        # x, y = 3771, 910 # 위치 지정해줘야함
        x, y = position_within_bounds(self.zone)
        demon = info.clazz(type, x, y)
        if demon.is_on_obstacle():
            return
        world = gfw.top().world
        world.append(demon)


    def update(self):
        pass
        # world = gfw.top().world
        # if world.count_at(world.layer.enemy) == 0:
        #     print(f"남은 적 없음")
        