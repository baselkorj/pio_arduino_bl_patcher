import sys
import uuid
Import("env")


def after_build(source, target, env):
    bootloader = open("bootloader.hex")
    bootloader_contents = bootloader.readlines()

    firmware = open(".pio/build/AVR_ISP_w_Bootloader/firmware.hex")
    firmware_contents = firmware.readlines()

    if (len(firmware_contents) > 2015):
        sys.exit("Flash Memory is Full, No Space Left for UUID and Bootloader!")

    firmware_contents.insert(0, ":020000040000FA\n")

    firmware_contents.pop(len(firmware_contents) - 1)

    print("\nMerging Bootloader...")

    for i in bootloader_contents:
        firmware_contents.append(i)

    firmware = open(".pio/build/AVR_ISP_w_Bootloader/firmware.hex", "w")
    firmware.writelines(firmware_contents)

    print("Bootloader Merged.\n")


def before_upload(source, target, env):
    print("\nGenerating UUID & Calculating Checksums...")

    uuidOne = uuid.uuid1()

    firmware = open(".pio/build/AVR_ISP_w_Bootloader/firmware.hex")
    firmware_contents = firmware.readlines()

    record_block = "107DF000" + uuidOne.hex

    record_block_bytes = []

    y = 0

    while y < len(record_block):
        record_block_bytes.append(int(record_block[y:y+2], 16))
        y += 2

    checksum = (~sum(record_block_bytes) + 1) & 0xFF

    full_record_block = (":" + record_block + "%0.2X" %
                         checksum + "\n").upper()

    if firmware_contents[len(firmware_contents) - 35].startswith(":107DF000"):
        firmware_contents.pop(len(firmware_contents) - 35)

    firmware_contents.insert(len(firmware_contents) - 34, full_record_block)

    firmware = open(".pio/build/AVR_ISP_w_Bootloader/firmware.hex", "w")
    firmware.writelines(firmware_contents)
    print("Success! Your Board ID is " + str(uuidOne) + "\n")


def after_upload(source, target, env):
    print("\nCleaning Workspace...")
    firmware = open(".pio/build/AVR_ISP_w_Bootloader/firmware.hex")
    firmware_contents = firmware.readlines()

    if firmware_contents[len(firmware_contents) - 35].startswith(":107DF000"):
        firmware_contents.pop(len(firmware_contents) - 35)
    else:
        sys.exit(
            "Something unexpected happened with the script at some point. Please clean the project and try again!")

    firmware = open(".pio/build/AVR_ISP_w_Bootloader/firmware.hex", "w")
    firmware.writelines(firmware_contents)
    print("Success!")


env.AddPreAction("upload", before_upload)
env.AddPostAction("upload", after_upload)
env.AddPostAction("buildprog", after_build)
