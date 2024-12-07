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

        demons = [d for d in world.objects_at(world.layer.enemy) if not d.state == 'dead']  # 살아있는 적만 필터링
        if not demons:  # 살아있는 적이 없다면
            return False

        self.x, self.y = weapon_x, weapon_y
        INF = float('inf')

        nearest = min(demons, key=lambda d: (d.x - self.x) ** 2 + (d.y - self.y) ** 2)
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

        dead = obj.hit(self.power)

        self.reset()
        return dead
    def get_bb(self):
        r = 12 # radius
        return self.x-r, self.y-r, self.x+r, self.y+r

class Weapon(AnimSprite):
    COOL_TIME = 0.0

    def __init__(self, player, bullet_img, power, speed, bullet_count, fps = 10, sprite_img=None, frame_count=1):
        self.frame_count = frame_count
        super().__init__(sprite_img, 0, 0, fps, self.frame_count)
        self.player = player
        self.bullets = []
        self.power = power
        self.speed = speed
        self.cooldown = 0.0
        self.is_firing = False
        self.sprite_img = sprite_img
        self.image = load_image(sprite_img) if sprite_img else None
        self.width, self.height = (self.image.w // frame_count, self.image.h) if self.image else (0, 0)
        for _ in range(bullet_count):
            self.append_bullet(bullet_img)

    def append_bullet(self, bullet_img):
        bullet = Bullet(self.player, bullet_img, self.power, self.speed)
        self.bullets.append(bullet)

    def get_pos(self):
        raise NotImplementedError("get_pos() must be implemented in subclasses")

    def get_bullet_pos(self):
        raise NotImplementedError("get_bullet_pos() must be implemented in subclasses")

    def fire(self):
        if self.cooldown > 0:
            return
        for b in self.bullets:
            if not b.valid:
                bullet_x, bullet_y = self.get_bullet_pos()
                fired = b.fire(bullet_x, bullet_y)
                if fired:
                    self.cooldown = self.COOL_TIME
                    self.is_firing = True
                    self.created_on = time.time()
                return

    def update(self):
        if self.cooldown > 0:
            self.cooldown -= gfw.frame_time

        for b in self.bullets:
            if b.valid:
                b.update()

    def draw(self):
        if self.sprite_img:
            bg = self.player.bg
            self.get_pos()
            screen_pos = bg.to_screen(self.x, self.y)

            index = 0
            if self.is_firing:
                index = self.get_anim_index()
                if index ==  self.frame_count - 1:
                    self.is_firing = False

            flip_scale = '' if self.player.flip else 'h'
            self.image.clip_composite_draw(index * self.width, 0, self.width, self.height, 0, flip_scale, *screen_pos, self.width, self.height)

        for b in self.bullets:
            if b.valid:
                b.draw()

    def try_hit(self, obj):
        for b in self.bullets:
            if b.valid and b.try_hit(obj):
                return True
        return False


class AK47(Weapon):
    COOL_TIME = 0.1

    def __init__(self, player):
        super().__init__(player, f'res/gun/AK47_Bullet.png', power=25, speed=400, bullet_count=1, fps = 10, sprite_img=f'res/gun/AK47_Sprite.png', frame_count=12)

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


class Bazooka(Weapon):
    COOL_TIME = 0.1

    def __init__(self, player):
        super().__init__(player, f'res/gun/Bazooka_Bullet.png', power=40, speed=200, bullet_count=6, fps = 10, sprite_img=f'res/gun/Bazooka_Sprite.png', frame_count=8)

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