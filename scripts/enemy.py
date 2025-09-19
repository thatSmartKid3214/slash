import pygame
import random

import scripts.Engine as E
from scripts.entity import HurtableEntity
from scripts.weapon import Slash
from scripts.misc import Coin
from scripts.projectile import *

vec2 = pygame.Vector2

class Enemy(HurtableEntity):
    def __init__(self, game, x, y, width, height, vel, jump_height, gravity, health, anim_obj=None, hurt_time=0.3):
        super().__init__(x, y, width, height, vel, jump_height, gravity, health, anim_obj, hurt_time)
        self.game = game

        self.attacking = False
        self.attack_timer = E.Timer(0, self.can_attack)
        self.flip = False

        self.max_vel_y = 7
        self.jump_count = 0
        self.max_jumps = 1
        self.grounded = False
        self.retardation = 0.2
        self.state = "idle"
        self.battle_enemy = False

        self.coin_drop = 0
        self.dmg = 0
        self.exp_gain = 0
    
    def can_attack(self):
        self.attacking = False

    def move(self, tiles):
        self.grounded = False
        if self.left:
            self.movement[0] = -self.vel
            self.flip = True
        if self.right:
            self.movement[0] = self.vel
            self.flip = False

        self.vel_y += self.gravity
        if self.vel_y > self.max_vel_y:
            self.vel_y = self.max_vel_y

        self.movement[1] = self.vel_y

        self.collisions = self.physics_obj.movement(self.movement, tiles, 1.0)
        self.rect.x = self.physics_obj.rect.x
        self.rect.y = self.physics_obj.rect.y

        if self.collisions["bottom"]:
            self.vel_y = 1
            self.grounded = True

        if self.collisions["top"]:
            self.vel_y = 1

    def run_ai(self, target):
        pass

    def update(self, target, tiles):
        super().update()
        self.run_ai(target)
        self.move(tiles)

        self.attack_timer.update()


class Drone(Enemy):
    def __init__(self, game, x, y, width, height, image):
        super().__init__(game, x, y, width, height, 0.7, 0, 0, 1, None, 0.1)

        self.image = image
        self.coin_drop = 5
        self.exp_gain = 2
        self.dmg = 2
        self.attack_timer.set_cooldown(3)
        self.attack_timer.set()
        self.attacking = True

        self.clear_to_attack = True

        self.area_rect = pygame.Rect(0, 0, 960, 960) # 60 tiles range

        self.area_rect.x = self.rect.x-self.area_rect.width/2
        self.area_rect.y = self.rect.y-self.area_rect.height/2

    def draw(self, surf, scroll):
        if not self.hurt:
            color = (255, 0, 0)
        else:
            color = (255, 255, 255)

        E.perfect_outline(self.image, surf, (self.rect.x-scroll[0], self.rect.y-scroll[1]), color)
        surf.blit(self.image, (self.rect.x-scroll[0], self.rect.y-scroll[1]))
        #pygame.draw.rect(surf, (0, 255, 0), (self.rect.x-scroll[0], self.rect.y-scroll[1], self.rect.width, self.rect.height), 1)

        if self.hurt:
            mask = pygame.mask.from_surface(self.image)
            img = mask.to_surface(unsetcolor=(0, 0, 0, 0), setcolor=(255, 255, 255, 255))
            surf.blit(img, (self.rect.x-scroll[0], self.rect.y-scroll[1]))
    
    def move(self, tiles):
        if len(E.collision_test(self.rect, tiles)) == 0:
            self.clear_to_attack = True
        else:
            self.clear_to_attack = False

    def run_ai(self, target):
        rect = target.rect

        if not self.area_rect.colliderect(rect):
            return

        target_pos = vec2(rect.centerx+random.randint(-10, 10), rect.centery)
        pos = vec2(self.rect.centerx, self.rect.centery)

        if E.dis_between_points_opt(target_pos, pos) <= pow(120, 2):
            target_pos.y -= 16*4

        dir = target_pos-pos
        dir = dir.normalize()

        if E.dis_between_points_opt(target_pos, pos) <= pow(150, 2) and self.rect.y < rect.y - 8:
            direction = 1
            if dir.x < 0:
                direction = -1

            self.attack(direction)

        dir *= self.vel

        self.rect.x += dir.x
        self.rect.y += dir.y

        self.area_rect.x = self.rect.x-self.area_rect.width/2
        self.area_rect.y = self.rect.y-self.area_rect.height/2
    
    def attack(self, direction):
        if not self.attacking and self.clear_to_attack:
            surf = pygame.Surface((10, 10))
            surf.fill((255, 0, 0))
            self.game.projectiles.append(PhysicsProjectile(surf, self, self.dmg, self.rect.centerx, self.rect.centery, 10, 10, 0.2, [2.7*direction, 1.2]))
            self.attack_timer.set()
            self.attacking = True


class Dummy(Enemy):
    def __init__(self, game, x, y, width, height, anim_obj):
        super().__init__(game, x, y, width, height, 0, 0, 0, 4000, anim_obj, 0.3)

        self.hurt_timer.set_callback(self.set_idle)
        self.animation.set_loop(False)

        self.coin_drop = 2100

    def set_idle(self):
        self.state = "idle"

    def draw(self, surf, scroll):
        self.image = self.animation.animate(self.state, True)
        self.image = pygame.transform.flip(pygame.transform.scale(self.image, (self.image.get_width()*2, self.image.get_height()*2)), self.flip, False)

        #E.perfect_outline(pygame.transform.scale(self.image, (self.image.get_width()*2, self.image.get_height()*2)), surf, (self.x-scroll[0], self.y-scroll[1]-14), (255, 0, 0))
        surf.blit(self.image, (self.x-scroll[0], self.y-scroll[1]-14))
        #pygame.draw.rect(surf, (0, 255, 0), (self.x-scroll[0], self.y-scroll[1], self.rect.width, self.rect.height), 1)
    
    def damage(self, dmg, cause = None):
        super().damage(dmg)
        if self.hurt:
            self.state = "hurt"

        if(type(cause) == Slash):
            self.flip = cause.flip






