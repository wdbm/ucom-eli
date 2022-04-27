#!/usr/bin/env python

'''
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
# <http://www.gnu.org/licenses>.                                               #
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
    --panel_title=TEXT        panel title              [default: UCOM]
    --hide_panel_title=BOOL   hide panel title         [default: true]
    --close_button=BOOL       include close button     [default: true]
    --power=BOOL              include power display    [default: false]
    --window_frame=BOOL       include window frame     [default: false]
    --always_on_top=BOOL      set always on top        [default: true]
    --set_position=BOOL       set launcher position    [default: true]
    --screen_number=NUMBER    set launch screen number [default: -1]
'''

import datetime
import docopt
import logging
import os
import subprocess
import sys
import threading
import time

import psutil
from PyQt5 import QtGui, QtWidgets
from PyQt5.QtCore import(
    QSize,
    Qt
)
from PyQt5.QtGui import(
    QIcon,
    QFont
)
from PyQt5.QtWidgets import(
    QApplication,
    QLabel,
    QPushButton,
    QWidget,
    QVBoxLayout
)
import shijian
import technicolor
from Xlib.display import Display

name        = 'UCOM-ELI'
__version__ = '2022-04-27T0259Z'

log = logging.getLogger(name)
log.addHandler(technicolor.ColorisingStreamHandler())
log.setLevel(logging.DEBUG)

def main(options):

    class Program(object):
        def __init():
            return 0
    global program
    program = Program()

    filepath_configuration    =     options['--configuration']
    program.color_1           =     options['--foreground_color']
    program.color_2           =     options['--background_color']
    program.panel_title       =     options['--panel_title']
    program.hide_panel_title  =     options['--hide_panel_title'].lower()  == 'true'
    program.close_button      =     options['--close_button'].lower()      == 'true'
    program.power             =     options['--power'].lower()             == 'true'
    program.window_frame      =     options['--window_frame'].lower()      == 'true'
    program.set_always_on_top =     options['--always_on_top'].lower()     == 'true'
    program.set_position      =     options['--set_position'].lower()      == 'true'
    program.screen_number     = int(options['--screen_number'])

    program.icon_width        = 70
    program.icon_height       = 70
    program.button_width      = 85
    program.button_height     = 85
    program.font_size         = 12

    filepath_configuration = os.path.expanduser(os.path.expandvars(filepath_configuration))
    if not os.path.isfile(filepath_configuration):
        log.fatal(f'file {filepath_configuration} not found')
        program.terminate()
    program.configuration = shijian.open_configuration(filename=filepath_configuration)

    application = QApplication(sys.argv)
    interface = Interface()
    interface.move(
        application.desktop().screenGeometry(program.screen_number).left(),
        application.desktop().screenGeometry(program.screen_number).top()
    )
    sys.exit(application.exec_())

class Launcher(object):

    def __init__(
        self,
        name    = None,
        command = ':',
        icon    = '',
        button  = None,
        ):
        self.name    = name
        self.command = command
        self.icon    = icon
        self.button  = button
        # Set button style.
        self.button.setStyleSheet(
            f'''
            color: #{program.color_1};
            background-color: #{program.color_2};
            border: 1px solid #{program.color_1};
            '''
        )
        # Set button dimensions.
        self.button.setFixedSize(program.button_width, program.button_height)
        # Set button icon.
        self.button.setIcon(QIcon(self.icon))
        # Set button icon dimensions.
        self.button.setIconSize(QSize(program.icon_width, program.icon_height))
        # Set button action.
        self.button.clicked.connect(lambda: self.execute())
        
    def execute(self):
        if self.name == 'close':
            sys.exit()
        else:
            log.info(f'execute launcher "{self.name}"')
            #print(self.command.split())
            #subprocess.Popen(['bash', '-c'] + self.command.split())
            os.system(self.command)
        
