import pygame
import random

import scripts.Engine as E
from scripts.assets import frame_times
from scripts.entity import HurtableEntity
from scripts.projectile import *
from scripts.weapon import *

TILESIZE = 16

class Player(HurtableEntity):
    def __init__(self, game, x, y, width, height, vel, jump_height, gravity, health):
        super().__init__(x, y, width, height, vel, jump_height, gravity, health, hurt_time=0.4)

        self.game = game
        

        self.attacking = False
        self.flip = False
        self.weapon = None

        self.max_vel_y = 7
        self.jump_count = 0
        self.max_jumps = 1
        self.grounded = False
        self.retardation = 0.2
        self.state = "idle"

        self.on_wall = False
        self.wall_jumping = False
        self.wall_jump_timer = E.Timer(0.28)
        self.wall_jump_speed = self.vel
        self.direction = 1

        self.speed_boost = False
        self.slowing_down = False
        self.big_jump = False
        self.leaping = False
        self.leap_angle = 0
        self.max_leap_angle = 135
        self.rolling = False
        self.speed_multiplier = 2.3
        self.speed_boost_timer = E.Timer(24, self.stop_boost)

        self.ability_active = False
        self.current_ability = ""
        self.ability_timer = E.Timer(0)

        self.bounces = 0 # For the death animation
        self.death_index = 1

        self.num_throwables = 6
        self.throw_timer = E.Timer(0.05)
        self.can_throw = True
        self.projectile_data = {}

    def boost(self):
        self.speed_boost = True
        self.wall_jump_timer.set_cooldown(0)
        self.animation.set_frame_duration("run", 0.05)
        self.speed_boost_timer.set()
    
    def perform_dash_slash(self):
        self.ability_active = True
        self.current_ability = "dash_slash"
        self.ability_timer.set_cooldown(0.4)
        self.ability_timer.set()
        if self.flip:
            direction = -1
            angle = -180
        else:
            direction = 1
            angle = 0
        
        # Create Slash
        slash = Slash(self, self.weapon.dmg*2, 0, 15, self.flip, self.rect.centerx+(direction*TILESIZE*3), self.rect.centery, 120, 40, 0.5, 0, 0, 9, (self.weapon.slash_info["color"]), 30, angle, cutout_radius=26, cutout_center=[21, 18])
        self.game.slashes.append(slash)
        
        self.movement[0] = 5*direction
        self.vel_y = 0

    def throw_projectile(self, projectile_list, angle):
        if self.can_throw:
            surf = pygame.Surface((8,8))
            surf.fill((0, 0, 255))
            p = Projectile(surf, self, 2, self.rect.centerx, self.rect.centery, 8, 8, 8, angle)

            projectile_list.append(p)
            self.throw_timer.set()
            self.can_throw = False
            self.num_throwables -= 1
    
    def stop_boost(self):
        self.speed_boost = False
        self.wall_jump_timer.set_cooldown(0.25)
        self.animation.set_frame_duration("run", frame_times["player"]["run"])

    def jump(self):

        if self.leaping or self.rolling:
            return
        
        if not self.on_wall:
            # The first jump should be when the player is grounded
            if self.jump_count == 0:
                if not self.grounded:
                    return

            if self.jump_count >= 0 and self.jump_count < self.max_jumps:
                if not self.slowing_down:
                    self.grounded = False
                    self.vel_y = -self.jump_height
                    self.jump_count += 1
                    self.state = "jump"
                else:
                    if abs(self.movement[0] < self.vel*self.speed_multiplier*0.6):
                        self.grounded = False
                        self.vel_y = -self.jump_height*0.85
                        self.jump_count = self.max_jumps
                        self.big_jump = True

                        self.animation.set_loop(False)
                        self.slowing_down = False
                        self.state = "backflip"
                        
                        if self.movement[0] > 0:
                            self.movement[0] = -self.vel*0.35
                            self.flip = False
                        else:
                            self.movement[0] = self.vel*0.35
                            self.flip = True
                    else:
                        self.grounded = False
                        self.vel_y = -self.jump_height
                        self.jump_count += 1
                        self.state = "jump"

        else:
            if not self.speed_boost:
                self.movement[0] = self.wall_jump_speed*self.direction
                self.vel_y = -4.7
                self.jump_count = self.max_jumps - 1
            else:
                self.movement[0] = self.wall_jump_speed*self.speed_multiplier*self.direction
                self.vel_y = -4.4
                self.jump_count = self.max_jumps
            
            self.state = "jump"

            self.wall_jumping = True    
            self.wall_jump_timer.set() 
    
    def leap(self):
        
        if not self.grounded or self.rolling:
            return

        if self.speed_boost and not self.leaping:
            self.vel_y = -4
            speed = self.vel * self.speed_multiplier
            if self.flip:
                self.movement[0] = -speed
            else:
                self.movement[0] = speed

            
            self.slowing_down = False

            self.leaping = True
            if self.flip:
                self.leap_angle = 60
            else:
                self.leap_angle = -60
        
    def roll(self):
        if not self.rolling:
            self.rolling = True
            self.slowing_down = False
            self.state = "roll"
            self.animation.set_loop(False)
            if self.flip:
                self.movement[0] = -self.vel*1.3
            else:
                self.movement[0] = self.vel*1.3
            
            self.vel_y = 1

    def move(self, tiles):
        if self.alive:
            speed_mult = 1.0
            if self.speed_boost:
                speed_mult = self.speed_multiplier
            
            if self.leaping:
                if self.flip:
                    self.leap_angle += 1
                    if self.leap_angle > self.max_leap_angle:
                        self.leap_angle = self.max_leap_angle
                else:
                    self.leap_angle -= 1
                    if self.leap_angle < -self.max_leap_angle:
                        self.leap_angle = -self.max_leap_angle

            if  not self.ability_active:
                if not (self.big_jump or self.leaping or self.rolling):
                    if not (self.wall_jumping or self.speed_boost):
                        self.slowing_down = False
                        if self.left:
                            self.movement[0] = -self.vel * speed_mult
                            self.flip = True
                            if self.grounded:
                                self.state = "run"
                        if self.right:
                            self.movement[0] = self.vel * speed_mult
                            self.flip = False
                            if self.grounded:
                                self.state = "run"
                    elif (not self.wall_jumping) and self.speed_boost:
                        acceleration = 0.3
                        self.slowing_down = False
                        if self.left:
                            self.flip = True
                            if self.movement[0] > 0:
                                acceleration /= 3
                                self.slowing_down = True

                            self.movement[0] -= acceleration
                            self.state = "run"
                            if self.movement[0] <= -self.vel * speed_mult:
                                self.movement[0] = -self.vel * speed_mult
                        if self.right:
                            self.flip = False
                            if self.movement[0] < 0:
                                acceleration /= 3
                                self.slowing_down = True
                            self.movement[0] += acceleration
                            self.state = "run"
                            if self.movement[0] >= self.vel * speed_mult:
                                self.movement[0] = self.vel * speed_mult
                    
                    self.vel_y += self.gravity
                    if self.vel_y >= self.max_vel_y:
                        self.vel_y = self.max_vel_y
                else:
                    if self.movement[1] > self.max_vel_y*0.7:
                        self.big_jump = False
                    
                    self.vel_y += self.gravity*0.65
                    if self.vel_y >= self.max_vel_y:
                        self.vel_y = self.max_vel_y
            
            if self.on_wall and self.vel_y > 1:
                self.vel_y = 1.4

            self.movement[1] = self.vel_y

            if self.wall_jumping:
                if self.wall_jump_timer.timed_out():
                    self.wall_jumping = False
            
            if self.movement[0] == 0 and self.grounded:
                self.state = "idle"

            self.collisions = self.physics_obj.movement(self.movement, tiles, 1.0)
            self.rect.x = self.physics_obj.rect.x
            self.rect.y = self.physics_obj.rect.y

            if self.collisions["bottom"]:
                self.vel_y = 1
                self.jump_count = 0
                self.grounded = True

                if not self.rolling:
                    self.animation.set_loop(True)

                self.big_jump = False

                if self.leaping:
                    self.leaping = False
                    temp_vel_y = self.vel_y
                    self.roll()
                    self.vel_y = temp_vel_y
                    self.animation.set_frame(2)
            else:
                self.grounded = False

            if self.collisions["top"]:
                self.vel_y = 1

            if (self.collisions["left"] or self.collisions["right"]):
                if not self.grounded and not self.rolling:
                    self.on_wall = True
                    self.state = "wall_slide"
                
                if self.speed_boost and self.grounded:
                    self.movement[0] *= 0.2

                if self.leaping:
                    self.leaping = False
                    temp_vel_y = self.vel_y
                    self.roll()
                    self.vel_y = temp_vel_y
                    self.animation.set_frame(2)
            else:
                self.on_wall = False
                if not self.grounded and not self.rolling and self.state != "backflip":
                    self.state = "jump"

            if self.collisions["left"]:
                self.direction = 1
                if self.on_wall and not self.rolling:
                    self.flip = False
            
            if self.collisions["right"]:
                self.direction = -1
                if self.on_wall and not self.rolling:
                    self.flip = True
            
            if not (self.wall_jumping or self.big_jump or self.leaping or self.rolling):
                if self.movement[0] < 0:
                    self.movement[0] = min(0, self.movement[0] + self.retardation)
                if self.movement[0] > 0:
                    self.movement[0] = max(0, self.movement[0] - self.retardation)
            
            self.wall_jump_timer.update()
        else:

            self.vel_y += self.gravity
            if self.vel_y > self.max_vel_y:
                self.vel_y = self.max_vel_y
            
            self.movement[1] = self.vel_y

            self.collisions = self.physics_obj.movement(self.movement, tiles, 1.0)
            self.rect.x = self.physics_obj.rect.x
            self.rect.y = self.physics_obj.rect.y

            if self.collisions["bottom"]:
                if self.bounces < 2:
                    self.vel_y = random.randint(-4, -3)
                    self.bounces += 1
                    
                    self.death_index = random.randint(1, 3) 
                else:
                    self.vel_y = 1
                    self.death_index = 4
            
            if self.movement[0] < 0:
                self.movement[0] = min(0, self.movement[0] + self.retardation*0.35)
            if self.movement[0] > 0:
                self.movement[0] = max(0, self.movement[0] - self.retardation*0.35)
    
    def die(self):
        if self.alive:
            self.death_index = random.randint(1, 3)
            self.animation.set_loop(False)

            if self.flip:
                self.movement[0] = random.randint(4, 6)
            else:
                self.movement[0] = random.randint(-6, -4)

            self.vel_y = random.randint(-4, -3)
            self.state = "death"

            super().die()

    def draw(self, surf, scroll=[0, 0]):
        if self.alive:
            if self.slowing_down and self.grounded:
                self.state = "slow_down"
                if self.movement[0] > 0:
                    self.flip = False
                elif self.movement[0] < 0:
                    self.flip = True
            
            if self.big_jump:
                self.state = "backflip"

            self.image = self.animation.animate(self.state, True)
            
            if self.leaping:
                self.animation.set_frame(0)
                self.image = self.animation.animate("idle", True)

            if self.animation.end_of_anim and self.state == "roll":
                self.animation.set_loop(True)
                self.state = "idle"
                self.rolling = False
                self.animation.end_of_anim = False
                if not self.speed_boost:
                    self.movement[0] = 0
                else:
                    if self.movement[0] < 0:
                        self.movement[0] = -self.vel*self.speed_multiplier*0.45
                    else:
                        self.movement[0] = self.vel*self.speed_multiplier*0.45
        else:
            self.state = "death"
            #print(self.death_index)
            self.animation.set_frame(self.death_index)
            self.image = self.image = self.animation.animate(self.state, True)
    
        offset_x = 0
        if self.state == "wall_slide" and self.flip:
            offset_x = 2
        
        if not self.leaping:
            E.perfect_outline(pygame.transform.flip(self.image, self.flip, False), surf, (self.rect.x+offset_x-scroll[0],self.rect.y-scroll[1]-3), (20, 20, 20))
            surf.blit(pygame.transform.flip(self.image, self.flip, False), (self.rect.x+offset_x-scroll[0],self.rect.y-scroll[1]-3))
        else:
            E.perfect_outline(pygame.transform.rotate(pygame.transform.flip(self.image, self.flip, False), self.leap_angle), surf, (self.rect.x+offset_x-scroll[0],self.rect.y-scroll[1]-3), (20, 20, 20))
            surf.blit(pygame.transform.rotate(pygame.transform.flip(self.image, self.flip, False), self.leap_angle), (self.rect.x+offset_x-scroll[0],self.rect.y-scroll[1]-3))

    def update(self, tiles):
        super().update()
        self.move(tiles)
        self.speed_boost_timer.update()
        self.throw_timer.update()
        self.ability_timer.update()

        if self.throw_timer.timed_out():
            self.can_throw = True

        if self.ability_timer.timed_out():
            self.ability_active = False
            self.current_ability = ""


