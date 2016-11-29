WakeupKodi
==========

[![License](https://img.shields.io/badge/license-MIT-blue.svg?style=flat)](https://github.com/Ventto/wakeupkd/blob/master/LICENSE)   [![Status](https://img.shields.io/badge/status-experimental-orange.svg?style=flat)](https://github.com/Ventto/wakeupkd/)

*WakeupKodi is a Python program to leverage Kore's "Wake Up" button to start Kodi.*

Introduction
------------

The purpose was to start Kodi without any intrusive and fastidious way as
opening a ssh-session.

On my Rpi, I did not need 'Wake' or 'Suspend' features
So I have leveraged Kore buttons such as "Wake Up" to start Kodi.


Requirements
------------

* *python3.5*

Usage
-----

### Archlinux

It could be nice to run *wakeupkd.py* after Kodi execution, automatically.
If you have installed *kodi-standalone*, it is worth editing  kodi.service such as:

```
...
[Service]
User = kodi
ExecStart = /usr/bin/kodi-standalone -l /run/lirc/lircd
ExecStartPost = python <path>/wakeupkd.py
...
```

### Manually

```
$ sudo python wakeupkd.py
```