class Interface(QWidget):

    def __init__(self):
        super(Interface, self).__init__()
        self.text_panel = QLabel(program.panel_title)
        if program.power:
            self.indicator_percentage_power = QLabel(self)
        self.indicator_clock = QLabel(self)
        # Loop over all launchers specified in the configuration, building a
        # list of launchers.
        launchers = []
        for name, attributes in list(program.configuration['launchers'].items()):
            log.info(f'load launcher "{name}"')
            # If a launcher has a "desktop entry" file specification, accept it
            # in preference to other specifications of the launcher.
            if 'desktop entry' not in attributes:
                # Cope with specification or no specification of the icon. If an
                # icon is specified, set no button text.
                if 'icon' in attributes:
                    icon = attributes['icon']
                    button = QPushButton(self)
                else:
                    icon = ''
                    button = QPushButton(name, self)
                # Parse the command.
                command = attributes['command']
            else:
                filepath_desktop_entry = attributes['desktop entry']
                file_desktop_entry = open(filepath_desktop_entry, 'r')
                icon               = ''
                command            = ''
                desktop_entry_name = name
                for line in file_desktop_entry:
                    if 'Icon=' in line:
                        icon = line.split('Icon=')[1].rstrip('\n')
                    if 'Exec=' in line:
                        command = line.split('Exec=')[1].rstrip('\n')
                    if 'Name=' in line:
                        desktop_entry_name = line.split('Name=')[1].rstrip('\n')
                # Cope with specification or no specification of the icon. If an
                # icon is specified, set no button text.
                if icon is not None:
                    button = QPushButton(self)
                else:
                    icon = ''
                    button = QPushButton(name, self)
                button.setToolTip(desktop_entry_name)
            # Create the launcher.
            launcher = Launcher(
                name    = desktop_entry_name,
                command = command,
                icon    = icon,
                button  = button
            )
            launchers.append(launcher)
        # Add an close launcher.
        if program.close_button:
            name = 'close'
            launcher = Launcher(
                name   = name,
                button = QPushButton(name, self)
            )
            launchers.append(launcher)
        # Set the layout.
        vbox = QVBoxLayout()
        vbox.addStretch(1)
        if not program.hide_panel_title:
            if program.panel_title != '':
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
        self.font = QFont('Arial', program.font_size)
        self.setStyleSheet(
            f'''
            color: #{program.color_1};
            background-color: #{program.color_2}
            '''
        )
        self.text_panel.setStyleSheet(
            f'''
            QLabel{{
                color: #{program.color_1};
                background-color: #{program.color_2};
                border: 1px solid #{program.color_1};
            }}
            '''
        )
        #self.text_panel.setFont(self.font)
        self.text_panel.setAlignment(Qt.AlignCenter)
        if len(program.panel_title) <= 7:
            self.text_panel.setFixedSize(program.button_width, 20)
        else:
            self.text_panel.setFixedSize(program.button_width, program.button_height)
        if program.power:
            self.indicator_percentage_power.setStyleSheet(
                f'''
                QLabel{{
                    color: #{program.color_1};
                    background-color: #{program.color_2};
                    border: 1px solid #{program.color_1};
                }}
                '''
            )
            #self.indicator_percentage_power.setFont(self.font)
            self.indicator_percentage_power.setAlignment(Qt.AlignCenter)
            #self.indicator_percentage_power.setFixedSize(program.button_width, program.button_height)
            self.indicator_percentage_power.setFixedSize(program.button_width, 20)
        self.indicator_clock.setStyleSheet(
            f'''
            QLabel{{
                color: #{program.color_1};
                background-color: #{program.color_2};
                border: 1px solid #{program.color_1};
            }}
            '''
        )
        self.indicator_clock.setFont(self.font)
        self.indicator_clock.setAlignment(Qt.AlignCenter)
        #self.indicator_clock.setFixedSize(program.button_width, program.button_height)
        self.indicator_clock.setFixedSize(program.button_width, 60)
        # power thread
        if program.power:
            thread_percentage_power = threading.Thread(target=self.percentage_power)
            thread_percentage_power.daemon = True
            thread_percentage_power.start()
        # clock thread
        thread_clock = threading.Thread(target=self.clock)
        thread_clock.daemon = True
        thread_clock.start()
        self.setWindowTitle(name)
        # Position and decorate the window.
        if program.set_always_on_top is True:
            self.setWindowFlags(Qt.WindowStaysOnTopHint)
        if program.window_frame is False:
            self.setWindowFlags(Qt.FramelessWindowHint)
        if program.set_position is True:
            self.move(0, 0)
        self.show()
        # Reserve space for the window.
        program.window_identification = self.winId().__int__()
        program.window_width = self.width()
        program.window_height = self.height()
        log.info(f'window identification: {program.window_identification}')
        #try:
        window = Window(program.window_identification)
        #window.reserve_space(program.window_width, 0, 0, 0)
        #except:
        #    log.info('could not reserve space for interface')

    def percentage_power(self):
        while True:
            percentage_power = str(round(psutil.sensors_battery().percent, 2)) + ' %'
            self.indicator_percentage_power.setText(percentage_power)
            time.sleep(30)

    def clock(self):
        while True:
            self.indicator_clock.setText(datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC').replace(' ', '\n', 2))
            time.sleep(1)

class Window(object):

    def __init__(self, window_ID):
        self._display = Display()
        self._window = self._display.create_resource_object('window', window_ID)

    def reserve_space(
        self,
        left   = 0,
        right  = 0,
        top    = 0,
        bottom = 0
        ):
        LEFT    = int(left)
        RIGHT   = int(right)
        TOP     = int(top)
        BOTTOM  = int(bottom)
        print([LEFT, RIGHT, TOP, BOTTOM])
        self._window.change_property(
            self._display.intern_atom('_NET_WM_STRUT'),
            self._display.intern_atom('CARDINAL'),
            32,
            [LEFT, RIGHT, TOP, BOTTOM]
        )
        self._display.sync()

if __name__ == '__main__':
    options = docopt.docopt(__doc__)
    if options['--version']:
        print(__version__)
        exit()
    main(options)
