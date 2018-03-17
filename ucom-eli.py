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
    -h, --help                display help message
    --version                 display version and exit
    -v, --verbose             verbose logging
    -s, --silent              silent
    -u, --username=USERNAME   username

    --configuration=FILE      configuration            [default: ~/.ucom]

    --foreground_color=COLOR  foreground color         [default: 3861aa]
    --background_color=COLOR  background color         [default: 000000]
    --panel_text=TEXT         panel text               [default: UCOM]
    --close_button=BOOL       include close button     [default: true]
    --power=BOOL              include power display    [default: false]
    --window_frame=BOOL       include window frame     [default: false]
    --always_on_top=BOOL      set always on top        [default: true]
    --set_position=BOOL       set launcher position    [default: true]
    --screen_number=NUMBER    set launch screen number [default: -1]
"""

import docopt
import logging
import os
import subprocess
import sys
import threading
import time

import propyte
from PyQt4 import QtGui, QtCore
import shijian

name    = "UCOM-ELI"
version = "2018-03-17T2122Z"
logo    = None

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

    filepath_configuration    =     options["--configuration"]
    program.color_1           =     options["--foreground_color"]
    program.color_2           =     options["--background_color"]
    program.panel_text        =     options["--panel_text"]
    program.close_button      =     options["--close_button"].lower()  == "true"
    program.power             =     options["--power"].lower()         == "true"
    program.window_frame      =     options["--window_frame"].lower()  == "true"
    program.set_always_on_top =     options["--always_on_top"].lower() == "true"
    program.set_position      =     options["--set_position"].lower()  == "true"
    program.screen_number     = int(options["--screen_number"])

    filepath_configuration = os.path.expanduser(os.path.expandvars(filepath_configuration))
    if not os.path.isfile(filepath_configuration):
        log.fatal("file {filepath} not found".format(filepath = filepath_configuration))
        program.terminate()
    program.configuration = shijian.open_configuration(filename = filepath_configuration)

    application = QtGui.QApplication(sys.argv)
    interface_1 = interface()
    interface_1.move(
        application.desktop().screenGeometry(program.screen_number).left(),
        application.desktop().screenGeometry(program.screen_number).top()
    )
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
        self.button.setFixedSize(self.button_width, self.button_height)
        # Set button icon.
        self.button.setIcon(
            QtGui.QIcon(self.icon)
        )
        # Set button icon dimensions.
        self.button.setIconSize(QtCore.QSize(self.icon_width, self.icon_height))
        # Set button action.
        self.button.clicked.connect(lambda: self.execute())
        
    def execute(
        self,
        ):
        if self.name == "close":
            program.terminate()
        else:
            log.info("execute launcher \"{name}\"".format(name = self.name))
            #print(self.command.split())
            #subprocess.Popen(["bash", "-c"] + self.command.split())
            os.system(self.command)
        
class interface(QtGui.QWidget):

    def __init__(
        self,
        ):
        super(interface, self).__init__()
        self.text_panel = QtGui.QLabel(program.panel_text)
        if program.power:
            self.indicator_percentage_power = QtGui.QLabel(self)
        self.indicator_clock = QtGui.QLabel(self)
        # Loop over all launchers specified in the configuration, building a
        # list of launchers.
        launchers = []
        for name, attributes in list(program.configuration["launchers"].items()):
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
                filepath_desktop_entry = attributes["desktop entry"]
                file_desktop_entry = open(filepath_desktop_entry, "r")
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
        # Add an close launcher.
        if program.close_button:
            name = "close"
            launcher = Launcher(
                name   = name,
                button = QtGui.QPushButton(name, self)
            )
            launchers.append(launcher)
        # Set the layout.
        vbox = QtGui.QVBoxLayout()
        vbox.addStretch(1)
        if program.panel_text != "":
            vbox.addWidget(self.text_panel)
        # Loop over all launchers, adding the launcher buttons to the layout.
        for launcher in launchers:
            # add button widget
            vbox.addWidget(launcher.button)
            vbox.addStretch(1)
        if program.power:
            vbox.addStretch(1)
            vbox.addWidget(self.indicator_percentage_power)
        vbox.addStretch(1)
        vbox.addWidget(self.indicator_clock)
        self.setLayout(vbox)
        self.font = QtGui.QFont("Arial", 8)
        self.setStyleSheet(
            """
            color: #{color_1};
            background-color: #{color_2}
            """.format(
                color_1 = program.color_1,
                color_2 = program.color_2
            )
        )
        self.text_panel.setStyleSheet(
            """
            QLabel{{
                color: #{color_1};
                background-color: #{color_2};
                border: 1px solid #{color_1};
            }}
            """.format(
                color_1 = program.color_1,
                color_2 = program.color_2
            )
        )
        #self.text_panel.setFont(self.font)
        self.text_panel.setAlignment(QtCore.Qt.AlignCenter)
        if len(program.panel_text) <= 7:
            self.text_panel.setFixedSize(60, 20)
        else:
            self.text_panel.setFixedSize(60, 60)
        if program.power:
            self.indicator_percentage_power.setStyleSheet(
                """
                QLabel{{
                    color: #{color_1};
                    background-color: #{color_2};
                    border: 1px solid #{color_1};
                }}
                """.format(
                    color_1 = program.color_1,
                    color_2 = program.color_2
                )
            )
            #self.indicator_percentage_power.setFont(self.font)
            self.indicator_percentage_power.setAlignment(QtCore.Qt.AlignCenter)
            self.indicator_percentage_power.setFixedSize(60, 60)
        self.indicator_clock.setStyleSheet(
            """
            QLabel{{
                color: #{color_1};
                background-color: #{color_2};
                border: 1px solid #{color_1};
            }}
            """.format(
                color_1 = program.color_1,
                color_2 = program.color_2
            )
        )
        self.indicator_clock.setFont(self.font)
        self.indicator_clock.setAlignment(QtCore.Qt.AlignCenter)
        self.indicator_clock.setFixedSize(60, 60)
        self.setWindowTitle(program.name)
        if program.set_always_on_top is True:
            self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
        if program.window_frame is False:
            self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        if program.set_position is True:
            self.move(0, 0)
        if program.power:
            thread_percentage_power = threading.Thread(target = self.percentage_power)
            thread_percentage_power.daemon = True
            thread_percentage_power.start()
        thread_clock = threading.Thread(target = self.clock)
        thread_clock.daemon = True
        thread_clock.start()
        self.show()

    def percentage_power(
        self
        ):
        while True:
            percentage_power = shijian.percentage_power()
            if not percentage_power:
                percentage_power = "100%"
            self.indicator_percentage_power.setText(percentage_power)
            time.sleep(30)

    def clock(
        self
        ):
        while True:
            self.indicator_clock.setText(shijian.time_UTC(style = "YYYY-MM-DD HH:MM:SS UTC").replace(" ", "\n", 2))
            time.sleep(1)

if __name__ == "__main__":
    options = docopt.docopt(__doc__)
    if options["--version"]:
        print(version)
        exit()
    main(options)
