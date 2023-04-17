# CP2AT
## About
A tool for converting Stardew Valley Mods from the Content Patcher framework to the Alternative Textures framework. For more information on the Content Patcher framework, see [here](https://github.com/Pathoschild/StardewMods/tree/develop/ContentPatcher/docs). For more information on the Alternative Textures framework, see [here](https://github.com/Floogen/AlternativeTextures/wiki/).

This script relies on comparing the asset provided by the mod to the vanilla asset from the game. All vanilla Stardew Valley assets can be unpacked from the game using [StardewXnbHack](https://github.com/Pathoschild/StardewXnbHack#readme), and belong to ConcernedApe.

## Features
Currently, this script supports the conversion of:
1. TileSheets/Craftables.png
2. Fruit Trees & Trees
3. TileSheets/Furniture.png (but no sit, only look >:C)
4. Farm Buildings

## Usage
For a better guide (with screenshots!) on how to install Python and run a Python script from command line, see Elizabeth's guides for **Windows** [here](https://github.com/elizabethcd/FurnitureConverter/blob/main/docs/Windows_guide.md#windows-detailed-pictorial-install-guide) and **Mac** [here](https://github.com/elizabethcd/FurnitureConverter/blob/main/docs/Mac_guide.md#mac-detailed-pictorial-install-guide)

### Basic Instructions
1. Install Python between versions 3.8 and 3.10 (see the download page for Python 3.8 [here](https://www.python.org/downloads/release/python-380/)).
2. Install the Python requirements
    * **NOTE**: For this converter, you can run `pip install -r requirements.txt`, but for issues, the required packages are `json5`, `pillow`, and `numpy`.
3. Download and extract the latest GitHub release.
4. Place the entire mod folder into `CP2AT/` folder so the folders look like this:
```
CP2AT/
├─ MOD_FOLDER_NAME/
│  ├─ assets/
│  ├─ manifest.json
│  ├─ content.json
```
4. Change the `config.json` to indicate the name of your mod folder (e.g. `[CP] YourModHere`) and any keywords that you wish to include.
```
{
    "mod_folder_path": "[CP] Mi's and Magimatica Country Furniture",
    "keywords": ["furniture", "Mi's and Magimatica"] 
}
```
5. Open a Command Prompt or Terminal window in the `CP2AT` folder.
    1. For Windows, open the folder in your file browser and type `cmd` into the address bar at the top.
    2. For Mac/Linux, right click and select "Open folder in Terminal"
6. Run `main.py` using `py main.py` (or if that doesn't work, `python main.py` or `python3 main.py`)
7. Find your textures in the new `[AT]` folder!

## Known Issues
Furniture conversion will not fully work if the CP's `content.json` changes more than one row of furniture sprites at a time. Will maybe be fixed in future update.

Craftables conversions will also not fully work in the same scenario. Will work on this.

## To-Do:
* Extend script to function for springobjects, animals, buildings, etc.
* Add argument flags for indicating Object Type when no content.json is available to scrape from (e.g. XNB conversions or PNGs from Naver)
