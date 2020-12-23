#!/usr/bin/env python

import sys
import os
import subprocess


def check_requirements():

    if os.name == "nt":
        print("Doesn't work on Windows operating systems.")
        return False

    pro = subprocess.run("pmount", stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, shell=True)
    if pro.returncode != 0:
        print("ERROR: 'pmount' not found.")
        return False

    pro = subprocess.run("pumount --version", stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, shell=True)
    if pro.returncode != 0:
        print("ERROR: 'pumount' not found.")
        return False

    return True


def unmount_device(device_list):

    cmd = "pumount " + device_list[0]
    pumount = subprocess.run(cmd, stdout=subprocess.PIPE, shell=True)
    if pumount.returncode == 0:
        print("Device '" + device_list[0] + "' has been unmounted successfully.")
    else:
        print("ERROR: Device '" + device_list[0] + "' couldn't be unmounted.")


def main():

    if check_requirements() is False:
        sys.exit(0)

    pmount = subprocess.Popen("pmount", stdout=subprocess.PIPE, shell=True, universal_newlines=True)

    pmount_output_str = str(pmount.communicate())

    # Splitting the output so we can parse them line by line ->
    output_list = pmount_output_str.split("\\n")

    mounted_devices = False

    # Iiterate through the output line by line ->
    for line in output_list:
        if line.startswith("/dev/"):
            unmount_device(line.split())
            mounted_devices = True

    if mounted_devices is False:
        print("No mounted devices found.")


if __name__ == "__main__":
    main()
