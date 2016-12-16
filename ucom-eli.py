#!/usr/bin/env python

"""
################################################################################
#                                                                              #
# UCOM-ELI                                                                     #
#                                                                              #
################################################################################
#                                                                              #
# LICENCE INFORMATION                                                          #
#                                                                              #
# This program is an ergonomic launcher interface.                             #
#                                                                              #
# copyright (C) 2014 William Breaden Madden                                    #
#                                                                              #
# This software is released under the terms of the GNU General Public License  #
# version 3 (GPLv3).                                                           #
#                                                                              #
# This program is free software: you can redistribute it and/or modify it      #
# under the terms of the GNU General Public License as published by the Free   #
# Software Foundation, either version 3 of the License, or (at your option)    #
# any later version.                                                           #
#                                                                              #
# This program is distributed in the hope that it will be useful, but WITHOUT  #
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or        #
# FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for     #
# more details.                                                                #
#                                                                              #
# For a copy of the GNU General Public License, see                            #
# <http://www.gnu.org/licenses/>.                                              #
#                                                                              #
################################################################################

Usage:
    program [options]

Options:
    -h, --help               display help message
    --version                display version and exit
    -v, --verbose            verbose logging
    -s, --silent             silent
    -u, --username=USERNAME  username
    --configuration=FILE     configuration          [default: ~/.ucom]
    --foregroundcolor=COLOR  foreground color       [default: 3861aa]
    --backgroundcolor=COLOR  background color       [default: 000000]
    --exitbutton=BOOL        include exit button    [default: true]
    --windowframe=BOOL       include window frame   [default: false]
    --setposition=BOOL       set launcher position  [default: true]
"""

name    = "UCOM-ELI"
version = "2016-12-16T1450Z"
logo    = None

import docopt
import logging
import os
import propyte
from PyQt4 import QtGui, QtCore
import pyrecon
import subprocess
import sys
import time

def main(options):

    global program
    program = propyte.Program(
        options = options,
        name    = name,
        version = version,
        logo    = logo
    )
    global log
    from propyte import log

    filename_configuration = options["--configuration"]
    program.color_1        = options["--foregroundcolor"]
    program.color_2        = options["--backgroundcolor"]
    program.exit_button    = options["--exitbutton"].lower() == "true"
    program.window_frame   = options["--windowframe"].lower() == "true"
    program.set_position   = options["--setposition"].lower() == "true"
    
    program.configuration = pyrecon.open_configuration(
        filename = filename_configuration
    )

    application = QtGui.QApplication(sys.argv)
    interface1  = interface()
    sys.exit(application.exec_())

class Launcher(object):

    def __init__(
        self,
        name    = None,
        command = ":",
        icon    = "",
        button  = None,
        ):
        self.name          = name
        self.command       = command
        self.icon          = icon
        self.icon_width    = 54
        self.icon_height   = 54
        self.button        = button
        self.button_width  = 60
        self.button_height = 60

        # Set button style.
        self.button.setStyleSheet(
            """
            color: #{color_1};
            background-color: #{color_2};
            border: 1px solid #{color_1};
            """.format(
                color_1 = program.color_1,
                color_2 = program.color_2
            )
        )
        # Set button dimensions.
        self.button.setFixedSize(
            self.button_width,
            self.button_height
        )
        # Set button icon.
        self.button.setIcon(
            QtGui.QIcon(self.icon)
        )
        # Set button icon dimensions.
        self.button.setIconSize(QtCore.QSize(
            self.icon_width,
            self.icon_height
        ))
        # Set button action.
        self.button.clicked.connect(lambda: self.execute())
        
    def execute(
        self,
        ):
        if self.name == "exit":
            program.terminate()
        else:
            log.info("execute launcher \"{name}\"".format(name = self.name))
            #print(self.command.split())
            #subprocess.Popen(['bash', '-c'] + self.command.split())
            os.system(self.command)
        
class interface(QtGui.QWidget):

    def __init__(
        self,
        ):
        super(interface, self).__init__()

        # Loop over all launchers specified in the configuration, building a
        # list of launchers.
        launchers = []
        for name, attributes in program.configuration["launchers"].iteritems():
            log.info("load launcher \"{name}\"".format(name = name))
            # If a launcher has a "desktop entry" file specification, accept it
            # in preference to other specifications of the launcher.
            if "desktop entry" not in attributes:
                # Cope with specification or no specification of the icon. If an
                # icon is specified, set no button text.
                if "icon" in attributes:
                    icon = attributes["icon"]
                    button = QtGui.QPushButton(self)
                else:
                    icon = ""
                    button = QtGui.QPushButton(name, self)
                # Parse the command.
                command = attributes["command"]
            else:
                filename_desktop_entry = attributes["desktop entry"]
                file_desktop_entry = open(filename_desktop_entry, "r")
                for line in file_desktop_entry:
                    if "Icon=" in line:
                        icon = line.split("Icon=")[1].rstrip("\n")
                    if "Exec=" in line:
                        command = line.split("Exec=")[1].rstrip("\n")
                # Cope with specification or no specification of the icon. If an
                # icon is specified, set no button text.
                if icon is not None:
                    button = QtGui.QPushButton(self)
                else:
                    icon = ""
                    button = QtGui.QPushButton(name, self)
            # Create the launcher.
            launcher = Launcher(
                name    = name,
                command = command,
                icon    = icon,
                button  = button
            )
            launchers.append(launcher)

        # Add an exit launcher.
        if program.exit_button is True:
            name = "exit"
            launcher = Launcher(
                name   = name,
                button = QtGui.QPushButton(name, self)
            )
            launchers.append(launcher)

        # Set the layout.
        vbox = QtGui.QVBoxLayout()
        vbox.addStretch(1)

        # Loop over all launchers, adding the launcher buttons to the layout.
        for launcher in launchers:
            # add button widget
            vbox.addWidget(launcher.button)
            vbox.addStretch(1)

        self.setLayout(vbox)

        # window
        self.setWindowTitle(program.name)
        # set window position
        if program.set_position is True:
            self.move(0, 0)
        self.setStyleSheet(
            """
            color: #{color_1};
            background-color: #{color_2}
            """.format(
                color_1 = program.color_1,
                color_2 = program.color_2
            )
        )
        if program.window_frame is False:
            self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        self.show()

if __name__ == "__main__":
    options = docopt.docopt(__doc__)
    if options["--version"]:
        print(programVersion)
        exit()
    main(options)
