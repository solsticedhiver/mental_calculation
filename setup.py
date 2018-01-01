#!/usr/bin/env python3

from distutils.core import setup
from subprocess import call
import glob
import sys
import mentalcalculation

if sys.version_info[0] > 3:
    print("This script requires python 3")
    exit(1)

dist = setup(name=mentalcalculation.appName,
        version=mentalcalculation.appVersion,
        description='Mental Calculation',
        author="solsTiCe d'Hiver",
        author_email='solstice.dhiver@sorobanexam.org',
        url='http://www.sorobanexam.org/anzan.html',
        scripts=['mentalcalculation.py'],
        packages = ['gui'],
        data_files = [
            ('share/mentalcalculation/i18n', glob.glob('i18n/*.qm')),
            ('share/doc/mentalcalculation', ['README.md', 'COPYING', 'Changelog']),
            ('share/mentalcalculation/img', [
                'img/soroban.png',
                'img/warning.png',
                'img/restart.png',
                'img/face-smile.png',
                'img/face-sad.png',
                'img/calculator.png'
                ]),
            ('share/mentalcalculation/sound', [
                'sound/bad.mp3',
                'sound/good.mp3',
                'sound/bell.mp3',
                'sound/3bells.mp3',
                'sound/annoying-sound.mp3'
                ])
            ],
        )
# Non-documented way of getting the final directory prefix
# TODO: find a better way to do this!
installCmd = dist.get_command_obj(command="install_data")
installdir = installCmd.install_dir
installroot = installCmd.root if installCmd.root else ''
installprefix = installdir.replace(installroot, '', 1)

# hard-code the location of ressources in the main script
call(("sed -i /^SHARE_PATH/s|''|'%s'| %s" % (installdir+'/share/mentalcalculation/', installdir+'/bin/mentalcalculation.py')).split(' '))


# To uninstall, remove
# /usr/bin/mentalcalculation.py
# /usr/share/mentalcalculation/*
# /usr/share/doc/mentalcalculation/*
# /usr/lib/python3.*/site-packages/mentalcalculation*
#
# or record the list of installed files and use it to uninstall
# python setup.py install --record files.txt
# rm $(cat files.txt)
