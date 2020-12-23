# ppmount
PPMOUNT - a python wrapper for pmount, that mounts all unmounted devices with a single command

Probably pretty useless for most people, but I like to do any mounting of USB drives, SD cards, etc. myself, without using udev and things like that.
I've been using pmount for quite a while now and it works great, I was just looking for a single command, that mounts all unmounted devices - that's why I created ppmount, a python wrapper for pmount. It uses the output of lsblk to identify all mountable devices and mounts them accordingly.

To unmount all previously pmounted devices, ppumount.py (no arguments/options) takes care of that.

SYSTEMREQUIREMENTS:

   - Operating system: any OS that is capable of running pmount, not Windows obviously
   - lsblk
   - pmount

OPTIONS:

   - -a, --all <br /> Mounts all unmounted devices, that have a filesystem
   - -d, --device <device> <br /> Mounts a single device by its name (e.g. sdb or sdc4, without '/dev/')	
   - -l, --label <label> <br /> Mounts a single device by its label
