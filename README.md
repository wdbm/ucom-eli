# UCOM-ELI

![](ucom-eli.png)

# introduction

UCOM-ELI is an ergonomic launcher interface. It is launchers displayed as buttons with icons or text. Launchers can be configured by a Markdown list of the following form using icon and command specifications:

    - launchers
       - <launcher 1 name>
          - command: <launcher 1 command>
          - icon: <launcher 1 icon>
       - <launcher 2 name>
          - command: <launcher 2 command>
          - icon: <launcher 2 icon>
       - <launcher 3 name>
          - command: <launcher 3 command>

Launchers can be configured by a Markdown list of the following form using [desktop entry](https://specifications.freedesktop.org/desktop-entry-spec/desktop-entry-spec-latest.html) specifications:

    - launchers
       - <launcher name>
          - desktop entry: <.desktop file path>

An example configuration file is included, which can be used in the following way:

    ./ucom-eli.py --configuration="configuration_example.md"
