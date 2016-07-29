# PokemonGO-IV-Renamer
Automatically renames your pokemon to their IV stats.

Example:
A perfect vaporeon will be renamed to 45, 15/15/15

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

| Argument             | Description                                   | Required | Example                                         |
| -------------------- | --------------------------------------------- | -------- | ----------------------------------------------- |
| `-a`                 | Login service, `google` or `ptc`              | yes      |                                                 |
| `-u`                 | Username                                      | yes      |                                                 |
| `-p`                 | Password                                      | yes      |                                                 |
| `--format`           | Custom nickname format, placeholders below    | optional | `--format "%percent% %name"` => `100% Vaporeon` |
| `--list_only`, `-lo` | Show only Pokémons' IVs without renaming them | optional |                                                 |
| `--locale`, `-l`     | Translations for Pokémon names, default `en`  | optional | `--locale de`, `-l de` (check `locales` folder for more options) |
| `--clear`            | Reset names to original                       | optional |                                                 |

Placeholders for custom nickname format (automatically gets cropped to 12 characters):

| Placeholder | Description    | Example  |
| ----------- | -------------- | -------- |
| `%name`     | Name           | Vaporeon |
| `%cp`       | CP             | 1800     |
| `%atk`      | Attack         | 15       |
| `%def`      | Defense        | 15       |
| `%sta`      | Stamina        | 15       |
| `%percent`  | IV perfection  | 100      |

## Credits
- [tejado](https://github.com/tejado) for the API
- [PokemonGo-Bot People](https://github.com/PokemonGoF/PokemonGo-Bot) for some of the code
