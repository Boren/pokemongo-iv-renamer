#!/usr/bin/env python
"""This module renames pokemon according to user configuration"""

import json
import time
import argparse
from pgoapi import PGoApi

class Renamer(object):
    """Main renamer class object"""

    def __init__(self):
        self.pokemons = []
        self.api = None
        self.config = None
        self.pokemon_list = None

    def init_config(self):
        """Gets configuration from command line arguments"""
        parser = argparse.ArgumentParser()

        parser.add_argument("-a", "--auth_service")
        parser.add_argument("-u", "--username")
        parser.add_argument("-p", "--password")
        parser.add_argument("--clear", action='store_true', default=False)
        parser.add_argument("--format", default="%ivsum, %atk/%def/%sta")

        self.config = parser.parse_args()
        self.config.delay = 2
        self.config.overwrite = True
        #self.config.skip_favorite = True
        #self.config.only_favorite = False

    def start(self):
        """Start renamer"""
        print "Start renamer"
        self.pokemon_list = json.load(open('pokemon.json'))
        self.init_config()
        self.setup_api()
        self.get_pokemons()

        if self.config.clear:
            self.clear_pokemons()
        else:
            self.rename_pokemons()

    def setup_api(self):
        """Prepare and sign in to API"""
        self.api = PGoApi()

        if not self.api.login(self.config.auth_service,
                              str(self.config.username),
                              str(self.config.password)):
            print "Login error"
            exit(0)

        print "Signed in"

    def get_pokemons(self):
        """Fetch pokemons from server and store in array"""
        print "Getting pokemon list"
        self.api.get_inventory()
        response_dict = self.api.call()

        self.pokemons = []
        inventory_items = response_dict['responses'] \
                                       ['GET_INVENTORY'] \
                                       ['inventory_delta'] \
                                       ['inventory_items']

        for item in inventory_items:
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
                    combat_power = pokemon.get('cp', 0)

                    self.pokemons.append({
                        'id': pid,
                        'name': name,
                        'nickname': nickname,
                        'num': num,
                        'cp': combat_power,
                        'attack': attack,
                        'defense': defense,
                        'stamina': stamina
                    })
                except KeyError:
                    pass


    def rename_pokemons(self):
        """Renames pokemons according to configuration"""
        already_renamed = 0
        renamed = 0

        for pokemon in self.pokemons:
            individual_value = pokemon['attack'] + pokemon['defense'] + pokemon['stamina']
            percent = int((float(individual_value) / 45.0) * 100)

            if individual_value < 10:
                individual_value = "0" + str(individual_value)

            name = self.config.format
            name = name.replace("%ivsum", str(individual_value))
            name = name.replace("%atk", str(pokemon['attack']))
            name = name.replace("%def", str(pokemon['defense']))
            name = name.replace("%sta", str(pokemon['stamina']))
            name = name.replace("%percent", str(percent))
            name = name.replace("%cp", str(pokemon['cp']))
            name = name.replace("%name", pokemon['name'])
            name = name[:12]

            if pokemon['nickname'] == "NONE" \
               or pokemon['nickname'] == pokemon['name'] \
               or (pokemon['nickname'] != name and self.config.overwrite):
                print "Renaming " + pokemon['name'] + " (CP " + str(pokemon['cp'])  + ") to " + name

                self.api.nickname_pokemon(pokemon_id=pokemon['id'], nickname=name)
                self.api.call()

                time.sleep(self.config.delay)

                renamed += 1

            else:
                already_renamed += 1

        print str(renamed) + " pokemons renamed."
        print str(already_renamed) + " pokemons already renamed."

    def clear_pokemons(self):
        """Resets all pokemon names to the original"""
        cleared = 0

        for pokemon in self.pokemons:
            if pokemon['nickname'] != "NONE" and pokemon['nickname'] != pokemon['name']:
                print "Resetting " + pokemon['nickname'] + " to " + pokemon['name']

                self.api.nickname_pokemon(pokemon_id=pokemon['id'], nickname=pokemon['name'])
                self.api.call()

                time.sleep(self.config.delay)

                cleared += 1

        print "Cleared " + str(cleared) + " names"

if __name__ == '__main__':
    Renamer().start()
