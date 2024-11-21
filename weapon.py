from pico2d import *
from gfw import *
import time

def make_rect(size, idx):
    x, y = idx % 100, idx // 100
    return (x * (size ) , y * (size ), size, size)

def make_rects(size, idxs):
    return list(map(lambda idx: make_rect(size, idx), idxs))


class Knight(SheetSprite):
    JUMP_POWER = 1000
    HURT_DURATION = 0.5
    ROLLING_DURATION = 0.6
    MOVE_SPEED = 200  # 이동 속도 (픽셀/초)
    ROLL_SPEED = 400  # 구르기 시 이동 속도 (픽셀/초)

    def __init__(self, info):
        super().__init__(f'res/gun/AK47_Sprite.png', 160, 500, 10)
        self.states = build_states(info)
        self.running = True
        self.width, self.height = info["size"], info["size"]
        self.mag = 0.8  # 크기 배율을 설정
        self.dy = 0
        self.time = 0
        self.flip = True  # 이미지 반전 상태를 저장
        self.roll_dx, self.roll_dy = 0, 0  # 구르기 시 이동 방향
        self.key_state = {SDLK_w: False, SDLK_a: False, SDLK_s: False, SDLK_d: False}

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
         # 좌우 반전 여부에 따라 그리기
        flip_scale = -1 if self.flip else 1
        self.image.clip_composite_draw(
            l, b, w, h,  # 클립 영역
            0,  # 회전 각도
            'h',  # 축을 기준으로 뒤집기 (h는 수평 반전)
            self.x, self.y,  # 그려질 위치
            self.mag * w * flip_scale, self.mag * h  # 크기 (flip_scale로 반전 적용)
        )

if __name__ == '__main__':
    open_canvas()
    close_canvas()
