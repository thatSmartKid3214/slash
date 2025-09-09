import pygame
import json
import scripts.Engine as E


class Assets:
    def __init__(self):
        self.images = {}
        self.audio = {
            "music": {}, "sfx": {}
        }
        self.animations = {}
        self.tilesets = {}
        self.weapon_data = {}

        self.load_weapon_data()

    def load_weapon_data(self):
        with open("data/game_data/weapon_data.json") as file:
            self.weapon_data = json.load(file)
            file.close()

    def get_weapon(self, weapon_id):
        if weapon_id in self.weapon_data:
            return self.weapon_data[weapon_id]