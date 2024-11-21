# sword.py
from weapon import Weapon  # 부모 클래스 Weapon을 import

class AK47(Weapon):
    def __init__(self, owner):
        super().__init__(owner, f'res/gun/AK47_Sprite.png', attack_speed=1.5, range=100, damage=25, fps=10)
        # 추가적인 속성 -> 나중에 추가
        #self.swing_sound = load_sound('sword_swing.wav')
        self.width, self.height = 96, 48

    def attack(self):
        super().attack()  # 부모의 attack 호출
        #self.swing_sound.play()  # 검 휘두를 때 사운드 재생
        print("AK47 attack executed!")
