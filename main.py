#!/usr/bin/env python

import json
import time
import argparse
from sets import Set
from pgoapi import PGoApi

class Renamer():

    def init_config(self):
        parser = argparse.ArgumentParser()
    
        parser.add_argument("-a", "--auth_service")
        parser.add_argument("-u", "--username")
        parser.add_argument("-p", "--password")
        parser.add_argument("--clear", action = 'store_true', default = False)

        self.config = parser.parse_args()
        self.config.delay = 2
        self.config.overwrite = False
        #self.config.skip_favorite = True
        #self.config.only_favorite = False
        #self.config.format = "%ivsum %atk/%def/%sta"

    def start(self):
        print("Start renamer")
        self.pokemon_list = json.load(open('pokemon.json'))
        self.init_config()
        self.setup_api()
        self.get_pokemons()

        if self.config.clear:
            self.clear_pokemons()
        else:
            self.rename_pokemons()

    def setup_api(self):
        self.api = PGoApi()

        if not self.api.login(self.config.auth_service, str(self.config.username), str(self.config.password)):
            print("Login error")
            exit(0)

        print("Signed in")

    def get_pokemons(self):
        print("Getting pokemon list")
        self.api.get_inventory()
        response_dict = self.api.call()

        self.pokemons = []

        for item in response_dict['responses']['GET_INVENTORY']['inventory_delta']['inventory_items']:
            try:
                reduce(dict.__getitem__, ["inventory_item_data", "pokemon_data"], item)
            except KeyError:
                pass
            else:
                try:
                    pokemon = item['inventory_item_data']['pokemon_data']

                    pid = pokemon['id']
                    num = int(pokemon['pokemon_id']) - 1
                    name = self.pokemon_list[int(num)]['Name']
                    
                    attack = pokemon.get('individual_attack', 0)
                    defense = pokemon.get('individual_defense', 0)
                    stamina = pokemon.get('individual_stamina', 0)
                    nickname = pokemon.get('nickname', 'NONE')
                    cp = pokemon.get('cp', 0)

                    self.pokemons.append({
                        'id': pid,
                        'name': name,
                        'nickname': nickname,
                        'num': num,
                        'cp': cp,
                        'attack': attack,
                        'defense': defense,
                        'stamina': stamina
                    })
                except:
                    pass


    def rename_pokemons(self):
        already_renamed = 0
        
        for pokemon in self.pokemons:
            iv = pokemon['attack'] + pokemon['defense'] + pokemon['stamina']
            if iv < 10:
                iv = "0" + str(iv)
            name = str(iv) + ", " + str(pokemon['attack']) + "/" + str(pokemon['defense']) + "/" + str(pokemon['stamina'])

            if pokemon['nickname'] == "NONE" or pokemon['nickname'] == pokemon['name'] or (pokemon['nickname'] != name and self.config.overwrite):
                print("Renaming " + pokemon['name'] + " (CP " + str(pokemon['cp'])  + ") to " + name)

                self.api.nickname_pokemon(pokemon_id = pokemon['id'], nickname = name)
                response_dict = self.api.call()

                time.sleep(self.config.delay)

            else:
                already_renamed += 1

        print(str(already_renamed) + " pokemons already renamed.")

    def clear_pokemons(self):
        cleared = 0

        for pokemon in self.pokemons:
            if pokemon['nickname'] != "NONE" and pokemon['nickname'] != pokemon['name']:
                print("Resetting " + pokemon['nickname'] + " to " + pokemon['name'])

                self.api.nickname_pokemon(pokemon_id = pokemon['id'], nickname = pokemon['name'])
                response_dict = self.api.call()

                time.sleep(self.config.delay)
                
                cleared += 1

        print("Cleared " + str(cleared) + " names")

if __name__ == '__main__':
    Renamer().start()
