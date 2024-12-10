from pico2d import *
from gfw import *
import time

class Bullet(Sprite):
    def __init__(self, player, fg_fname, power, speed, mag, is_splash_damage = False):
        super().__init__(fg_fname, -100, -100)
        self.player = player
        self.power = power
        self.speed = speed  # 총알 속도
        self.mag = mag  # 크기 배율을 설정
        self.angle = 0
        self.is_splash_damage = is_splash_damage
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

        # 바주카포라면 스플래시 데미지 추가
        if self.is_splash_damage:  # 바주카 총알인지 확인
            self.splash_damage()

        self.reset()
        return dead

    def splash_damage(self):
        SPLASH_RADIUS = 200  # 스플래시 반경
        SPLASH_DAMAGE = self.power * 0.2  # 스플래시 데미지 비율 (기본 데미지의 50%)

        world = gfw.top().world
        enemies = world.objects_at(world.layer.enemy)

        for enemy in enemies:
            if enemy.state == 'dead':
                continue

            # 거리 계산
            dist = math.sqrt((self.x - enemy.x) ** 2 + (self.y - enemy.y) ** 2)
            if dist <= SPLASH_RADIUS:  # 스플래시 반경 내에 있으면 데미지 적용
                enemy.hit(SPLASH_DAMAGE)

    def get_bb(self):
        r = 12 # radius
        return self.x-r, self.y-r, self.x+r, self.y+r

class Weapon(AnimSprite):
    COOL_TIME = 0.0

    def __init__(self, player, bullet_img, power, speed, bullet_count,bullet_mag, fps = 10, sprite_img=None, frame_count=1):
        self.frame_count = frame_count
        super().__init__(sprite_img, 0, 0, fps, self.frame_count)
        self.player = player
        self.bullets = []
        self.power = power
        self.speed = speed
        self.bullet_mag = bullet_mag
        self.cooldown = 0.0
        self.is_firing = False
        self.sprite_img = sprite_img
        self.image = load_image(sprite_img) if sprite_img else None
        self.width, self.height = (self.image.w // frame_count, self.image.h) if self.image else (0, 0)
        for _ in range(bullet_count):
            self.append_bullet(bullet_img)

    def append_bullet(self, bullet_img):
        bullet = Bullet(self.player, bullet_img, self.power, self.speed, self.bullet_mag)
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
    COOL_TIME = 0.3

    def __init__(self, player):
        super().__init__(player, f'res/gun/AK47_Bullet.png', power=30, speed=400, bullet_count=3, bullet_mag = 3, fps = 20, sprite_img=f'res/gun/AK47_Sprite.png', frame_count=12)

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
    COOL_TIME = 1.0

    def __init__(self, player):
        super().__init__(player, f'res/gun/Bazooka_Bullet.png', power=50, speed=200, bullet_count=1,bullet_mag = 2, fps = 25, sprite_img=f'res/gun/Bazooka_Sprite.png', frame_count=8)

    def append_bullet(self, bullet_img):
        bullet = Bullet(self.player, bullet_img, self.power, self.speed, self.bullet_mag, True)
        self.bullets.append(bullet)

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

class MP5(Weapon):
    COOL_TIME = 0.2

    def __init__(self, player):
        super().__init__(player, f'res/gun/MP5_Bullet.png', power=15, speed=400, bullet_count=5 ,bullet_mag = 3, fps = 20, sprite_img=f'res/gun/MP5_Sprite.png', frame_count=12)

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

class Revolver(Weapon):
    COOL_TIME = 0.7

    def __init__(self, player):
        super().__init__(player, f'res/gun/Revolver_Bullet.png', power=45, speed=400, bullet_count=6 ,bullet_mag = 3, fps = 30, sprite_img=f'res/gun/Revolver_Sprite.png', frame_count=10)

    def get_pos(self):
        if self.player.flip:
            self.x = self.player.x + 35
            self.y = self.player.y - 65
        else:
            self.x = self.player.x - 35
            self.y = self.player.y - 64

    def get_bullet_pos(self):
        if self.player.flip:
            return self.x + 35, self.y + 10
        else:
            return self.x - 35, self.y + 10


class Glock(Weapon):
    COOL_TIME = 0.2

    def __init__(self, player):
        super().__init__(player, f'res/gun/Glock_Bullet.png', power=10, speed=300, bullet_count=12 ,bullet_mag = 3, fps = 30, sprite_img=f'res/gun/Glock_Sprite.png', frame_count=12)

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
        self.player = player
        self.weapon_list = [AK47(player), Bazooka(player), MP5(player), Revolver(player), Glock(player)]  # 무기 추가
        self.current_weapon_index = 0  # 현재 장착된 무기의 인덱스
        self.weapon = self.weapon_list[self.current_weapon_index]  # 현재 장착된 무기

    def update(self):
        self.weapon.update()

    def draw(self):
        self.weapon.draw()

    def try_hit(self, obj):
        return self.weapon.try_hit(obj)

    def attack(self):
        self.weapon.fire()

    def switch_weapon(self):
        self.current_weapon_index = (self.current_weapon_index + 1) % len(self.weapon_list)
        self.weapon = self.weapon_list[self.current_weapon_index]