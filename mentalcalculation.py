#!/usr/bin/python

# mentalcalculation - version 0.3.2
# Copyright (C) 2008-2010, solsTiCe d'Hiver <solstice.dhiver@gmail.com>

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
# In addition, as a special exception, the copyright holders give
# permission to link the code of portions of this program with the
# OpenSSL library under certain conditions as described in each
# individual source file, and distribute linked combinations
# including the two.
#
# You must obey the GNU General Public License in all respects for
# all of the code used other than OpenSSL.  If you modify file(s)
# with this exception, you may extend this exception to your version
# of the file(s), but you are not obligated to do so.  If you do not
# wish to do so, delete this exception statement from your version.
# If you delete this exception statement from all source files in the
# program, then also delete it here.
#

import sys
from optparse import OptionParser
from platform import system
from tempfile import mkstemp, NamedTemporaryFile
from os import remove, sep
from os.path import isfile, abspath
try:
    from random import SystemRandom
    IS_SYSTEMRANDOM_AVAILABLE = True
except ImportError:
    from random import randint

try:
    from PyQt4 import QtGui,QtCore
    from PyQt4.phonon import Phonon
except ImportError:
    print 'Error: you need PyQt4 to run this software'
    sys.exit(1)
import main, settings

DIGIT = dict([(i,(int('1'+'0'*(i-1)), int('9'*i))) for i in range(1,10)])

appName = 'mentalcalculation'
appVersion = '0.3.2'

BELL = 'sound/bell.mp3'
GOOD = 'sound/good.mp3'
BAD = 'sound/bad.mp3'
WELCOME = 'img/soro.png'
SMILE = 'img/face-smile.png'
SAD = 'img/face-sad.png'

class Settings(QtGui.QDialog):
    def __init__(self, mysettings, parent=None):
        QtGui.QDialog.__init__(self, parent)
        self.__ui = settings.Ui_Dialog()
        self.__ui.setupUi(self)
        self.importSettings(mysettings)
        self.__ui.sb_flash.setEnabled(not self.__ui.cb_sound.isChecked())
        self.connect(self, QtCore.SIGNAL('accepted()'), self.exportSettings)
        self.connect(self.__ui.cb_sound, QtCore.SIGNAL('clicked()'), self.updateSound)
        if IS_ESPEAK_INSTALLED:
            self.__ui.cb_sound.setEnabled(True)
            self.__ui.pm_warning.hide()

    def importSettings(self, mysettings):
        self.__ui.sb_flash.setValue(mysettings['flash'])
        self.__ui.sb_timeout.setValue(mysettings['timeout'])
        self.__ui.sb_digits.setValue(mysettings['digits'])
        self.__ui.sb_rows.setValue(mysettings['rows'])
        self.__ui.cb_sound.setChecked(mysettings['sound'])
        if not IS_ESPEAK_INSTALLED:
            self.__ui.cb_sound.setChecked(False)
        self.__ui.cb_neg.setChecked(mysettings['neg'])
        self.mysettings = mysettings

    def exportSettings(self):
        mysettings = {}
        mysettings['flash'] = self.__ui.sb_flash.value()
        mysettings['timeout'] = self.__ui.sb_timeout.value()
        mysettings['digits'] = self.__ui.sb_digits.value()
        mysettings['rows'] = self.__ui.sb_rows.value()
        mysettings['sound'] = self.__ui.cb_sound.isChecked()
        mysettings['neg'] = self.__ui.cb_neg.isChecked()
        self.mysettings = mysettings

    def updateSound(self):
        sound = self.__ui.sb_flash.isEnabled()
        self.__ui.sb_flash.setEnabled(not sound)

    def exec_(self):
        ok = QtGui.QDialog.exec_(self)
        return (ok, self.mysettings)

