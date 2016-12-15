# UCOM-ELI

![](ucom-eli.py)

# introduction

UCOM-ELI is an ergonomic launcher interface. It is launchers displayed as buttons with icons or text. Launchers are configured by a Markdown list of the following form:

    - launchers
       - <launcher 1 name>
          - command: <launcher 1 command>
          - icon: <launcher 1 icon>
       - <launcher 2 name>
          - command: <launcher 2 command>
          - icon: <launcher 2 icon>
       - <launcher 3 name>
          - command: <launcher 3 command>

An example configuration file is included, which can be used in the following way:

    ./ucom-eli.py --configuration="configuration_example.md"
