from pico2d import *
from gfw import *
from weapon import *
from enemy import Demon, DemonGen
import time

def make_rect(size, idx):
    x, y = idx % 100, idx // 100
    return (x * (size ) , y * (size ), size, size)

def make_rects(size, idxs):
    return list(map(lambda idx: make_rect(size, idx), idxs))

STATE_IDLE,STATE_ROLLING,STATE_RUNNING, STATE_HURT = range(4)

IS_STAGE_ENTERING, IS_STAGE_ACTIVE, IS_STAGE_COMPLETE = range(3)

types = {
    "15x8": {
        "states": [
            {"rect": [600], "size": [100, 140]},  # 0행 0~6
            {"rect": [700, 701, 702, 703, 704, 705, 706], "size": [100, 140]},  # 0행 0~6
            {"rect": [600, 601, 602, 603], "size": [100, 140]},  # 1행 14, 15 -> (100, 101)
            {"rect": [400], "size": [100, 140]},  # 2행 16~18 -> (200, 201, 202)
        ]
    }

}

# 구역 정보 (좌표 범위 및 상태)
zones = {
    'zone1': {'range': ((1632, 1110), (2369, 1824)), 'status': IS_STAGE_ENTERING},
    'zone2': {'range': ((131, 1110), (919, 1824)), 'status': IS_STAGE_ENTERING},
    'zone3': {'range': ((3034, 1111), (3868, 1824)), 'status': IS_STAGE_ENTERING},
    'zone4': {'range': ((1630, 2511), (2368, 3222)), 'status': IS_STAGE_ENTERING},
    'zone5': {'range': ((3031, 2510), (3865, 3224)), 'status': IS_STAGE_ENTERING}
}

# StatesManager: 관리 및 애니메이션 관리
class StatesManager:
    def __init__(self, type_info, size):
        self.states = self._build_states(type_info, size)

    def _build_states(self, type_info, size):
        states = []
        type_data = types[type_info] if type_info in types else types["11x6"]
        for st in type_data["states"]:
            rects = make_rects(size, st["rect"])
            states.append((rects, st["size"]))
        return states

    def get_state_data(self, state):
        return self.states[state]

# ZoneManager: 영역 상태 관리
class ZoneManager:
    def __init__(self, zones, bg):
        self.zones = zones
        self.bg = bg
        # self.world = gfw.top().world


    def update_zone_status(self, x, y):
        for zone_name, zone_data in self.zones.items():
            (left, bottom), (right, top) = zone_data['range']
            if left <= x <= right and bottom <= y <= top:
                if zone_data['status'] == IS_STAGE_ENTERING:
                    zone_data['status'] = IS_STAGE_ACTIVE
                    world = gfw.top().world
                    # DemonGen 인스턴스 생성 및 참조 저장
                    gen_instance = DemonGen(left, bottom, right, top)
                    world.append(gen_instance, world.layer.controller)
                    print(f"{zone_name}에 도달했습니다! 상태: IS_STAGE_ACTIVE")

                    # 저장해둔 DemonGen 인스턴스를 zone_data에 추가하여 관리
                    zone_data['gen_instance'] = gen_instance

                elif zone_data['status'] == IS_STAGE_ACTIVE:
                    self.bg.set_collision_tiles({2, 43})
                    world = gfw.top().world
                    if world.count_at(world.layer.enemy) == 0:
                        zone_data['status'] = IS_STAGE_COMPLETE
                        # DemonGen 인스턴스 제거
                        if 'gen_instance' in zone_data:
                            gen_instance = zone_data['gen_instance']
                            world.remove(gen_instance, world.layer.controller)
                            del zone_data['gen_instance']  # 관리에서 제거
                        else:
                            print("Error: gen_instance not found.")

                elif zone_data['status'] == IS_STAGE_COMPLETE:
                    # 상태 완료 메시지가 한 번만 출력되도록 처리
                    if not zone_data.get('completed_flag', False):
                        print(f"{zone_name}은 이미 완료되었습니다.")
                        self.bg.set_collision_tiles({2})
                        zone_data['completed_flag'] = True  # 플래그 설정


