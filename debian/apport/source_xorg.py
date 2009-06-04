#!/usr/bin/python

'''Xorg Apport interface

Copyright (C) 2007, 2008 Canonical Ltd.
Author: Bryce Harrington <bryce.harrington@ubuntu.com>

This program is free software; you can redistribute it and/or modify it
under the terms of the GNU General Public License as published by the
Free Software Foundation; either version 2 of the License, or (at your
option) any later version.  See http://www.gnu.org/copyleft/gpl.html for
the full text of the license.
'''

# TODO:
#  - Create some general purpose routines (see source_network-manager.py)
#  - Parse files to generate system_environment more concisely
#  - Trim lshal output to just required info

import os.path
import subprocess
from apport.hookutils import *

def installed_version(pkg):
    script = subprocess.Popen(['apt-cache', 'policy', pkg], stdout=subprocess.PIPE)
    output = script.communicate()[0]
    return output.split('\n')[1].replace("Installed: ", "")

def add_info(report):
    # Build System Environment
    report['system']  = "distro:             Ubuntu\n"
    report['system'] += "architecture:       " + command_output(['uname','-m'])
    report['system'] += "kernel:             " + command_output(['uname','-r'])

    attach_related_packages(report, [
            "xserver-xorg",
            "libgl1-mesa-glx",
            "libdrm2",
            "xserver-xorg-video-intel",
            "xserver-xorg-video-ati"
            ])

    attach_file(report, '/etc/X11/xorg.conf', 'XorgConf')
    attach_file(report, '/var/log/Xorg.0.log', 'XorgLog')
    attach_file(report, '/var/log/Xorg.0.log.old', 'XorgLogOld')
    attach_file_if_exists(report, '/var/log/gdm/:0.log', 'GdmLog')
    attach_file_if_exists(report, '/var/log/gdm/:0.log.1', 'GdmLogOld')

    # Capture hardware
    attach_hardware(report)
    report['PciDisplay'] = pci_devices(PCI_DISPLAY)
    
    # Detect proprietary drivers
    if 'fglrx' in report['ProcModules']:
        report['fglrx'] = recent_syslog(re.compile('fglrx'))
    else:
        report['fglrx'] = 'Not loaded'

    # For resolution/multi-head bugs
    report['Xrandr'] = command_output(['xrandr', '--verbose'])
    attach_file_if_exists(report,
                          os.path.expanduser('~/.config/monitors.xml'),
                          'monitors.xml')


    # For font dpi bugs
    report['xdpyinfo'] = command_output(['xdpyinfo'])

    # For 3D/Compiz/Mesa bugs
    report['glxinfo'] = command_output(['glxinfo'])

    # For keyboard bugs
    report['setxkbmap'] = command_output(['setxkbmap', '-print'])
    report['xkbcomp'] = command_output(['xkbcomp', ':0', '-w0', '-'])

## DEBUGING ##
if __name__ == '__main__':
    report = {}
    add_info(report)
    for key in report:
        print '[%s]\n%s' % (key, report[key])
