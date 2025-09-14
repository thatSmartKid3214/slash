import pygame
import json
import os
import scripts.Engine as E

TILESIZE = 16


class Assets:
    def __init__(self):
        self.images =  {}
        self.audio = {
            "music": {}, "sfx": {}
        }

        self.animations = {}
        self.tilesets = {}
        self.weapon_data = {}

        self.load_weapon_data()
        self.load_tilesets()
        self.load_images()
        self.load_animations()

    def load_images(self):
        path = "data/images/"

        # Load weapon images
        files = os.listdir(path + "weapons/")

        for filename in files:
            img = E.ImageManager.load(path + "weapons/" + filename, (0, 0, 0))
            self.images[filename.split(".")[0]] = img
    
    def load_animations(self):
        path = "data/images/animations/"

        # Load player animations
        self.animations["player"] = {"object": None, "images": {}}

        anim_states = os.listdir(path + "player/")

        for state in anim_states:
            self.animations["player"]["images"][state] = []

            img_list = os.listdir(path+"player/"+state)
            for filename in img_list:
                img = E.ImageManager.load(path+"player/"+state+"/"+filename, (0, 0, 0))
                self.animations["player"]["images"][state].append(img)
        
        player_anim_obj = E.Animation()
        for state in self.animations["player"]["images"]:
            frame_time = 100
            if state == "idle":
                frame_time = 300
            elif state == "run":
                frame_time = 150

            if state != "jump":
                player_anim_obj.load_anim(self.animations["player"]["images"][state], state, frame_time)
        
        self.animations["player"]["object"] = player_anim_obj

    def load_tilesets(self):
        path = "data/images/tilesets/"

        files = os.listdir(path)

        for filename in files:
            tile_id = 1
            if len(filename.split(".")) <= 1:
                continue

            file_type = filename.split(".")[1]

            if file_type == "png":
                image = E.ImageManager.load(path+filename, (0, 0, 0))
                tileset = filename.split(".")[0]
                self.tilesets[tileset] = {}

                for i in range(int(image.get_height()/TILESIZE)):
                    for j in range(int(image.get_width()/TILESIZE)):
                        img = E.ImageManager.get_image(image, j*TILESIZE, i*TILESIZE, TILESIZE, TILESIZE, 1)

                        self.tilesets[tileset][tile_id] = img
                        tile_id += 1
            elif file_type == "json":
                with open(path+filename) as file:
                    data = json.load(file)
                    file.close()

                image = E.ImageManager.load(data["path"], (0, 0, 0))
                tileset = filename.split(".")[0]
                self.tilesets[tileset] = {}

                for tile_id in data:
                    if tile_id != "path":
                        tile = data[tile_id]
                        img = E.ImageManager.get_image(image, tile["x"], tile["y"], tile["width"], tile["height"], 1)
                        self.tilesets[tileset][tile_id] = img

    def load_weapon_data(self):
        with open("data/game_data/weapon_data.json") as file:
            self.weapon_data = json.load(file)
            file.close()

    def get_weapon(self, weapon_id):
        if weapon_id in self.weapon_data:
            return self.weapon_data[weapon_id]
    
    def get_tile(self, tileset, tile_id):
        if tileset in self.tilesets:
            if tile_id in self.tilesets[tileset]:
                return self.tilesets[tileset][tile_id]
            else:
                surf = pygame.Surface((TILESIZE, TILESIZE))
                surf.fill((255, 255, 255))
                return surf
        else:
            surf = pygame.Surface((TILESIZE, TILESIZE))
            surf.fill((255, 255, 255))
            return surf
            
    def get_tileset(self, tileset):
        if tileset in self.tilesets:
            return self.tilesets[tileset]

    def get_image(self, img_id):
        if img_id in self.images:
            return self.images[img_id]
        else:
            surf = pygame.Surface((TILESIZE, TILESIZE))
            surf.fill((255, 0, 0))
            return surf