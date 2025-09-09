import pygame
from scripts.Engine import blit_center
from vfx import SlashVFX

class Weapon:
    def __init__(self, image: pygame.Surface, damage, attack_rate, attack_cooldown, slash_color):
        self.image = image
        self.dmg = damage
        self.attack_rate = attack_rate
        self.attack_cooldown = attack_cooldown
        self.slash_color = slash_color

    def attack(self, pos, owner):
        pass

    def draw(self, surf, scroll):
        pass