#!/usr/bin/env python

import getopt
import sys
import os
import subprocess
import json


def check_requirements():

    if os.name == "nt":
        print("Doesn't work on Windows operating systems.")
        return False

    pro = subprocess.run("lsblk", stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, shell=True)
    if pro.returncode != 0:
        print("ERROR: 'lsblk' not found.")
        return False

    pro = subprocess.run("pmount", stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, shell=True)
    if pro.returncode != 0:
        print("ERROR: 'pmount' not found.")
        return False

    return True


def print_usage():

    print("Usage:")
    print("  ppmount.py [arguments/options], e.g.: 'ppmount.py -a' or 'ppmount.py -d /dev/sdb2' - see readme for more.")


def get_cmd_args():

    commandline_args = sys.argv[1:]
    unix_options = "ad:l:"
    gnu_options = ["all", "device=", "label="]

    oplist = []

    try:
        oplist, args = getopt.getopt(commandline_args, unix_options, gnu_options)

    except getopt.error:
        print("ERROR: Please check your commandline arguments / options.\n")
        print_usage()

    return oplist


def clean_string_output(string):

    new = string.replace("\\n", "")
    new = new.replace("('", "")
    new = new.replace("', None)", "")

    return new


def is_device_mountable(device_list):

    if device_list["fstype"] is not None and device_list["mountpoint"] is None:
        return True

    return False


def check_args(device_list, mount_all, name, label):

    if mount_all is True or (device_list["name"] == name or device_list["label"] == label):
        return True

    return False


def mount_device(device_list):

    dev = "/dev/" + device_list["name"]
    if device_list["label"] is not None:
        mount_point = "/media/" + device_list["name"] + "_" + str(device_list["label"]).replace(" ", "_")
    else:
        mount_point = "/media/" + device_list["name"]

    cmd = "pmount " + dev + " " + mount_point
    pmount = subprocess.run(cmd, stdout=subprocess.PIPE, shell=True)
    if pmount.returncode == 0:
        print("Device '" + dev + "' has been mounted to '" + mount_point + "' successfully.")
    else:
        print("ERROR: Device '" + dev + "' couldn't be mounted to '" + mount_point + "'.")


def check_and_mount_devices(device_list, mount_all, device_name, device_label, devices_mounted):

    if is_device_mountable(device_list) is True:
        if check_args(device_list, mount_all, device_name, device_label) is True:
            mount_device(device_list)
            devices_mounted = True

    return devices_mounted


def main():

    if check_requirements() is False:
        sys.exit(0)

    if len(sys.argv) <= 1:
        print_usage()
        sys.exit(0)

    oplist = get_cmd_args()
    if not oplist:
        sys.exit(0)

    mount_all = False
    device_name = ""
    device_label = ""

    for opt, arg in oplist:

        if opt in ['-a', '--all']:
            mount_all = True
        if opt in ['-d', '--device']:
            device_name = arg
        if opt in ['-l', '--label']:
            device_label = arg

    if mount_all is True and (device_name != "" or device_label != ""):
        print("You can either mount all devices (-a/--All) or a specific one (-d/--device or -l/--label), not both.")
        sys.exit(0)

    if device_name != "" and device_label != "":
        print("You can either mount a specific device by is name (-d/--device) or label (-l/--label), not both.")
        sys.exit(0)

    pro = subprocess.Popen("lsblk -Jf", stdout=subprocess.PIPE, shell=True, universal_newlines=True)

    lsblk_output_str = str(pro.communicate())
    lsblk_output_str = clean_string_output(lsblk_output_str)

    lsblk_output_json = json.loads(lsblk_output_str)

    devices_mounted = False
    for blockdev in lsblk_output_json["blockdevices"]:

        devices_mounted = check_and_mount_devices(blockdev, mount_all, device_name, device_label, devices_mounted)

        if "children" in blockdev:
            for child in blockdev["children"]:

                devices_mounted = check_and_mount_devices(child, mount_all, device_name, device_label, devices_mounted)

    if devices_mounted is False:
        print("No unmounted devices found.")


if __name__ == "__main__":
    main()
