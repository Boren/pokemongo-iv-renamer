# PokemonGO-IV-Renamer

Automatically renames your Pokémon to their IV stats.

Example:
Using the default settings, a perfect Vaporeon gets renamed to `45, 15/15/15`.

## Installation

### Requirements

- Python 2
- pip
- git

### Guide

```
git clone -b master https://github.com/Boren/PokemonGO-IV-Renamer.git
cd PokemonGO-IV-Renamer
pip install -r requirements.txt (Might need to sudo)
python2 main.py -a AUTH_SERVICE -u USERNAME -p PASSWORD
```

**Note:** If you use a Google account and have two-factor authentication enabled, you need to [generate an app password](https://security.google.com/settings/security/apppasswords) and use that to log in. 

#### CLI arguments

| Argument             | Description                                   | Required | Example                                         |
| -------------------- | --------------------------------------------- | -------- | ----------------------------------------------- |
| `-a`                 | Login service, `google` or `ptc`              | yes      |                                                 |
| `-u`                 | Username                                      | yes      |                                                 |
| `-p`                 | Password                                      | yes      |                                                 |
| `--format`           | Custom nickname format, placeholders below    | optional | `--format "%percent% %name"` => `100% Vaporeon` |
| `--list_only`, `-lo` | Show only Pokémon IVs without renaming them   | optional |                                                 |
| `--locale`, `-l`     | Translations for Pokémon names, default `en`  | optional | `--locale de`, `-l de` (check `locales` folder for more options) |
| `--clear`            | Reset names to original                       | optional |                                                 |
| `--min_delay`        | Minimum time (in seconds) to wait between requests; default `10`  | optional |                                                 |
| `--max_delay`        | Maximum time (in seconds) to wait between requests; default `20`  | optional |                                                 |
| `--iv`               | Only rename Pokémon with at least _n_% perfect IV; default `0` | optional | `--iv 90` only renames Pokémon with at least 90% perfect IV |

#### Placeholders for `--format`

Placeholders for custom nickname format (automatically gets cropped to 12 characters):

| Placeholder | Description    | Example  |
| ----------- | -------------- | -------- |
| `%id`       | Pokédex ID     | 134      |
| `%name`     | Name           | Vaporeon |
| `%cp`       | CP             | 1800     |
| `%atk`      | Attack         | 15       |
| `%def`      | Defense        | 15       |
| `%sta`      | Stamina        | 15       |
| `%ivsum`    | IV sum         | 45       |
| `%percent`  | IV perfection  | 100      |

Example formats:

| Parameter                             | Example        |
| ------------------------------------- | -------------- |
| `--format '%percent% %name'`          | `98% Vaporeon` |
| `--format '%percent% %atk %def %sta'` | `98% 15 15 14` |
| `--format '#%id @ %percent%'`         | `#134 @ 98%`   |
| `--format '%id %percent %atk %def'`   | `134 98 15 15` |

## Installation with Docker

### Requirements

- Docker or Docker toolbox 

### Guide

```sh
docker pull monkeystorm/pogo-renamer
docker run --name CONTAINERNAME -it pogo-renamer /bin/bash
cd /home/PokemonGO-IV-Renamer/
python2 main.py -a AUTH_SERVICE -u USERNAME -p PASSWORD
```

## Commands

To leave the Docker container:
```
exit
```
  
Once the container has been started once you can reuse it by typing

```sh
docker start CONTAINERNAME
```

then

```sh
docker attach CONTAINERNAME
python2 main.py -a AUTH_SERVICE -u USERNAME -p PASSWORD
```

## Credits
- [tejado](https://github.com/tejado) for the API
- [PokemonGo-Bot People](https://github.com/PokemonGoF/PokemonGo-Bot) for some of the code
