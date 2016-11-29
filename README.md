Kakeup
=======

[![License](https://img.shields.io/badge/license-MIT-blue.svg?style=flat)](https://github.com/Ventto/kakeup/blob/master/LICENSE)
[![Status](https://img.shields.io/badge/status-experimental-orange.svg?style=flat)](https://github.com/Ventto/Kakeup/)
[![Language (Python)](https://img.shields.io/badge/powered_by-Python-yellow.svg)](https://www.python.org/)

*Kakeup is a Python tool to force starting Kodi with the Kore's "Wake Up" button.*

Introduction
------------

The purpose is to start a Kodi server without any intrusive and fastidious way as
opening a ssh-session.

The Kore remote is the official Kodi remote and a wonderful application which
implements that feature.<br />But sometimes it works and sometimes not
(reported issue: [KodiForum](http://forum.kodi.tv/showthread.php?tid=222872&pid=2466409#pid2466409)).

So Kakeup is a temporary workaround.

![Screenshot of Kore](doc/kore-btn.jpg)

Requirements
------------

* *python3.5*
* *python-argparse*

Installation
------------

Using a RAW socket listening to a default low number port (cf. screenshot),
you need to:

* Run the script as a privileged user (sudo only)
* Or use a loginless and passwordless user and give it the permissions it needs

*Most modern systems ignore suid/sgid bits on scripts with any interpreter.<br />
So any SUID/CAP set on the script will be ignored.*

![Screenshot of Kore](doc/kore-cfg.jpg)

Usage
-----

```
usage: kakeup.py [-h] [-c CMD] [-m MACADDR] [-i IPSRC]

Miscellaneous:
  -h, --help  Show this help message and exit

Necessary:
  -c CMD      Shell CMD to execute
  -m MACADDR  Filters wol packets with a specific destination MACADDR

Optional:
  -i IPSRC    Filters wol packets with a specific IPSRC address
```

Examples
-------

* Run it with *sudo*:

```
$ python kakeup.py -c "systemctl start kodi" -m "B8:B2:B2:B2:42:42"
$ python kakeup.py -c "exec kodi" -m "B8:B2:B2:B2:42:42"
$ python kakeup.py -c "/usr/bin/bash -c <path>/kodi.sh" -m "B8:B2:B2:B2:42:42"
```
