from pico2d import *
from gfw import *
import time

def make_rect(size, idx):
    x, y = idx % 100, idx // 100
    return (x * (size + 2) + 2, y * (size + 2) + 2, size, size)

def make_rects(size, idxs):
    return list(map(lambda idx: make_rect(size, idx), idxs))

STATE_ROLLING,STATE_RUNNING, STATE_HURT = range(3)

# JSON 대신 하드코딩된 데이터
types = {
    "15x8": {
        "states": [
            {"rect": [0, 1, 2, 3, 4, 5, 6], "size": [200, 210]},  # 0행 0~6
            {"rect": [100, 101], "size": [160, 180]},  # 1행 14, 15 -> (100, 101)
            {"rect": [200, 201, 202], "size": [250, 240]},  # 2행 16~18 -> (200, 201, 202)
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

    def __init__(self, info):
        super().__init__(f'res/knight_sheet.png', 160, 500, 10)
        self.states = build_states(info)
        self.running = True
        self.width, self.height = info["size"], info["size"]
        self.mag = 1.0  # 크기 배율을 설정
        self.dy = 0
        self.set_state(STATE_RUNNING)

    def handle_event(self, e):
        if e.type == SDL_KEYDOWN:
            if e.key == SDLK_w:
                self.move()
            elif e.key == SDLK_a:
                self.move_down_from_floor()
            elif e.key == SDLK_s:
                self.slide(True)
            elif e.key == SDLK_d:
                self.toggle_mag()

    def update(self):
        if self.state == STATE_HURT:
            self.time += gfw.frame_time
            if self.time >= Knight.HURT_DURATION:
                self.set_state(STATE_RUNNING)

        elif self.state == STATE_ROLLING:
            self.dy -= self.GRAVITY * gfw.frame_time
            self.y += self.dy * gfw.frame_time

        elif self.state == STATE_RUNNING:
            # no floor detection, just check for falling
            self.set_state(STATE_RUNNING)
            self.dy = 0

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
        index = self.get_anim_index()
        l, b, w, h = self.src_rects[index]
        self.image.clip_draw(l, b, w, h, self.x, self.y, self.mag * w, self.mag * h)


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
