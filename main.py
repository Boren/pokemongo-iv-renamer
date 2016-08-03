#!/usr/bin/env python
"""This module renames pokemon according to user configuration"""

import json
import time
import argparse
from itertools import groupby
from pgoapi import PGoApi

class Colors:
    OKGREEN = '\033[92m'
    ENDC = '\033[0m'

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
        parser.add_argument("-lo", "--list_only", action='store_true', default=False)
        parser.add_argument("--format", default="%ivsum, %atk/%def/%sta")
        parser.add_argument("-l", "--locale", default="en")
	parser.add_argument("-d", "--delay", type=int, default=4)

        self.config = parser.parse_args()
        self.config.overwrite = True
        #self.config.skip_favorite = True
        #self.config.only_favorite = False

    def start(self):
        """Start renamer"""
        print "Start renamer"

        self.init_config()

        try:
            self.pokemon_list = json.load(open('locales/pokemon.' + self.config.locale + '.json'))
        except IOError:
            print "The selected language is currently not supported"
            exit(0)

        self.setup_api()
        self.get_pokemons()
        self.print_pokemons()

        if self.config.list_only:
            pass
        elif self.config.clear:
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
                    num = int(pokemon['pokemon_id'])
                    name = self.pokemon_list[str(num)]

                    attack = pokemon.get('individual_attack', 0)
                    defense = pokemon.get('individual_defense', 0)
                    stamina = pokemon.get('individual_stamina', 0)
                    iv_percent = (float(attack + defense + stamina) / 45.0) * 100.0

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
                        'stamina': stamina,
                        'iv_percent': iv_percent,
                    })
                except KeyError:
                    pass

    def print_pokemons(self):
        """Print pokemons and their stats"""
        sorted_mons = sorted(self.pokemons, key=lambda k: (k['num'], -k['iv_percent']))
        groups = groupby(sorted_mons, key=lambda k: k['num'])

        for key, group in groups:
            group = list(group)
            print "\n--------- " + self.pokemon_list[str(key)].replace(u'\N{MALE SIGN}', '(M)').replace(u'\N{FEMALE SIGN}', '(F)') + " ---------"
            best_iv_pokemon = max(group, key=lambda k: k['iv_percent'])
            best_iv_pokemon['best_iv'] = True

            for pokemon in group:
                info_text = "CP {cp} - {attack}/{defense}/{stamina} {iv_percent:.2f}%".format(**pokemon)
                if pokemon.get('best_iv', False) and len(group) > 1:
                    info_text = Colors.OKGREEN + info_text + Colors.ENDC
                print info_text

    def rename_pokemons(self):
        """Renames pokemons according to configuration"""
        already_renamed = 0
        renamed = 0

        for pokemon in self.pokemons:
            individual_value = pokemon['attack'] + pokemon['defense'] + pokemon['stamina']
            iv_percent = int(pokemon['iv_percent'])

            if individual_value < 10:
                individual_value = "0" + str(individual_value)

            num = int(pokemon['num'])
            pokemon_name = self.pokemon_list[str(num)]

            name = self.config.format
            name = name.replace("%ivsum", str(individual_value))
            name = name.replace("%atk", str(pokemon['attack']))
            name = name.replace("%def", str(pokemon['defense']))
            name = name.replace("%sta", str(pokemon['stamina']))
            name = name.replace("%percent", str(iv_percent))
            name = name.replace("%cp", str(pokemon['cp']))
            name = name.replace("%name", pokemon_name)
            name = name[:12]

            if pokemon['nickname'] == "NONE" \
               or pokemon['nickname'] == pokemon_name \
               or (pokemon['nickname'] != name and self.config.overwrite):

                self.api.nickname_pokemon(pokemon_id=pokemon['id'], nickname=name)
                response = self.api.call()

                result = response['responses']['NICKNAME_POKEMON']['result']

                if result == 1:
                    print "Renaming " + pokemon_name.replace(u'\N{MALE SIGN}', '(M)').replace(u'\N{FEMALE SIGN}', '(F)') + " (CP " + str(pokemon['cp'])  + ") to " + name
                else:
                    print "Something went wrong with renaming " + pokemon_name.replace(u'\N{MALE SIGN}', '(M)').replace(u'\N{FEMALE SIGN}', '(F)') + " (CP " + str(pokemon['cp'])  + ") to " + name + ". Error code: " + str(result)

                renamed += 1

            else:
                already_renamed += 1

        print str(renamed) + " pokemons renamed."
        print str(already_renamed) + " pokemons already renamed."

    def clear_pokemons(self):
        """Resets all pokemon names to the original"""
        cleared = 0

        for pokemon in self.pokemons:
            num = int(pokemon['num'])
            name_original = self.pokemon_list[str(num)]

            if pokemon['nickname'] != "NONE" and pokemon['nickname'] != name_original:
                self.api.nickname_pokemon(pokemon_id=pokemon['id'], nickname=name_original)
                
                time.sleep(self.config.delay)
                
                response = self.api.call()

                result = response['responses']['NICKNAME_POKEMON']['result']		

                if result == 1:
                    print "Resetted " + pokemon['nickname'] +  " to " + name_original
                else:
                    print "Something went wrong with resetting " + pokemon['nickname'] + " to " + name_original + ". Error code: " + str(result)

                time.sleep(self.config.delay)

                cleared += 1

        print "Cleared " + str(cleared) + " names"

if __name__ == '__main__':
    Renamer().start()
