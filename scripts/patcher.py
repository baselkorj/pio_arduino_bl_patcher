import subprocess
import shutil
import sys
import os
import sys
from tkinter import *
from tkinter.messagebox import askyesno

import odoo.owrapper as odoo

Import('env')

# Set to True if you want to flash the generated board ID in flash
flash_id = False

# Meta Data
product_id = 9999
pcb_model = 'XXX'
pcb_version = '1.0'
fw_version = '1.0'


def install_packages():
    subprocess.check_call([sys.executable, '-m', 'pip',
                          'install', 'xlrd', 'Pillow'])


def merge_bl(source, target, env):
    root = Tk()
    root.withdraw()
    answer = askyesno(title='Confirmation',
                      message='Add Bootloader to Firmware?')
    if answer:
        bootloader = open('scripts/bootloader.hex')
        bootloader_contents = bootloader.readlines()

        shutil.copy('.pio/build/' + env.Dictionary('PIOENV') + '/firmware.hex',
                    '.pio/build/' + env.Dictionary('PIOENV') + '/firmware_no_bootloader.hex')

        firmware = open(
            '.pio/build/' + env.Dictionary('PIOENV') + '/firmware.hex')
        firmware_contents = firmware.readlines()

        if (len(firmware_contents) > 2014):
            sys.exit('Flash Memory is Full, No Space Left for UUID and Bootloader!')

        firmware_contents.insert(0, ':020000040000FA\n')

        firmware_contents.pop(len(firmware_contents) - 1)

        print('\nMerging Bootloader...')

        for i in bootloader_contents:
            firmware_contents.append(i)

        firmware = open('.pio/build/' + env.Dictionary('PIOENV') +
                        '/firmware.hex', 'w')
        firmware.writelines(firmware_contents)

        print('Bootloader Merged.\n')


def set_id(source, target, env):
    firmware = open(
        '.pio/build/' + env.Dictionary('PIOENV') + '/firmware.hex')
    firmware_contents = firmware.readlines()

    bootloader = open('scripts/bootloader.hex')
    bootloader_contents = bootloader.readlines()

    y = len(firmware_contents)

    print('\nChecking Built File for Bootloader...')
    for i in reversed(bootloader_contents):
        if (firmware_contents[y - 1] != i):
            merge_bl(source, target, env)
            firmware = open(
                '.pio/build/' + env.Dictionary('PIOENV') + '/firmware.hex')
            firmware_contents = firmware.readlines()
            break
        y -= 1

    root = Tk()
    root.withdraw()
    answer = askyesno(title='Confirmation',
                      message='Flash PCB with new Serial ID?')
    if answer:
        install_packages()

        odoo.setCredentials()
        odoo.signIn()

        products = odoo.getProductLots(product_id)

        if os.path.exists('scripts/.temp'):
            new_product_lot = open('scripts/.temp', 'r').read()
        else:
            j = int(products[len(products) - 1]['name'][-6:]) + 1

            new_product_lot = pcb_model + '_PCB_' + \
                pcb_version + '_' + f'{j:06d}'

            with open('scripts/.temp', 'w') as f:
                f.write(new_product_lot)

        print('Generating UUID & Calculating Checksums...')

        firmware = open(
            '.pio/build/' + env.Dictionary('PIOENV') + '/firmware.hex')
        firmware_contents = firmware.readlines()

        pcb_version_partitioned = pcb_version.partition('.')

        record_block = '107DF000' + new_product_lot[0:3].encode(
            'utf-8').hex() + '%0.2X' % int(pcb_version_partitioned[0]) + '%0.2X' % int(pcb_version_partitioned[2]) + '%0.8X' % int(new_product_lot[-6:]) + '00000000000000'

        record_block_bytes = []

        y = 0

        while y < len(record_block):
            record_block_bytes.append(int(record_block[y:y+2], 16))
            y += 2

        checksum = (~sum(record_block_bytes) + 1) & 0xFF

        full_record_block = (':' + record_block + '%0.2X' %
                             checksum + '\n').upper()

        if firmware_contents[len(firmware_contents) - 35].startswith(':107DF000'):
            firmware_contents.pop(len(firmware_contents) - 35)

        firmware_contents.insert(
            len(firmware_contents) - 34, full_record_block)

        firmware = open('.pio/build/' + env.Dictionary('PIOENV') +
                        '/firmware.hex', 'w')
        firmware.writelines(firmware_contents)
        print('\nSuccess! Your Board ID is: ' + new_product_lot + '\n')


def upload_clean_workspace(source, target, env):
    odoo.setCredentials()
    odoo.signIn()

    print('\nSaving Data to Odoo...')

    if os.path.exists('scripts/.temp'):
        try:
            odoo.createProductLot(open('scripts/.temp', 'r').read(),
                                  product_id, fw_version)
            os.remove('scripts/.temp')
        except:
            print('Odoo Operation Failed, Board Was NOT Registered on Odoo!')

    print('Cleaning Workspace...')
    firmware = open('.pio/build/' + env.Dictionary('PIOENV') + '/firmware.hex')
    firmware_contents = firmware.readlines()

    if firmware_contents[len(firmware_contents) - 35].startswith(':107DF000'):
        firmware_contents.pop(len(firmware_contents) - 35)
    else:
        sys.exit(
            'Something unexpected happened with the script at some point. Please clean the project and try again!')

    firmware = open('.pio/build/' + env.Dictionary('PIOENV') +
                    '/firmware.hex', 'w')
    firmware.writelines(firmware_contents)
    print('Success!')


env.AddPreAction('upload', set_id)
env.AddPostAction('upload', upload_clean_workspace)
env.AddPostAction('buildprog', merge_bl)
