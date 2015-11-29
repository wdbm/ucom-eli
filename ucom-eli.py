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
    --configuration=FILE     configuration             [default: ~/.ucom]
    --foregroundcolor=COLOR  foreground color          [default: 3861aa]
    --backgroundcolor=COLOR  background color          [default: 000000]
    --exitbutton=BOOL        include exit button       [default: true]
    --windowframe=BOOL       include window frame      [default: false]
"""

name    = "UCOM-ELI"
version = "2015-11-29T1926Z"

import imp
import urllib

def smuggle(
    moduleName = None,
    URL        = None
    ):
    if moduleName is None:
        moduleName = URL
    try:
        module = __import__(moduleName)
        return(module)
    except:
        try:
            moduleString = urllib.urlopen(URL).read()
            module = imp.new_module("module")
            exec moduleString in module.__dict__
            return(module)
        except: 
            raise(
                Exception(
                    "module {moduleName} import error".format(
                        moduleName = moduleName
                    )
                )
            )
            sys.exit()

import os
import sys
import subprocess
import time
import logging
docopt = smuggle(
    moduleName = "docopt",
    URL = "https://rawgit.com/docopt/docopt/master/docopt.py"
)
pyrecon = smuggle(
    moduleName = "pyrecon",
    URL = "https://rawgit.com/wdbm/pyrecon/master/pyrecon.py"
)
from PyQt4 import QtGui, QtCore

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
        self.name    = name

        # options
        self.options = options

        # logging
        global logger
        logger = logging.getLogger(__name__)
        logging.basicConfig()
        logger.level = logging.INFO
        logger.info("run {name}".format(name = self.name))

        # configuration
        configurationFileName = self.options["--configuration"]
        self.configuration = pyrecon.openConfiguration(configurationFileName)

        # settings
        self.color1      = self.options["--foregroundcolor"]
        self.color2      = self.options["--backgroundcolor"]
        self.exitButton  = self.options["--exitbutton"].lower() == "true"
        self.windowFrame = self.options["--windowframe"].lower() == "true"

class Launcher(object):

    def __init__(
        self,
        name    = None,
        command = ":",
        icon    = "",
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
            color: #{color1};
            background-color: #{color2};
            border: 1px solid #{color1};
            """.format(
                color1 = program.color1,
                color2 = program.color2
            )
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
        
        if self.name == "exit":
            logger.info("{name}".format(name = self.name))
            sys.exit()
        else:
            logger.info("execute launcher \"{name}\"".format(name = self.name))
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
            logger.info("load launcher \"{name}\"".format(name = name))
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

        # Add an exit launcher.
        if program.exitButton is True:
            name = "exit"
            launcher = Launcher(
                name    = name,
                button  = QtGui.QPushButton(name, self)
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
            color: #{color1};
            background-color: #{color2}
            """.format(
                color1 = program.color1,
                color2 = program.color2
            )
        )
        if program.windowFrame is False:
            self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        self.show()

if __name__ == "__main__":
    options = docopt.docopt(__doc__)
    if options["--version"]:
        print(programVersion)
        exit()
    main(options)
