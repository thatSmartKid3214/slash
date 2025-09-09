import pygame
import random
from scripts.Engine import blit_center, Timer
from scripts.vfx import SlashVFX


class Slash(SlashVFX):
    def __init__(self, owner, damage, crit, lifetime, x, y, width, height, speed, slash_size, slash_size_change, roll_down_speed, color, radius, angle, shape="circle"):
        super().__init__(x, y, width, height, speed, slash_size, slash_size_change, roll_down_speed, color, radius, angle, shape)

        self.owner = owner
        self.damage = damage
        self.is_crit = crit
        self.lifetime = lifetime
        self.hitboxes = []
    
    def set_hitboxes(self, hitboxes=[]):
        self.hitboxes = hitboxes

    def did_collide(self, entity_rect: pygame.Rect):
        pass

    def handle_collision(self, entity):
        pass

class Weapon:
    def __init__(self, image: pygame.Surface, data):
        surf = pygame.Surface((image.get_width()*2, image.get_height()))
        surf.blit(image, (image.get_width(), 0))
        surf.set_colorkey(image.get_colorkey())

        self.image = surf
        self.data = data

        self.dmg = data["damage"]
        self.crit_rate = data["crit_rate"]
        self.attack_cooldown = data["attack_cooldown"]
        self.can_attack = True
        self.cooldown_timer = Timer(self.attack_cooldown)

        self.slash_info = data["slash_info"]

    def attack(self, pos, angle, owner, slash_list: list):
        if self.can_attack:
            is_crit = random.random() < self.crit_rate
            slash = Slash(owner, self.dmg, is_crit, self.slash_info["lifetime"], pos[0], pos[1], random.randint(self.slash_info["width"][0], self.slash_info["width"][1]), random.randint(self.slash_info["height"][0], self.slash_info["height"][1]), self.slash_info["speed"], random.randint(self.slash_info["slash_size"][0], self.slash_info["slash_size"][1]), self.slash_info["slash_change_size"], self.slash_info["roll_down_speed"], self.slash_info["color"], self.slash_info["radius"], angle, self.slash_info["shape"])

            slash_list.append(slash)
            self.can_attack = False
            self.cooldown_timer.set()

    def draw(self, pos, angle, surf, scroll):
        blit_center(surf, pygame.transform.rotate(self.image, angle), [pos[0]-scroll[0], pos[1]-scroll[1]])

    def update(self):
        self.cooldown_timer.update()

        if self.cooldown_timer.timed_out():
            self.can_attack = True