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

        self.config = parser.parse_args()
        self.config.overwrite = True

    def start(self):
        print("Start renamer")
        self.pokemon_list = json.load(open('pokemon.json'))
        self.init_config()
        self.setup_api()
        self.get_pokemons()
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
                    pokemon_num = int(pokemon['pokemon_id']) - 1
                    pokemon_name = self.pokemon_list[int(pokemon_num)]['Name']
                    try:
                        pokemon_attack = int(pokemon['individual_attack'])
                    except:
                        pokemon_attack = 0
                    try:
                        pokemon_defense = int(pokemon['individual_defense'])
                    except:
                        pokemon_defense = 0
                    try:
                        pokemon_stamina = int(pokemon['individual_stamina'])
                    except:
                        pokemon_stamina = 0

                    try:
                        pokemon_nickname = pokemon['nickname']
                    except:
                        pokemon_nickname = "NONE"

                    #print("[" + str(pokemon_attack) + "/" + str(pokemon_defense) + "/" + str(pokemon_stamina) + "] " + pokemon_name)
                    self.pokemons.append([
                        pokemon['id'],
                        pokemon_attack,
                        pokemon_defense,
                        pokemon_stamina,
                        pokemon_name,
                        pokemon_nickname
                        ])
                except:
                    pass


    def rename_pokemons(self):
        for pokemon in self.pokemons:
            iv = pokemon[1] + pokemon[2] + pokemon[3]
            if iv < 10:
                iv = "0" + str(iv)
            name = str(iv) + ", " + str(pokemon[1]) + "/" + str(pokemon[2]) + "/" + str(pokemon[3])

            if pokemon[5] == "NONE" or (pokemon[5] != name and self.config.overwrite):
                print("Renaming " + pokemon[4] + " to " + name)

                self.api.nickname_pokemon(pokemon_id = pokemon[0], nickname = name)
                response_dict = self.api.call()

                #time.sleep(2)

            else:
                print(pokemon[4] + " already renamed.")

if __name__ == '__main__':
    Renamer().start()
