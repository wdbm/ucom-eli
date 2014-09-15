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
# FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for    #
# more details.                                                                #
#                                                                              #
# For a copy of the GNU General Public License, see                            #
# <http://www.gnu.org/licenses/>.                                              #
#                                                                              #
################################################################################

Usage:
    program [options]

Options:
    -h, --help                 Show this help message.
    --version                  Show the version and exit.
    -c, --configuration=CONF   configuration [default: ~/.ucom]
"""

programName    = "UCOM-ELI"
programVersion = "2014-09-15T2304"

import os
import sys
import subprocess
import time
import logging
from   docopt import docopt
import pyrecon as pyrecon
from   PyQt4 import QtGui, QtCore

def main(options):
    global program
    program     = Program(options = options)
    application = QtGui.QApplication(sys.argv)
    interface1  = interface()
    sys.exit(application.exec_())

class Program(object):

    def __init__(
        self,
        parent  = None,
        options = None
        ):
        # name
        self.name    = programName
        # options
        self.options = options
        # logging
        global logger
        logger = logging.getLogger(__name__)
        logging.basicConfig()
        logger.level = logging.INFO
        logger.info("running {name}".format(name = self.name))
        # configuration
        configurationFileName = self.options["--configuration"]
        self.configuration = pyrecon.openConfiguration(configurationFileName)

class Launcher(object):

    def __init__(
        self,
        name    = None,
        command = None,
        icon    = None,
        button  = None,
        ):
        self.name         = name
        self.command      = command
        self.icon         = icon
        self.iconWidth    = 54
        self.iconHeight   = 54
        self.button       = button
        self.buttonWidth  = 60
        self.buttonHeight = 60

        # Set button style.
        self.button.setStyleSheet(
            """
            color: yellow;
            background-color: black;
            border: 1px solid yellow;
            """
        )
        # Set button dimensions.
        self.button.setFixedSize(
            self.buttonWidth,
            self.buttonHeight
        )
        # Set button icon.
        self.button.setIcon(
            QtGui.QIcon(self.icon)
        )
        # Set button icon dimensions.
        self.button.setIconSize(QtCore.QSize(
            self.iconWidth,
            self.iconHeight
        ))
        # Set button action.
        self.button.clicked.connect(lambda: self.execute())
        
    def execute(
        self,
        ):
        logger.info("executing launcher \"{name}\"".format(name = self.name))
        #print self.command.split()
        #subprocess.Popen(['bash', '-c'] + self.command.split())
        os.system(self.command)
        
class interface(QtGui.QWidget):

    def __init__(
        self,
	    ):
        super(interface, self).__init__()

        # Cycle over all launchers specified in the configuration, building a
        # list of launchers.
        launchers = []
        for name, attributes in program.configuration["launchers"].iteritems():
            logger.info("loading launcher \"{name}\"".format(name = name))
            # Cope with specification or no specification of the icon. If an
            # icon is specified, there is no button text set.
            if "icon" in attributes:
                icon = attributes["icon"]
                button = QtGui.QPushButton(self)
            else:
                icon = ""
                button = QtGui.QPushButton(name, self)
            # Parse the command.
            command = attributes["command"]
            # Create the launcher.
            launcher = Launcher(
                name    = name,
                command = command,
                icon    = icon,
                button  = button
            )
            launchers.append(launcher)

        # Set the layout.
        vbox = QtGui.QVBoxLayout()
        vbox.addStretch(1)

        # Cycle over all launchers, adding the launcher buttons to the layout.
        for launcher in launchers:
            # add button widget
            vbox.addWidget(launcher.button)
            vbox.addStretch(1)
        self.setLayout(vbox)

        # window
        self.setWindowTitle(program.name)
        # set window position
        self.move(0, 0)
        self.setStyleSheet(
            """
            color: yellow;
            background-color: black
            """
        )
        self.show()

if __name__ == "__main__":
    options = docopt(__doc__)
    if options["--version"]:
        print(programVersion)
        exit()
    main(options)
