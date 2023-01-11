# CP2AT
## About
A tool for converting Stardew Valley Mods from the Content Patcher framework to the Alternative Textures framework.

## Features
Currently, this script supports the conversion of:
1. Craftables
2. Trees

## Usage
1. Download the latest release.
2. Install Python between versions 3.8 and 3.10.
3. Place the entire mod folder into `CP2AT/` folder.
4. Change the `config.json` to indicate the name of your mod folder (e.g. `[CP] YourModHere`) and any keywords that you wish to include.
5. In your terminal, navigate to the `CP2AT/` folder.
6. Run `main.py` using `python main.py` (or `py main.py`, `python3 main.py`)
7. Find the new `Textures/` folder in your mod folder!

## To-Do:
* Create a separate output folder for `Textures`
* Add creation of the `manifest.json` file.
* Extend script to function for animals, furniture, buildings, etc.
