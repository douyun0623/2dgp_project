from pico2d import *
from gfw import *
import time

def make_rect(size, idx):
    x, y = idx % 100, idx // 100
    return (x * (size ) , y * (size ), size, size)

def make_rects(size, idxs):
    return list(map(lambda idx: make_rect(size, idx), idxs))

STATE_ROLLING,STATE_RUNNING, STATE_HURT = range(3)

# JSON 대신 하드코딩된 데이터
types = {
    "15x8": {
        "states": [
            {"rect": [700, 701, 702, 703, 704, 705, 706], "size": [100, 140]},  # 0행 0~6
            {"rect": [600, 601, 602, 603], "size": [100, 140]},  # 1행 14, 15 -> (100, 101)
            {"rect": [400], "size": [100, 140]},  # 2행 16~18 -> (200, 201, 202)
        ]
    }

}

# Knight 타입을 객체로 정의
def build_states(info):
    states = []
    type = types[info["type"]] if info["type"] in types else types["11x6"]
    for st in type["states"]:
        rects = make_rects(info["size"], st["rect"])
        states.append((rects, st["size"]))
    return states


class Knight(SheetSprite):
    JUMP_POWER = 1000
    HURT_DURATION = 0.5
    ROLLING_DURATION = 0.6
    MOVE_SPEED = 200  # 이동 속도 (픽셀/초)
    ROLL_SPEED = 400  # 구르기 시 이동 속도 (픽셀/초)

    def __init__(self, info, bg):
        super().__init__(f'res/knight_sheet.png', 80, 150, 10) #160, 500
        self.bg = bg
        self.states = build_states(info)
        self.running = True
        self.width, self.height = info["size"], info["size"]
        self.mag = 0.6  # 크기 배율을 설정
        self.dy = 0
        self.time = 0
        self.flip = True  # 이미지 반전 상태를 저장
        self.roll_dx, self.roll_dy = 0, 0  # 구르기 시 이동 방향
        self.key_state = {SDLK_w: False, SDLK_a: False, SDLK_s: False, SDLK_d: False}

        
        self.x = 2000  # 맵의 중앙에 캐릭터 위치
        self.y = 0
       

        self.set_state(STATE_RUNNING)

    def handle_event(self, e):
        if e.type == SDL_KEYDOWN:
            if e.key in self.key_state:
                self.key_state[e.key] = True
            if e.key == SDLK_a:  # 왼쪽 이동: 반전
                self.flip = False
            elif e.key == SDLK_d:  # 오른쪽 이동: 정방향
                self.flip = True
            if e.key == SDLK_j:  # 구르기 실행
                self.rolling()

        elif e.type == SDL_KEYUP:
            if e.key in self.key_state:
                self.key_state[e.key] = False


    def update(self):

        ox, oy = self.x, self.y

        if self.state == STATE_HURT:
            self.time += gfw.frame_time
            if self.time >= Knight.HURT_DURATION:
                self.set_state(STATE_RUNNING)

         # 상태가 ROLLING일 때 처리
        elif self.state == STATE_ROLLING:
            # 구르기 시 이동
            self.x += self.roll_dx * gfw.frame_time
            self.y += self.roll_dy * gfw.frame_time

            # 구르기 애니메이션 종료 처리
            if self.current_index != self.get_anim_index():
                self.index += 1
            self.current_index = self.get_anim_index()
            if self.index == len(self.src_rects) - 1:  # 마지막 애니메이션 프레임
                self.set_state(STATE_RUNNING)

        # 상태가 RUNNING일 때 처리
        elif self.state == STATE_RUNNING:

            # 이동 처리
            dx, dy = 0, 0
            if self.key_state[SDLK_w]:  # 위쪽 이동
                dy += Knight.MOVE_SPEED * gfw.frame_time
            if self.key_state[SDLK_a]:  # 왼쪽 이동
                dx -= Knight.MOVE_SPEED * gfw.frame_time
            if self.key_state[SDLK_s]:  # 아래쪽 이동
                dy -= Knight.MOVE_SPEED * gfw.frame_time
            if self.key_state[SDLK_d]:  # 오른쪽 이동
                dx += Knight.MOVE_SPEED * gfw.frame_time

            self.x += dx
            self.y += dy

        if self.bg.collides_box(*self.get_bb()):
            self.x, self.y = ox, oy

        # # 배경과 연동: 캐릭터 좌표를 map 좌로 변환
        # self.x = clamp(self.bg.margin, self.x, self.bg.total_width() - self.bg.margin)
        self.y = clamp(self.bg.margin, self.y, self.bg.total_height() - self.bg.margin)
        # self.bg.show(self.x, self.y)

        # 배경과 연동: 캐릭터 좌표를 화면 좌표로 변환하여 항상 화면 중앙에 위치하도록 조정
        # screen_center_x = self.bg.width // 2  # 화면 중앙 X 좌표
        # screen_center_y = self.bg.height // 2  # 화면 중앙 Y 좌표

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
        self.src_rects, (self.width, self.height) = self.states[self.state]
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
        
        # self.image.clip_draw(l , b , w, h, self.x, self.y, self.mag * w, self.mag * h)
        
        # 좌표를 배경의 스크린 좌표로 변환하여 사용
        screen_pos = self.bg.to_screen(self.x, self.y)

        # 좌표 출력
        # print(f"World Position: (x: {self.x}, y: {self.y})")
        # print(f"Screen Position: {screen_pos}")

        # 좌우 반전 여부에 따라 그리기
        flip_scale = -1 if self.flip else 1

        self.image.clip_composite_draw(
            l, b, w, h,  # 클립 영역
            0,  # 회전 각도
            'h',  # 축을 기준으로 뒤집기 (h는 수평 반전)
            *screen_pos,  # 그려질 위치
            self.mag * w * flip_scale, self.mag * h  # 크기 (flip_scale로 반전 적용)
        )   

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
