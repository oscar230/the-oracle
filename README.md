# The Oracle
A website oracle operating on Tor exit relays.
* Author: Oscar Andersson [oscaande.se](https://www.oscaande.se)
* Organization: Karlstads University [kau.se](https://www.kau.se)
* Course: Examnesarbete DVGC25
* Term: Autmn 2020 (HT2020)
* Licence: GPL-3.0 License, see license file or [gpl-3.0 on gnu.org](https://www.gnu.org/licenses/gpl-3.0.en.html).

## NOTICE
Do not use this on exit nodes and relays that you do not own!

## Overview
This is tool that exploits DNS cache in the Tor exit nodes. 

## Requirements
Makefile supose that a UNIX enviorment is used. On Windows, manual building is required.
This repository requires python 3 and the dependencies requires python 2.
The current version of the tools is noted in case future versions dont support backwards compatability. (as of 2020-10-28)
### Command line tools
install using `pacman -S python python2 pip git tor` on Arch based systems and `apt-get install python python2 python-pip git tor` on Debian based systems.
* python2	(2.7.18)
* python3	(3.8.5)
* pip		(20.1.1)
* git		(2.28.0)
* autoconf	(2.69)
* automake	(1.16.2)
* libtool	(2.4.6.42-b88ce-dirty)
* gcc		(10.2.0)
* tor       (0.3.5.12)
### Python3 packages
install using `python3 -m pip install stem pysocks seaborn`.
* stem
* pysocks
* seaborn
### Python2 packages
install using `python2 -m pip install stem`.
* stem
### You also need to build thses tools
These tools can be built using the makefile in this repository. More about this in "Running chapter".
* [exitmap](https://github.com/NullHypothesis/exitmap) (2019.05.30) by [Philipp Winter](https://nymity.ch/)
* [torsocks](https://git.torproject.org/torsocks.git) (2.3.0) by [The Tor Project](https://torproject.org)

## Using the tool
### Setup
* All requirements can simply be aquired from running `make` or install [exitmap](https://github.com/NullHypothesis/exitmap) manually, then place the contents of `src/` in exitmaps modules folder and copy `theoracle.conf.example` to `theoracle.conf` to the same direcotry.
* After running `make` or manually installing. Configure the program in the `theoracle.conf` file.
### Reset
To reset the tool, run `make clean`. You will then have do redo the setup procedure, altough note that the configuration file is persistent.
### Run
Run the modules with exitmap using `./exitmap/bin/exitmap A --first-hop B --exit C --config-file exitmaprc` where A is a module, B is the fingerprint of the first hop relay and C is the fingerprint of the targeted exit relay. The supplied exitmap configuration file is called `exitmaprc` and should be specificed using `--config-file exitmaprc`. Read [exitmap documentation](https://github.com/NullHypothesis/exitmap/blob/master/README.md) or run `./exitmap/bin/exitmap` for more commands, modules and information.

## This could not have been possible without:
* [Philipp Winter](https://nymity.ch/) for creating the wonderfull tool [exitmap](https://github.com/NullHypothesis/exitmap).

> And don't worry about the vase.