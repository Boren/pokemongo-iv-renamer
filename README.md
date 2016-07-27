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

-a can be either 'ptc' or 'google'

You can also pass a custom format if you want.
Just add --format "YOUR-FORMAT"

Format automatically replaces these values:
- %name (Vaporeon)
- %cp (1800)
- %atk (15)
- %def (15)
- %sta (15)
- %percent (100)

Example:
--format("%percent% %name") prints ("100% Vaporeon")

Automatically gets cropped to 12 characters.

If you want to reset names to original ones pass the flag "--clear"

## Credits
- [tejado](https://github.com/tejado) for the API
- [PokemonGo-Bot People](https://github.com/PokemonGoF/PokemonGo-Bot) for some of the code
