# pio_arduino_bl_patcher
A PlatformIO script that provides the ability to automatically add the bootloader to an ATmega328P during the flashing process, in addition to allowing the user to register the board on Oodoo automatically after flashing.

## How to Use
### For Bootloader Flashing
1. Copy the repo files to the root folder of your PlatformIO project, replacing the `platformio.ini` file.
2. In the new `platformio.ini` file, edit the project name, flashing params, and fuse settings according to your requirements.
3. Go to `scripts/patcher.py` and edit the following:
  - Choose whether to flash the generated board ID in flash memory or not.
  - In the meta data section, edit the fields according to your board information.
4. For Odoo integration, make sure to fill out the required fields in `scripts/odoo/owrapper.py`.