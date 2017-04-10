#!/usr/bin/env python
# coding=utf-8

"""This module renames Pokemon according to user configuration"""

import argparse
import json
import random
import re
import time
from itertools import groupby
from random import randint

import requests
from pgoapi import PGoApi
from pgoapi import utilities as util
from terminaltables import AsciiTable


class Colors:
    OKGREEN = '\033[92m'
    ENDC = '\033[0m'

class Renamer(object):
    """Main renamer class object"""

    def __init__(self):
        self.pokemon = []
        self.api = None
        self.config = None
        self.position = None
        self.pokemon_list = None
        self.pokemon_move = None

    def init_config(self):
        """Gets configuration from command line arguments"""
        parser = argparse.ArgumentParser()

        parser.add_argument("-a", "--auth_service")
        parser.add_argument("-u", "--username")
        parser.add_argument("-p", "--password")
        parser.add_argument("-l", "--location")
        parser.add_argument('--hash-key', required=True)
        parser.add_argument("--clear", action='store_true', default=False)
        parser.add_argument("-lo", "--list_only", action='store_true', default=False)
        parser.add_argument("--format", default="%ivsum, %atk/%def/%sta")
        parser.add_argument("-L", "--locale", default="en")
        parser.add_argument("--min_delay", type=int, default=10)
        parser.add_argument("--max_delay", type=int, default=20)
        parser.add_argument("--iv", type=int, default=0)
        parser.add_argument("--cp", type=int, default=0)

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
            self.pokemon_move = json.load(open('locales/moves.' + self.config.locale + '.json'))
        except IOError:
            print "The selected language is currently not supported"
            exit(0)

        self.setup_api()
        self.get_pokemon()
        self.print_pokemon()

        if self.config.list_only:
            pass
        elif self.config.clear:
            self.clear_pokemon()
        else:
            self.rename_pokemon()

    def setup_api(self):
        """Prepare and sign in to API"""
        self.api = PGoApi()
        self.api.activate_hash_server(self.config.hash_key)
        self.get_location()

        if not self.api.login(self.config.auth_service,
                              str(self.config.username),
                              str(self.config.password), self.position[0], self.position[1], self.position[2]):
            print "Login error"
            exit(0)

        print "Signed in"

    def get_pokemon(self):
        """Fetch Pokemon from server and store in array"""
        print "Getting Pokemon list"
        self.random_sleep()
        response_dict = self.api.get_inventory()

        self.pokemon = []
        inventory_items = (response_dict
                           .get('responses', {})
                           .get('GET_INVENTORY', {})
                           .get('inventory_delta', {})
                           .get('inventory_items', {}))

        for item in inventory_items:
            try:
                reduce(dict.__getitem__, ["inventory_item_data", "pokemon_data"], item)
            except KeyError:
                pass
            else:
                try:
                    pokemon = item['inventory_item_data']['pokemon_data']

                    pid = pokemon['id']
                    num = pokemon['pokemon_id']
                    name = self.pokemon_list[str(num)]

                    attack = pokemon.get('individual_attack', 0)
                    defense = pokemon.get('individual_defense', 0)
                    stamina = pokemon.get('individual_stamina', 0)
                    iv_percent = (float(attack + defense + stamina) / 45.0) * 100.0

                    nickname = pokemon.get('nickname', 'NONE')
                    combat_power = pokemon.get('cp', 0)

                    move_1 = self.pokemon_move[str(pokemon.get('move_1', 0))]
                    move_2 = self.pokemon_move[str(pokemon.get('move_2', 0))]

                    self.pokemon.append({
                        'id': pid,
                        'num': num,
                        'name': name,
                        'nickname': nickname,
                        'cp': combat_power,
                        'attack': attack,
                        'defense': defense,
                        'stamina': stamina,
                        'iv_percent': iv_percent,
                        'move_1': move_1,
                        'move_2': move_2,
                    })
                except KeyError:
                    pass
        # Sort the way the in-game `Number` option would, i.e. by Pokedex number
        # in ascending order and then by CP in descending order.
        self.pokemon.sort(key=lambda k: (k['num'], -k['cp']))

    def print_pokemon(self):
        """Print Pokemon and their stats"""
        sorted_mons = sorted(self.pokemon, key=lambda k: (k['num'], -k['iv_percent']))
        groups = groupby(sorted_mons, key=lambda k: k['num'])
        table_data = [
            ['Pokemon', 'CP', 'IV %', 'ATK', 'DEF', 'STA', 'FastATK (Damage)', 'ChargedATK (Damage)']
        ]
        for key, group in groups:
            group = list(group)
            pokemon_name = self.pokemon_list[str(key)].replace(u'\N{MALE SIGN}', '(M)').replace(u'\N{FEMALE SIGN}', '(F)')
            best_iv_pokemon = max(group, key=lambda k: k['iv_percent'])
            best_iv_pokemon['best_iv'] = True
            for pokemon in group:
                row_data = [
                    pokemon_name,
                    pokemon['cp'],
                    "{0:.0f}%".format(pokemon['iv_percent']),
                    pokemon['attack'],
                    pokemon['defense'],
                    pokemon['stamina'],
                    "{0} ({1})".format(pokemon['move_1']['name'], pokemon['move_1']['power']),
                    "{0} ({1})".format(pokemon['move_2']['name'], pokemon['move_2']['power']),
                ]
                table_data.append(row_data)
                # if pokemon.get('best_iv', False) and len(group) > 1:
                #     row_data = [Colors.OKGREEN + str(cell) + Colors.ENDC for cell in row_data]
        table = AsciiTable(table_data)
        table.justify_columns[0] = 'left'
        table.justify_columns[1] = 'right'
        table.justify_columns[2] = 'right'
        table.justify_columns[3] = 'right'
        table.justify_columns[4] = 'right'
        table.justify_columns[5] = 'right'
        table.justify_columns[6] = 'right'
        table.justify_columns[7] = 'right'
        print table.table

    def rename_pokemon(self):
        """Renames Pokemon according to configuration"""
        already_renamed = 0
        renamed = 0

        for pokemon in self.pokemon:
            individual_value = pokemon['attack'] + pokemon['defense'] + pokemon['stamina']
            iv_percent = int(pokemon['iv_percent'])

            if individual_value < 10:
                individual_value = "0" + str(individual_value)

            num = pokemon['num']
            pokemon_name = self.pokemon_list[str(num)]

            name = self.config.format
            name = name.replace("%id", str(num))
            name = name.replace("%ivsum", str(individual_value))
            name = name.replace("%atk", str(pokemon['attack']))
            name = name.replace("%def", str(pokemon['defense']))
            name = name.replace("%sta", str(pokemon['stamina']))
            name = name.replace("%percent", str(iv_percent))
            name = name.replace("%cp", str(pokemon['cp']))
            name = name.replace("%name", pokemon_name)
            name = name[:12]

            if (pokemon['nickname'] == "NONE" \
                or pokemon['nickname'] == pokemon_name \
                or (pokemon['nickname'] != name and self.config.overwrite)) \
                and iv_percent >= self.config.iv \
                and pokemon['cp'] >= self.config.cp:

                self.random_sleep()

                response = self.api.nickname_pokemon(pokemon_id=pokemon['id'], nickname=name)

                result = response['responses']['NICKNAME_POKEMON']['result']

                if result == 1:
                    print "Renaming " + pokemon_name.replace(u'\N{MALE SIGN}', '(M)').replace(u'\N{FEMALE SIGN}', '(F)') + " (CP " + str(pokemon['cp'])  + ") to " + name
                else:
                    print "Something went wrong with renaming " + pokemon_name.replace(u'\N{MALE SIGN}', '(M)').replace(u'\N{FEMALE SIGN}', '(F)') + " (CP " + str(pokemon['cp'])  + ") to " + name + ". Error code: " + str(result)

                renamed += 1

            else:
                already_renamed += 1

        print str(renamed) + " Pokemon renamed."
        print str(already_renamed) + " Pokemon already renamed."

    def clear_pokemon(self):
        """Resets all Pokemon names to the original"""
        cleared = 0

        for pokemon in self.pokemon:
            num = int(pokemon['num'])
            name_original = self.pokemon_list[str(num)]

            if pokemon['nickname'] != "NONE" and pokemon['nickname'] != name_original:
                response = self.api.nickname_pokemon(pokemon_id=pokemon['id'], nickname=name_original)

                result = response['responses']['NICKNAME_POKEMON']['result']

                if result == 1:
                    print "Resetted " + pokemon['nickname'] + " to " + name_original.replace(u'\N{MALE SIGN}', '(M)').replace(u'\N{FEMALE SIGN}', '(F)')
                else:
                    print "Something went wrong with resetting " + pokemon['nickname'] + " to " + name_original.replace(u'\N{MALE SIGN}', '(M)').replace(u'\N{FEMALE SIGN}', '(F)') + ". Error code: " + str(result)

                random_delay = randint(self.config.min_delay, self.config.max_delay)
                time.sleep(random_delay)

                cleared += 1

        print "Cleared " + str(cleared) + " names"

    def get_elevation_for_position(self):
        try:
            url = 'https://maps.googleapis.com/maps/api/elevation/json?locations={},{}'.format(
                str(self.position[0]), str(self.position[1]))
            altitude = requests.get(url).json()[u'results'][0][u'elevation'] + random.uniform(0.9, 1.7)
            print "Local altitude is: {0}m".format(altitude)

            self.position = (self.position[0], self.position[1], altitude)
        except requests.exceptions.RequestException:
            print "Unable to retrieve altitude from Google APIs; setting to 0"

    def get_location(self):
        # use lat/lng directly if matches such a pattern
        prog = re.compile("^(\-?\d+\.\d+),?\s?(\-?\d+\.\d+)$")
        res = prog.match(self.config.location)
        if res:
            print "Using coordinates from CLI directly"
            self.position = (float(res.group(1)), float(res.group(2)), 0)
        else:
            print "Looking up coordinates in API"
            self.position = util.get_pos_by_name(self.config.location)

        self.get_elevation_for_position()

    def random_sleep(self):
        random_delay = randint(self.config.min_delay, self.config.max_delay)
        print "Will sleep for " + str(random_delay) + " seconds to slow down and not stress out the api..."
        time.sleep(random_delay)

if __name__ == '__main__':
    Renamer().start()
