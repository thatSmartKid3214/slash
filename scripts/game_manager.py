import pygame
import json
import math
import time
import scripts.Engine as E

from scripts.player import Player
from scripts.misc import Coin
from scripts.weapon import *
from scripts.enemy import *

TILESIZE = 16
LEVEL_UP = 300

class LevelInfo:
    def __init__(self):
        self.current_level = ""
        self.coins = 0
        self.enemies_killed = 0
        self.play_time = 0
        self.exp_gained = 0

    def reset(self):
        self.current_level = ""
        self.coins = 0
        self.enemies_killed = 0
        self.play_time = 0
    
    def set_level(self, level):
        self.current_level = level

    def save_info(self):
        pass

class GameManager:
    def __init__(self, game):
        self.game = game
        self.win_surf = self.game.window.get_display()

        self.width_ratio = self.game.window.win_disp_width_ratio()
        self.height_ratio = self.game.window.win_disp_height_ratio()
        
        self.cam = E.Camera()
        self.dt = 0
        self.now = 0
        self.prev_time = 0

        self.save_data = {}
        self.level_info = LevelInfo()

        self.level = {}
        self.tiles = {}
        self.camera_bounds = []
        self.current_level = 1

        self.render_layers = ["background", "decor", "tiles", "enemies", "player", "attacks", "foreground"]

        self.slashes = []
        self.enemies = []
        self.projectiles = []
        self.particles = []
        self.coins = []


        self.battle_rooms = []
        self.in_battle = False
        self.battle_enemy_count = 0
        self.wave_count = 0
        self.current_wave = 0
        self.current_battle_room = -1

        self.spawn_pos = [0, 0]
        self.load_level("data/levels/debug2.lvl")
        self.player = Player(self, self.spawn_pos[0], self.spawn_pos[1], TILESIZE, TILESIZE, 3.4, 7.5, 0.32, 100)
        self.player.animation = self.game.assets.create_animation_object("player")

        weapon = Weapon(self.game.assets.get_image("worn katana"), self.game.assets.get_weapon("worn katana"))
        self.player.weapon = weapon

        # Debug stuff
        self.debug_font = pygame.font.SysFont("Verdana", 15, True)
    

    def begin_battle(self, battle_room):
        self.in_battle = True
        self.battle_enemy_count = len(battle_room["enemies"][self.current_wave])
        self.wave_count = int(battle_room["wave_count"])

        for exit in battle_room["exits"]:
            self.tiles[exit[1]] = exit[0]

        for enemy in battle_room["enemies"][self.current_wave]:
            if enemy[1] == "drone":
                e = Drone(self, enemy[0][0], enemy[0][1], TILESIZE*2, TILESIZE*2, self.game.assets.get_image("drone"))
                e.battle_enemy = True
                self.enemies.append(e)

    def end_battle(self, battle_room):
        self.in_battle = False
        self.wave_count = 0
        self.current_wave = -1
        self.current_battle_room = -1

        for exit in battle_room["exits"]:
            del self.tiles[exit[1]]

    def load_level(self, level):
        exclude_list = ["tree 1", "tree 2"]

        self.level_info.set_level(level.split("/")[-1].split(".")[0])

        with open(level) as file:
            data = json.load(file)
            file.close()

        self.level = data["level"]

        for tile_id in self.level["tiles"]:
            tile = self.level["tiles"][tile_id]
            if tile[1] not in exclude_list:
                self.tiles[tile_id] = pygame.Rect(tile[2][0]*TILESIZE, tile[2][1]*TILESIZE, TILESIZE, TILESIZE)

        self.bounds = [data["bounds"]["left"], data["bounds"]["top"], data["bounds"]["right"], data["bounds"]["bottom"]]

        for obj in data["objects"]:
            # do stuff
            if obj["name"] == "Spawn":
                self.spawn_pos = [obj["rect"][0], obj["rect"][1]]
            
            if obj["name"] == "Dummy":
                self.enemies.append(Dummy(self, obj["rect"][0], obj["rect"][1], TILESIZE*2, TILESIZE*2, self.game.assets.create_animation_object("dummy")))

            if obj["name"] == "drone":
                self.enemies.append(Drone(self, obj["rect"][0], obj["rect"][1], TILESIZE*2, TILESIZE*2, self.game.assets.get_image("drone")))
            
            if obj["name"] == "BattleRoom":
                room = {"rect": pygame.Rect(obj["rect"]), "exits": [], "enemies": [], "wave_count": int(obj["properties"]["waves"])}
                for exit in obj["properties"]["exits"].split(","):
                    for _obj in data["objects"]:
                        if _obj["name"] == exit:
                            room["exits"].append([pygame.Rect(_obj["rect"]), exit])
                
                for i, waves in enumerate(obj["properties"]["enemy_ids"].split(";")):
                    room["enemies"].append([])
                    for enemy_id in waves.split(","):
                        for _obj in data["objects"]:
                            if _obj["name"] == enemy_id:
                                room["enemies"][i].append([_obj["rect"], _obj["properties"]["enemy"]])
                
                self.battle_rooms.append(room)
        
    def get_tiles_near_object(self, pos, tile_radius):
        tile_x = int(pos[0]/TILESIZE)
        tile_y = int(pos[1]/TILESIZE)

        tiles = []
        for i in range(-tile_radius, tile_radius+1):
            for j in range(-tile_radius, tile_radius+1):
                tile_id = f"{tile_x+j}/{tile_y+i}"

                if tile_id in self.tiles:
                    tiles.append(self.tiles[tile_id])
                
        
        if self.in_battle:
            for exit in self.battle_rooms[self.current_battle_room]["exits"]:
                tiles.append(self.tiles[exit[1]])
        
        return tiles

    def manage_states(self):
        pass

    def play_game(self):
        self.game.window.fill((127, 127, 127))
        self.game.clock.tick(self.game.FPS)

        self.now = time.time()
        self.dt = self.now-self.prev_time
        self.prev_time = self.now

        self.level_info.play_time += self.dt

        mouse_pos = pygame.mouse.get_pos()
        display_pos = [mouse_pos[0]/self.width_ratio, mouse_pos[1]/self.height_ratio]

        self.cam.update(self.player.rect, self.win_surf, 1, 1.0)

        pos = E.world_to_screen(self.player.rect.center, self.cam.scroll)
        angle = E.angle_from_points(pos, display_pos)
        angle_deg = math.degrees(angle)

        cam_view = [self.cam.scroll[0], self.cam.scroll[1], self.cam.scroll[0]+self.win_surf.get_width(), self.cam.scroll[1]+self.win_surf.get_height()]

        if self.game.joystick != None:
            axis = self.game.joystick.get_axis(0)

            if axis > -0.08 and axis < 0.08:
                axis = 0
                self.player.left = False
                self.player.right = False

            if axis != 0:
                if axis > 0:
                    self.player.right = True
                    self.player.left = False
                if axis < 0:
                    self.player.left = True
                    self.player.right = False
        

        for event in self.game.window.events:
            if event.type == pygame.QUIT:
                self.game.quit()
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_a:
                    self.player.left = True
                if event.key == pygame.K_d:
                    self.player.right = True
                if event.key == pygame.K_SPACE:
                    self.player.jump()
                if event.key == pygame.K_v:
                    if self.player.speed_boost:
                        self.player.leap()
                if event.key == pygame.K_c:
                    self.player.roll()
                if event.key == pygame.K_f:
                    self.player.perform_dash_slash()
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 3:
                    if self.player.num_throwables > 0:
                        self.player.throw_projectile(self.projectiles, angle)
            
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_a:
                    self.player.left = False
                if event.key == pygame.K_d:
                    self.player.right = False
            
            if event.type == pygame.JOYDEVICEADDED:
                self.game.joystick = pygame.joystick.Joystick(event.device_index)

            if event.type == pygame.JOYDEVICEREMOVED:
                self.game.joystick = None
            
            if event.type == pygame.JOYBUTTONDOWN:
                if event.button == 0:
                    self.player.jump()

        self.player.update(self.get_tiles_near_object([self.player.rect.x, self.player.rect.y], 3))

        self.player.attacking = False
        if pygame.mouse.get_pressed()[0]:
            self.player.attacking = True
            self.player.weapon.attack(self.player.rect.center, -angle_deg+random.randint(-3, 3), self.player, self.slashes, display_pos[0]<pos[0])
        
        for i, b_room in enumerate(self.battle_rooms):
            if self.player.rect.colliderect(b_room["rect"]) and not self.in_battle:
                self.begin_battle(b_room)
                self.current_wave = 0
                self.current_battle_room = i
        
        if self.in_battle and self.battle_enemy_count <= 0 and self.current_battle_room != -1:
            if self.current_wave >= self.wave_count-1:
                self.end_battle(self.battle_rooms.pop(self.current_battle_room))
            else:
                self.current_wave += 1
                self.begin_battle(self.battle_rooms[self.current_battle_room])


        # Draw level
        for layer in self.render_layers:
            if layer == "player":
                self.player.draw(self.win_surf, self.cam.scroll)
                if not self.player.attacking:
                    self.player.weapon.draw(self.player.rect.center, -angle_deg, self.win_surf, self.cam.scroll)

                self.player.weapon.update()

                for i, coin in sorted(enumerate(self.coins), reverse=True):
                    coin.update(self.get_tiles_near_object([coin.rect.x, coin.rect.y], 1))
                    coin.draw(self.win_surf, self.cam.scroll)

                    if self.player.rect.colliderect(coin.rect):
                        self.level_info.coins += 1
                        self.coins.pop(i)


                #state = self.debug_font.render(self.player.state, False, (0, 0, 0))
                #self.win_surf.blit(state, (self.player.rect.x-self.cam.scroll[0], self.player.rect.y - self.cam.scroll[1] - 15))
            elif layer == "enemies":
                for i, enemy in sorted(enumerate(self.enemies), reverse=True):
                    enemy.update(self.player, self.get_tiles_near_object([enemy.rect.x, enemy.rect.y], 2))

                    if ((enemy.rect.x+enemy.rect.width+1) > cam_view[0] and enemy.rect.x < cam_view[2]) and ((enemy.rect.y+enemy.rect.height+1) > cam_view[1] and enemy.rect.y < cam_view[3]):
                        enemy.draw(self.win_surf, self.cam.scroll)

                    if not enemy.alive:
                        enemy = self.enemies.pop(i)

                        if enemy.battle_enemy:
                            self.battle_enemy_count -= 1
                        
                        for i in range(enemy.coin_drop):
                            self.coins.append(Coin(pygame.Surface((8,8)), enemy.rect.x, enemy.rect.y, [random.randint(-2, 2), random.randint(-5, 1)]))
                        
                        self.level_info.enemies_killed += 1
                        self.level_info.exp_gained += 1

                        if self.level_info.enemies_killed % 4 == 0:
                            self.player.boost()

            elif layer == "attacks":
                for i, slash in sorted(enumerate(self.slashes), reverse=True):
                    slash.draw(self.win_surf, self.cam.scroll)

                    for enemy in self.enemies:
                        slash.handle_collision(enemy)

                    if not slash.active:
                        self.slashes.pop(i)
                
                for i, projectile in sorted(enumerate(self.projectiles), reverse=True):
                    projectile.update(self.get_tiles_near_object([projectile.rect.x, projectile.rect.y], 2))

                    projectile.draw(self.win_surf, self.cam.scroll)

                    if not projectile.active:
                        self.projectiles.pop(i)
                        continue

                    if projectile.owner != self.player:
                        if self.player.rect.colliderect(projectile.rect) and not self.player.hurt and not self.player.rolling:
                            self.player.damage(projectile.dmg, projectile)
                            self.projectiles.pop(i)
                    else:
                        for e in self.enemies:
                            if e.rect.colliderect(projectile.rect):
                                e.damage(projectile.dmg, projectile)
                                self.projectiles.pop(i)
                                break
                    
            else:
                for tile_id in self.level[layer]:
                    tile = self.level[layer][tile_id]
                    pos = [tile[2][0]*TILESIZE, tile[2][1]*TILESIZE]

                    if tile[0] in ["tileset_green", "tileset_cherry"]:
                        if (pos[0] > cam_view[0]-TILESIZE-1 and pos[0] < cam_view[2]+1) and (pos[1] > cam_view[1]-TILESIZE-1 and pos[1] < cam_view[3]+1):
                            self.win_surf.blit(self.game.assets.get_tile(tile[0], tile[1]), (pos[0]-self.cam.scroll[0], pos[1]-self.cam.scroll[1]))
                    else:
                        img = self.game.assets.get_tile(tile[0], tile[1])
                        if (pos[0] > cam_view[0]-img.get_width()-1 and pos[0] < cam_view[2]+1) and (pos[1] > cam_view[1]-img.get_height()-1 and pos[1] < cam_view[3]+1):
                            self.win_surf.blit(img, (pos[0]-self.cam.scroll[0], pos[1]-self.cam.scroll[1]))
        
        text = self.debug_font.render(f"Coins: {self.level_info.coins}", False, (255, 255, 255))
        self.win_surf.blit(text, (self.win_surf.get_width()-text.get_width()*1.2, 5))

        text2 = self.debug_font.render(f"Health: {self.player.health}", False, (255, 255, 255))
        self.win_surf.blit(text2, (5, 5))

        text3 = self.debug_font.render(f"FPS: {int(self.game.clock.get_fps())}", False, (255, 255, 255))
        self.win_surf.blit(text3, (5, 20))

        self.game.window.update()
    
    def run(self):
        self.play_game()
