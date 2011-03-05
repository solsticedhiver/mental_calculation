# This is an example py2exe setup.py script customized to produce an exe but
# also a setup.exe with Inno Setup.

#####################################################################
#
# A setup script showing how to extend py2exe.
#
# In this case, the py2exe command is subclassed to create an installation
# script for InnoSetup, which can be compiled with the InnoSetup compiler
# to a single file windows installer.
#
# By default, the installer will be created as dist\Output\setup.exe.

from distutils.core import setup
import py2exe
import sys

################################################################
import os

class InnoScript:
    def __init__(self,
            name,
            lib_dir,
            dist_dir,
            windows_exe_files = [],
            lib_files = [],
            version = "0.3.4"):
        self.lib_dir = lib_dir
        self.dist_dir = dist_dir
        if not self.dist_dir[-1] in "\\/":
            self.dist_dir += "\\"
        self.name = name
        self.version = version
        self.windows_exe_files = [self.chop(p) for p in windows_exe_files]
        self.lib_files = [self.chop(p) for p in lib_files]

    def chop(self, pathname):
        assert pathname.startswith(self.dist_dir)
        return pathname[len(self.dist_dir):]

    def create(self, pathname="dist\\mentalcalculation.iss"):
        self.pathname = pathname
        ofi = self.file = open(pathname, "w")
        print >> ofi, "; WARNING: This script has been created by py2exe. Changes to this script"
        print >> ofi, "; will be overwritten the next time py2exe is run!"
        print >> ofi, """
[Languages]
Name: French; MessagesFile: "compiler:Languages\French.isl"
"""
        print >> ofi, r"[Setup]"
        print >> ofi, r"AppName=%s" % self.name
        print >> ofi, r"AppVerName=%s %s" % (self.name, self.version)
        print >> ofi, r"DefaultDirName={pf}\%s" % self.name
        print >> ofi, r"DefaultGroupName=%s" % self.name
        print >> ofi

        print >> ofi, r"[Files]"
        for path in self.windows_exe_files + self.lib_files:
            print >> ofi, r'Source: "%s"; DestDir: "{app}\%s"; Flags: ignoreversion' % (path, os.path.dirname(path))
        print >> ofi

        print >> ofi, r"[Icons]"
        for path in self.windows_exe_files:
            print >> ofi, r'Name: "{group}\%s";' \
                    'Filename: "{app}\%s";' \
                    'WorkingDir: "{app}"' % (self.name, path)
        print >> ofi, 'Name: "{group}\Uninstall %s"; Filename: "{uninstallexe}"' % self.name

        print >> ofi, r'[UninstallDelete]'
        print >> ofi, r'Type: dirifempty; Name: "{app}\img {app}"'

    def compile(self):
        try:
            import ctypes
        except ImportError:
            try:
                import win32api
            except ImportError:
                import os
                os.startfile(self.pathname)
            else:
                print "Ok, using win32api."
                win32api.ShellExecute(0, "compile",
                        self.pathname,
                        None,
                        None,
                        0)
        else:
            print "Cool, you have ctypes installed."
            res = ctypes.windll.shell32.ShellExecuteA(0, "compile",
                    self.pathname,
                    None,
                    None,
                    0)
            if res < 32:
                raise RuntimeError, "ShellExecute failed, error %d" % res


################################################################

from py2exe.build_exe import py2exe

class build_installer(py2exe):
    # This class first builds the exe file(s), then creates a Windows installer.
    # You need InnoSetup for it.
    def run(self):
        # First, let py2exe do it's work.
        py2exe.run(self)

        # create the Installer, using the files py2exe has created.
        script = InnoScript("Mental Calculation",
                self.lib_dir,
                self.dist_dir,
                self.windows_exe_files,
                self.lib_files)
        print "*** creating the inno setup script***"
        script.create()
        print "*** compiling the inno setup script***"
        script.compile()
        # Note: By default the final setup.exe will be in an Output subdirectory.

################################################################

setup(
        windows = [{"script" : "mentalcalculation.pyw",
            "icon_resources": [(1, "img/mentalcalculation.ico")]}],
        options = {"py2exe" : {"includes" : ["sip"], "compressed": 1, "optimize": 2}},
        zipfile = "lib/library.zip",
        data_files = [
            ('phonon_backend', [
                'C:\Python27\Lib\site-packages\PyQt4\plugins\phonon_backend\phonon_ds94.dll'
                ]),
            ('.', ['mentalcalculation_fr.qm', 'README', 'LISEZMOI', 'COPYING', 'Changelog',
                'C:\WINDOWS\system32\msvcp90.dll']),
            ('img', [
                'img/soro.png',
                'img/warning.png',
                'img/restart.png',
                'img/face-smile.png',
                'img/face-sad.png',
                'img/calculator.png'
                ]),
            ('sound', [
                'sound/bad.mp3',
                'sound/good.mp3',
                'sound/bell.mp3',
                'sound/3bells.mp3'
                ])
            ],
        # use out build_installer class as extended py2exe build command
        cmdclass = {"py2exe": build_installer},
        )