class Main(QtGui.QDialog):
    def __init__(self, parent=None, flag=0):
        QtGui.QDialog.__init__(self, parent, flag)
        self.__ui = main.Ui_Dialog()
        self.__ui.setupUi(self)
        self.score = (0,0)
        self.started = False
        # default settings
        self.digits = 1
        self.rows = 5
        self.flash = 500
        self.timeout = 1500
        self.neg = False
        self.sound = False
        self.tmpwav= None
        self.pb_replay = False
        self.replay = False
        self.noscore = False
        self.history = []
        self.importSettings()

        if IS_SYSTEMRANDOM_AVAILABLE:
            self.randint = SystemRandom().randint
        else:
            self.randint = randint

        self.__ui.label.clear()
        self.__ui.le_answer.setInputMask('000009')
        #self.__ui.pb_start.setFocus(QtCore.Qt.OtherFocusReason)
        self.__ui.pb_start.setDefault(True)
        #self.__ui.pb_exit.setAutoDefault(False)
        self.__ui.l_total.hide()

        self.connect(self.__ui.pb_check, QtCore.SIGNAL('clicked()'), self.updateAnswer)
        self.connect(self.__ui.pb_settings, QtCore.SIGNAL('clicked()'), self.mysettings)
        self.connect(self.__ui.pb_exit, QtCore.SIGNAL('clicked()'), self.close)
        self.connect(self.__ui.pb_start, QtCore.SIGNAL('clicked()'), self.start)

        # TODO: add a welcome message; this would be more explicit that this
        self.__ui.label.setPixmap(QtGui.QPixmap(WELCOME))

        self.player = Phonon.createPlayer(Phonon.AccessibilityCategory, Phonon.MediaSource(''))
        self.connect(self.player, QtCore.SIGNAL('finished()'), self.clearLabel)
        self.connect(self.player, QtCore.SIGNAL('stateChanged(Phonon::State, Phonon::State)'), self.cleanup)

        self.__ui.pb_start.installEventFilter(self)

    def eventFilter(self, obj, event):
        if not self.started and self.history:
            if event.type() == QtCore.QEvent.KeyPress and event.key() == QtCore.Qt.Key_Shift:
                self.pb_replay = True
                self.__ui.pb_start.setText(self.tr('&Replay'))
                self.__ui.pb_start.setToolTip(self.tr('Replay the previous sequence'))
                return True
            elif event.type() == QtCore.QEvent.KeyRelease and event.key() == QtCore.Qt.Key_Shift:
                self.pb_replay = False
                self.__ui.pb_start.setText(self.tr('&Start'))
                self.__ui.pb_start.setToolTip(self.tr('Start a sequence'))
                return True
            elif event.type() == QtCore.QEvent.MouseButtonPress and event.button() == QtCore.Qt.LeftButton:
                self.replay = self.pb_replay
                self.pb_replay = False
            elif event.type() == QtCore.QEvent.KeyPress and event.key() == QtCore.Qt.Key_Enter:
                self.replay = self.pb_replay
                self.pb_replay = False
        return QtGui.QPushButton.eventFilter(self, obj, event)

    def importSettings(self):
        # restore settings from the settings file if the settings exist
        settings = QtCore.QSettings(QtCore.QSettings.IniFormat,
                QtCore.QSettings.UserScope, '%s' % appName, '%s' % appName)

        if settings.contains('digits'):
            # these value have been written by the program, so then should be ok
            self.digits = settings.value('digits').toInt()[0]
            self.rows = settings.value('rows').toInt()[0]
            self.timeout = settings.value('timeout').toInt()[0]
            self.flash = settings.value('flash').toInt()[0]
            self.sound = settings.value('sound').toBool()
            self.neg = settings.value('neg').toBool()
        if 'Espeak' in settings.childGroups():
            global ESPEAK_CMD, ESPEAK_LANG, ESPEAK_SPEED, IS_ESPEAK_INSTALLED
            # test for every option
            if settings.contains('Espeak/cmd'):
                ESPEAK_CMD = str(settings.value('Espeak/cmd').toString()).strip('"')
                IS_ESPEAK_INSTALLED = isfile(ESPEAK_CMD)
            if settings.contains('Espeak/lang'):
                ESPEAK_LANG = str(settings.value('Espeak/lang').toString())
            if settings.contains('Espeak/speed'):
                a,b = settings.value('Espeak/speed').toInt()
                # check if it's good
                if b:
                    ESPEAK_SPEED = a

    def clearLabel(self):
        if self.started:
            self.__ui.label.clear()
            # display the next number after timeout
            QtCore.QTimer.singleShot(self.timeout, self.updateLabel)

    def mysettings(self):
        if not self.started:
            mysettings = {}
            mysettings['flash'] = self.flash
            mysettings['timeout'] = self.timeout
            mysettings['digits'] = self.digits
            mysettings['rows'] = self.rows
            mysettings['sound'] = self.sound
            mysettings['neg'] = self.neg
            s = Settings(mysettings, parent=self)
            ok, mysettings = s.exec_()
            if ok:
                self.flash = mysettings['flash']
                self.timeout = mysettings['timeout']
                self.digits = mysettings['digits']
                self.rows = mysettings['rows']
                self.sound = mysettings['sound']
                self.neg = mysettings['neg']
                # always save settings when closing the settings dialog
                settings = QtCore.QSettings(QtCore.QSettings.IniFormat,
                        QtCore.QSettings.UserScope, '%s' % appName, '%s' % appName)
                settings.setValue('digits', QtCore.QVariant(self.digits))
                settings.setValue('rows', QtCore.QVariant(self.rows))
                settings.setValue('timeout', QtCore.QVariant(self.timeout))
                settings.setValue('flash', QtCore.QVariant(self.flash))
                settings.setValue('sound', QtCore.QVariant(self.sound))
                settings.setValue('neg', QtCore.QVariant(self.neg))


    def start(self):
        if not self.started:
            self.started = True
            self.__ui.label.clear()
            self.__ui.l_total.hide()
            #self.__ui.l_answer.setText('Your answer')
            self.__ui.le_answer.clear()
            self.__ui.le_answer.setEnabled(False)
            self.__ui.pb_check.setEnabled(False)
            self.__ui.pb_settings.setEnabled(False)
            self.__count = 0
            # generate sequence
            if self.replay:
                self.replay = False
            else:
                self.makeHistory()
                self.noscore = False
            # wait 1s before starting the display
            QtCore.QTimer.singleShot(1000, self.updateLabel)
            # change pb_start to 'Stop' when starting display
            self.__ui.pb_start.setText(self.tr('&Stop'))
            self.__ui.pb_start.setToolTip(self.tr('Stop the sequence'))
            if self.sound:
                self.player.stop()
        else:
            # then stop it
            self.started = False
            self.__ui.pb_settings.setEnabled(True)
            self.__ui.gb_number.setTitle('#')
            self.__ui.pb_start.setText(self.tr('&Start'))
            self.__ui.pb_start.setToolTip(self.tr('Start a sequence'))
            self.__ui.label.clear()
            if options.verbose:
                print
            if self.sound:
                self.player.stop()
            # reset history
            self.history = []

    def cleanup(self, newstate, oldstate):
        if oldstate == Phonon.PlayingState:
            if self.tmpwav is not None:
                self.tmpwav.close()
                remove(self.tmpwav.name)
                self.tmpwav = None

    def pronounceit(self, s):
        p = QtCore.QProcess(self)
        # Create a tmp wav file that it is later played by Phonon back end
        self.tmpwav = NamedTemporaryFile(suffix='.wav', prefix='mentalcalculation_', delete=False)
        p.start(ESPEAK_CMD, ['-v', ESPEAK_LANG, '-s',  '%d' % ESPEAK_SPEED,'-w', self.tmpwav.name, "'%s'" % s])
        p.waitForFinished()
        # so that it works also on Windows ! wtf !
        self.tmpwav.close()
        # make sure to use the tmp wav
        self.player.setCurrentSource(Phonon.MediaSource(self.tmpwav.name))
        self.player.play()

    def updateAnswer(self):
        if self.__ui.le_answer.isEnabled():
            try:
                a = int(self.__ui.le_answer.text())
            except ValueError:
                a = -100
            u,v = self.score
            if  a == self.answer:
                img = SMILE
                sound = GOOD
                msg = ':-)'
                u += 1
            else:
                msg = ':-('
                img = SAD
                sound = BAD
            # Don't score twice if replay
            if not self.noscore:
                self.score = u,v+1
            if msg == ':-)':
                self.noscore = True
            self.__ui.l_total.show()
            self.__ui.l_total.setText(self.tr('The correct answer is %1').arg(self.answer))
            self.__ui.le_answer.setDisabled(True)
            self.__ui.pb_check.setDisabled(True)
            self.__ui.pb_start.setFocus(QtCore.Qt.OtherFocusReason)
            self.__ui.label.setPixmap(QtGui.QPixmap(img))
            if self.sound:
                self.player.setCurrentSource(Phonon.MediaSource(sound))
                self.player.play()
            self.setWindowTitle(self.tr('Mental Calculation %1/%2').arg(self.score[0]).arg(self.score[1]))
            self.__ui.pb_check.setDefault(False)
            self.__ui.pb_start.setDefault(True)

            if options.verbose:
                sys.stdout.flush()

    def makeHistory(self):
        answer = 0
        self.history = []
        for i in range(self.rows):
            a,b = DIGIT[self.digits]
            neg = False
            if self.neg:
                neg = bool(self.randint(0,1))
            if neg:
                if answer > a:
                    b = min(b, answer)
                else:
                    neg = False
            n = self.randint(a, b)
            # avoid a n - n situation
            while neg and n == self.history[-1]:
                n = self.randint(a, b)
            if neg and answer - n >= 0:
                n = -n
            answer += n
            self.history.append(n)
        self.answer = answer

    def updateLabel(self):
        if self.started:
            if self.__count == self.rows:
                self.started = False
                if self.sound:
                    self.player.setCurrentSource(Phonon.MediaSource(BELL))
                    self.player.play()
                self.__ui.label.setText('?')
                self.__ui.gb_number.setTitle('#')
                self.__ui.pb_start.setText(self.tr('&Start'))
                self.__ui.le_answer.setEnabled(True)
                self.__ui.pb_check.setEnabled(True)
                self.__ui.pb_settings.setEnabled(True)
                self.__ui.le_answer.setFocus(QtCore.Qt.OtherFocusReason)
                self.__ui.pb_check.setDefault(True)
                self.__ui.pb_start.setDefault(False)
                if options.verbose:
                    print
            else:
                self.__count += 1
                self.__ui.gb_number.setTitle('#%d' % (self.__count))
                n = self.history[self.__count-1]
                t = '%d' % n
                if self.neg and self.__count > 1:
                    t = '%+d' % n
                self.__ui.label.setText(t)
                # print the sequence in the console
                if options.verbose:
                    print t,

                if self.sound and IS_ESPEAK_INSTALLED:
                    # how to make it pronounce one digit at a time
                    #t = ' '.join(list(t)).replace('- ', '-')
                    # fix a bug with french not pronouncing the negative sign
                    if ESPEAK_LANG.startswith('fr'):
                        t = t.replace('-', 'moins ')
                    self.pronounceit(t)
                else:
                    # clear the label after self.flash time
                    QtCore.QTimer.singleShot(self.flash, self.clearLabel)

    def closeEvent(self, event):
        # stop the player
        self.player.stop()
        self.player = None
        QtGui.QDialog.closeEvent(self, event)

