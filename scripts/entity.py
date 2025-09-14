import pygame
from scripts.Engine import Entity, Timer


class HurtableEntity(Entity):
    def __init__(self, x, y, width, height, vel, jump_height, gravity, health, anim_obj=None, hurt_time=0.3):
        super().__init__(x, y, width, height, vel, jump_height, gravity, anim_obj)
        self.health = health

        self.hurt = False
        self.hurt_time = hurt_time
        self.hurt_display_count = 0
        self.hurt_timer = Timer(self.hurt_time)
        self.alive = True
    
    def damage(self, dmg, cause = None):
        if not self.hurt:
            self.health -= dmg
            if self.health <= 0:
                self.health = 0
                self.alive = False

            self.hurt = True
            self.hurt_timer.set()
    
    def update(self):
        self.hurt_timer.update()

        if self.hurt_timer.timed_out():
            self.hurt = False
