import os
Import("env", "projenv")


def after_build(source, target, env):
    bootloader = open("bootloader.hex")
    bootloader_contents = bootloader.readlines()

    firmware = open(".pio/build/AVR_ISP_w_Bootloader/firmware.hex")
    firmware_contents = firmware.readlines()

    firmware_contents.insert(0, bootloader_contents[0])

    bootloader_contents.pop(0)
    bootloader_contents.pop(len(bootloader_contents) - 1)

    for i in bootloader_contents:
        firmware_contents.insert(len(firmware_contents) - 1, i)

    firmware = open(".pio/build/AVR_ISP_w_Bootloader/firmware.hex", "w")
    firmware.writelines(firmware_contents)


env.AddPostAction("buildprog", after_build)
print(env)