if __name__ == '__main__':
    parser = OptionParser(usage='usage: %prog [-v]')
    parser.add_option('-v', '--verbose', action='store_true', dest='verbose',
            default=False, help='be verbose: print in console each number displayed')
    (options,args) = parser.parse_args(sys.argv)

    WINDOWS = system() == 'Windows'
    if WINDOWS:
        ESPEAK_CMD = 'C:\Program Files\eSpeak\command_line\espeak.exe'
    else:
        ESPEAK_CMD = '/usr/bin/espeak'

    # check espeak in the default location
    IS_ESPEAK_INSTALLED = isfile(ESPEAK_CMD)

    app = QtGui.QApplication(sys.argv)
    app.setApplicationName('Mental Calculation')

    # initialize locale and load translation files if available
    locale = QtCore.QLocale()
    LOCALENAME = str(locale.system().name())
    translator = QtCore.QTranslator()
    translator.load('mentalcalculation_%s' % LOCALENAME, '.')
    app.installTranslator(translator)

    if LOCALENAME.find('_'):
        ESPEAK_LANG = LOCALENAME[:LOCALENAME.index('_')]
    else:
        ESPEAK_LANG = LOCALENAME
    ESPEAK_SPEED = 170 # the default of espeak

    # create main gui and display settings dialog
    f = Main(flag=QtCore.Qt.WindowTitleHint|QtCore.Qt.WindowSystemMenuHint)
    f.show()
    f.mysettings()

    sys.exit(app.exec_())

