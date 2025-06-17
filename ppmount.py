#!/usr/bin/env python3

import getopt
import sys
import os
import subprocess
import json
import re

LSBLK_VERSION = (2, 37, 0)

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

    try:
        oplist, args = getopt.getopt(commandline_args, unix_options, gnu_options)
    except getopt.error:
        print("ERROR: Please check your commandline arguments / options.\n")
        print_usage()
        sys.exit(0)

    return oplist


def clean_string_output(string):
    new = string.replace("\\n", "")
    new = new.replace("('", "")
    new = new.replace("', None)", "")
    return new


def parse_lsblk_version():
    try:
        result = subprocess.run(
            ['lsblk', '--version'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
            text=True
        )
        match = re.search(r'util-linux\s+(\d+)\.(\d+)\.(\d+)', result.stdout)
        if match:
            return tuple(map(int, match.groups()))
    except Exception as e:
        print("WARNING: Couldn't get lsblk version:", e)
    return (0, 0, 0)


def is_device_mountable(device_list, use_mountpoints=True):
    fstype = device_list.get("fstype")
    if fstype is None:
        return False

    if use_mountpoints:
        mountpoints = device_list.get("mountpoints")
        if not mountpoints or all(mp is None for mp in mountpoints):
            return True
    else:
        mountpoint = device_list.get("mountpoint")
        if mountpoint is None:
            return True

    return False


def check_args(device_list, mount_all, name, label):
    return mount_all or (device_list.get("name") == name or device_list.get("label") == label)


def mount_device(device_list):
    dev = "/dev/" + device_list["name"]
    if device_list.get("label"):
        mount_point = "/media/" + device_list["name"] + "_" + str(device_list["label"]).replace(" ", "_")
    else:
        mount_point = "/media/" + device_list["name"]

    cmd = "pmount " + dev + " " + mount_point
    pmount = subprocess.run(cmd, stdout=subprocess.PIPE, shell=True)
    if pmount.returncode == 0:
        print("Device '" + dev + "' has been mounted to '" + mount_point + "' successfully.")
    else:
        print("ERROR: Device '" + dev + "' couldn't be mounted to '" + mount_point + "'.")


def check_and_mount_devices(device_list, mount_all, device_name, device_label, devices_mounted, use_mountpoints):
    if is_device_mountable(device_list, use_mountpoints):
        if check_args(device_list, mount_all, device_name, device_label):
            mount_device(device_list)
            devices_mounted = True
    return devices_mounted


def main():
    if not check_requirements():
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

    if mount_all and (device_name or device_label):
        print("You can either mount all devices (-a/--All) or a specific one (-d/--device or -l/--label), not both.")
        sys.exit(0)

    if device_name and device_label:
        print("You can either mount a specific device by its name (-d/--device) or label (-l/--label), not both.")
        sys.exit(0)

    version = parse_lsblk_version()
    use_mountpoints = version >= LSBLK_VERSION
    lsblk_fields = "NAME,FSTYPE,LABEL," + ("MOUNTPOINTS" if use_mountpoints else "MOUNTPOINT")

    try:
        result = subprocess.run(
            ["lsblk", "-J", "-f", "--output", lsblk_fields],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
            text=True
        )
        lsblk_output_json = json.loads(result.stdout)
    except Exception as e:
        print("lsblk ERROR:", e)
        sys.exit(1)

    devices_mounted = False
    for blockdev in lsblk_output_json.get("blockdevices", []):
        devices_mounted = check_and_mount_devices(blockdev, mount_all, device_name, device_label, devices_mounted, use_mountpoints)
        for child in blockdev.get("children", []):
            devices_mounted = check_and_mount_devices(child, mount_all, device_name, device_label, devices_mounted, use_mountpoints)

    if not devices_mounted:
        print("No unmounted devices found.")


if __name__ == "__main__":
    main()
