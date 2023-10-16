# The Oracle
## General
- This is a project created for [Oscar Andersson](https://github.com/oscar230)'s bachelor thesis at [KAU](www.kau.se). 🎉
- The thesis [dissertation is avaliable for download here](http://urn.kb.se/resolve?urn=urn:nbn:se:kau:diva-82564), the data used in this report are the results from [release 1.0.0](https://github.com/oscar230/the-oracle/releases/tag/1.0.0) of this repository. ✨
- Questions? Please, create an issue. 👍

<br><img src="https://styleguide.torproject.org/static/images/tb-onboarding/circumvention.svg" width="200px" height="auto" alt="A computer flying like a helicopter in the clouds above the praying eyes of the adversary.">

## Introduction
A website oracle operating on Tor exit relays.
* Author: Oscar Andersson [oscaande.se](https://www.oscaande.se)
* Organization: Karlstads University [kau.se](https://www.kau.se)
* Course: Examnesarbete DVGC25
* Term: Autmn 2020 (HT2020)
* Licence: GPL-3.0 License, see license file or [gpl-3.0 on gnu.org](https://www.gnu.org/licenses/gpl-3.0.en.html).

## Legal notice
- Do not use this on relays that you do not own or do not have explicit permission for!
- This code is for research purposes only.

## Overview
This is tool that exploits DNS cache in the Tor exit nodes.

## Build and develop
- Makefile supose that a UNIX enviorment is used.
- This repository requires python 3 and python 2.
- 
### Tools
The current version of the tools is noted below in case future versions dont support backwards compatability. (as of 2020-10-28)
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
* 
### Python3 packages
install using `python3 -m pip install stem pysocks seaborn`.
* stem
* pysocks
* seaborn
* 
### Python2 packages
install using `python2 -m pip install stem`.
* stem
* 
### Additional tools
These tools can be built using the makefile in this repository. More about this in "Running chapter".
* [exitmap](https://github.com/NullHypothesis/exitmap) (2019.05.30) by [Philipp Winter](https://nymity.ch/)
* [torsocks](https://git.torproject.org/torsocks.git) (2.3.0) by [The Tor Project](https://torproject.org)

## Usage

### Setup
* All requirements can simply be aquired from running `make` or install [exitmap](https://github.com/NullHypothesis/exitmap) manually, then place the contents of `src/` in exitmaps modules folder and copy `theoracle.conf.example` to `theoracle.conf` to the same direcotry.
* After running `make` or manually installing. Configure the program in the `theoracle.conf` file.

### Reset
To reset the tool, run `make clean`. You will then have do redo the setup procedure, altough note that the configuration file is persistent.

### Run
Run the modules with exitmap using `./exitmap/bin/exitmap A --first-hop B --exit C --config-file exitmaprc` where A is a module, B is the fingerprint of the first hop relay and C is the fingerprint of the targeted exit relay. The supplied exitmap configuration file is called `exitmaprc` and should be specificed using `--config-file exitmaprc`. Read [exitmap documentation](https://github.com/NullHypothesis/exitmap/blob/master/README.md) or run `./exitmap/bin/exitmap` for more commands, modules and information.

## Credits
Thanks! This could not have been possible without:
* [Tobias Pulls](https://www.kau.se/forskare/tobias-pulls) for inpspiring and consulting me.
* [Philipp Winter](https://nymity.ch/) for creating the wonderfull tool [exitmap](https://github.com/NullHypothesis/exitmap).

> And don't worry about [the vase](https://i.pinimg.com/originals/ba/6f/69/ba6f692a8cc8db6796f26d0a6e2b8ed1.gif).