class Knight(SheetSprite):
    JUMP_POWER = 1000
    HURT_DURATION = 0.5
    ROLLING_DURATION = 0.6
    MOVE_SPEED = 200  # 이동 속도 (픽셀/초)
    ROLL_SPEED = 400  # 구르기 시 이동 속도 (픽셀/초)

    def __init__(self, info, bg):
        super().__init__(f'res/knight_sheet.png', 80, 150, 8) #160, 500
        self.bg = bg
        self.running = True
        self.hp = 10
        self.mag = 0.6  # 크기 배율을 설정
        self.is_invincible = False
        self.time = 0
        self.flip = True  # 이미지 반전 상태를 저장
        self.roll_dx, self.roll_dy = 0, 0  # 구르기 시 이동 방향
        self.key_state = {SDLK_w: False, SDLK_a: False, SDLK_s: False, SDLK_d: False}

        # StatesManager: 애니메이션 관리
        self.state_manager = StatesManager(info["type"], info["size"])

        # ZoneManager: 구역 상태 관리
        self.zone_manager = ZoneManager(zones, bg)

        self.x = 2000  # 맵의 중앙에 캐릭터 위치
        self.y = 0

        self.set_state(STATE_IDLE)

        # 무기 추가
        self.weapon = Weapons(self)
        self.weapon.append(AK47(self))

    def handle_event(self, e):
        if e.type == SDL_KEYDOWN:
            if e.key in self.key_state:
                self.set_state(STATE_RUNNING)
                self.key_state[e.key] = True
            if e.key == SDLK_a:  # 왼쪽 이동: 반전
                self.flip = False
            elif e.key == SDLK_d:  # 오른쪽 이동: 정방향
                self.flip = True
            if e.key == SDLK_j:  # 구르기 실행
                self.is_invincible = True
                self.rolling()
            if e.key == SDLK_c:  # 모든 벽 이동할 수 있도록 함
                self.bg.set_collision_tiles({})
            if e.key == SDLK_k:  # 'k' 키를 누르면 총알 발사
                self.weapon.attack()

        elif e.type == SDL_KEYUP:
            if e.key in self.key_state:
                self.key_state[e.key] = False

    def check_idle(self):
        return not any(self.key_state.values())

    def update(self):
        ox, oy = self.x, self.y

        if self.check_idle():
            self.set_state(STATE_IDLE)

        # 현재 상태별 동작 처리
        if self.state == STATE_HURT:
            self.time += gfw.frame_time
            if self.time >= Knight.HURT_DURATION:
                self.set_state(STATE_RUNNING)

        elif self.state == STATE_ROLLING:
            self.x += self.roll_dx * gfw.frame_time
            self.y += self.roll_dy * gfw.frame_time

            # 구르기 애니메이션 종료 처리
            if self.current_index != self.get_anim_index():
                self.index += 1
            self.current_index = self.get_anim_index()
            if self.index == len(self.src_rects) - 1:  # 마지막 애니메이션 프레임
                self.set_state(STATE_RUNNING)
                self.is_invincible = False

        # 상태가 RUNNING일 때 처리
        elif self.state == STATE_RUNNING:
            dx, dy = 0, 0
            if self.key_state[SDLK_w]: dy += Knight.MOVE_SPEED * gfw.frame_time
            if self.key_state[SDLK_a]: dx -= Knight.MOVE_SPEED * gfw.frame_time
            if self.key_state[SDLK_s]: dy -= Knight.MOVE_SPEED * gfw.frame_time
            if self.key_state[SDLK_d]: dx += Knight.MOVE_SPEED * gfw.frame_time
            self.x += dx
            self.y += dy

        # 배경 충돌 체크
        if self.bg.collides_box(*self.get_bb()):
            self.x, self.y = ox, oy

        # ZoneManager를 사용해 구역 상태를 관리
        self.zone_manager.update_zone_status(self.x, self.y)

        self.y = clamp(self.bg.margin, self.y, self.bg.total_height() - self.bg.margin)

        # 화면 중앙에 주인공을 맞추기 위해 bg.x와 bg.y를 조정
        self.bg.x = self.x - self.bg.width // 2 - 400 
        self.bg.y = self.y - 200

        # 배경을 화면에 그리기
        self.bg.show(self.bg.x, self.bg.y)

    def rolling(self):
        self.roll_dx, self.roll_dy = 0, 0
        if self.key_state[SDLK_w]:
            self.roll_dy += Knight.ROLL_SPEED
        if self.key_state[SDLK_a]:
            self.roll_dx -= Knight.ROLL_SPEED
        if self.key_state[SDLK_s]:
            self.roll_dy -= Knight.ROLL_SPEED
        if self.key_state[SDLK_d]:
            self.roll_dx += Knight.ROLL_SPEED

        # 반전 상태 설정 (구르기 방향에 따라)
        if self.roll_dx < 0:
            self.flip = False   
        elif self.roll_dx > 0:
            self.flip = True


        self.index = 0
        self.current_index = self.get_anim_index()
        self.set_state(STATE_ROLLING)

    def hurt(self):
        self.time = 0
        self.set_state(STATE_HURT)

    def set_state(self, state):
        self.state = state
        # 상태에 맞는 애니메이션 데이터를 state_manager에서 가져옴
        self.src_rects, (self.width, self.height) = self.state_manager.get_state_data(state)
        self.frame_count = len(self.src_rects)

    def get_bb(self):
        foot = self.y - self.src_rects[0][3] // 2 * self.mag
        half_width = self.width // 2 * self.mag
        return (self.x - half_width, foot, self.x + half_width, foot + self.height * self.mag)

    def draw(self):
        if self.state == STATE_ROLLING:
            pass
        else:
            self.index = self.get_anim_index()
        l, b, w, h = self.src_rects[self.index]
        
        # 좌표를 배경의 스크린 좌표로 변환하여 사용
        screen_pos = self.bg.to_screen(self.x, self.y)

        # 좌표 출력
        # print(f"World Position: (x: {self.x}, y: {self.y})")
        # print(f"Screen Position: {screen_pos}")

        # 좌우 반전 여부에 따라 그리기
        flip_scale = -1 if self.flip else 1

        self.image.clip_composite_draw(l, b, w, h, 0, 'h', *screen_pos, self.mag * w * flip_scale, self.mag * h)   

if __name__ == '__main__':
    open_canvas()
    knight_info = {
        "id": "1",
        "name": "Bandit Knight",
        "type": "15x8",  # The type to use for this knight
        "size": 366
    }
    knight = Knight(knight_info)
    close_canvas()
