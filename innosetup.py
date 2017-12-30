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
# By default, the installer will be created as dist\\Output\\setup.exe.

from distutils.core import setup
#import py2exe
import sys

################################################################
import os
import glob
# get mentalcalculation version from source file
with open('mentalcalculation.py') as f:
    for line in f.readlines():
        if line.startswith('appVersion'):
            appVersion = line.split('=')[1].strip()

sys.path.append('C:\\Windows\\WinSxS\\x86_microsoft.vc90.crt_1fc8b3b9a1e18e3b_9.0.30729.9317_none_508dca76bcbcfe81')

class InnoScript:
    def __init__(self,
            name,
            lib_dir,
            dist_dir,
            windows_exe_files = [],
            lib_files = [],
            version = appVersion):
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
        print("; WARNING: This script has been created by py2exe. Changes to this script", file=ofi)
        print("; will be overwritten the next time py2exe is run!", file=ofi)
        print("""
[Languages]
Name: "en"; MessagesFile: "compiler:Default.isl"
Name: "fr"; MessagesFile: "compiler:Languages\French.isl"
Name: "it"; MessagesFile: "compiler:Languages\Italian.isl"
Name: "es"; MessagesFile: "compiler:Languages\Spanish.isl"
Name: "cs"; MessagesFile: "compiler:Languages\Czech.isl"
""", file=ofi)
        print(r"[Setup]", file=ofi)
        print(r"AppName=%s" % self.name, file=ofi)
        print(r"AppVerName=%s %s" % (self.name, self.version), file=ofi)
        print(r"DefaultDirName={pf}\%s" % self.name, file=ofi)
        print(r"DefaultGroupName=%s" % self.name, file=ofi)
        print(file=ofi)

        print(r"[Files]", file=ofi)
        for path in self.windows_exe_files + self.lib_files:
            print(r'Source: "%s"; DestDir: "{app}\%s"; Flags: ignoreversion' % (path, os.path.dirname(path)), file=ofi)
        print(file=ofi)

        print(r"[Icons]", file=ofi)
        for path in self.windows_exe_files:
            print(r'Name: "{group}\%s";' \
                    'Filename: "{app}\%s";' \
                    'WorkingDir: "{app}"' % (self.name, path), file=ofi)
        print('Name: "{group}\\Uninstall %s"; Filename: "{uninstallexe}"' % self.name, file=ofi)

        print(r'[UninstallDelete]', file=ofi)
        print(r'Type: dirifempty; Name: "{app}\img {app}"', file=ofi)

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
                print("Ok, using win32api.")
                win32api.ShellExecute(0, "compile",
                        self.pathname,
                        None,
                        None,
                        0)
        else:
            print("Cool, you have ctypes installed.")
            res = ctypes.windll.shell32.ShellExecuteA(0, "compile",
                    self.pathname,
                    None,
                    None,
                    0)
            if res < 32:
                raise RuntimeError("ShellExecute failed, error %d" % res)


################################################################

from py2exe.distutils_buildexe import py2exe

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
        print("*** creating the inno setup script***")
        script.create()
        print("*** compiling the inno setup script***")
        script.compile()
        # Note: By default the final setup.exe will be in an Output subdirectory.

################################################################

setup(
        windows = [{"script" : "mentalcalculation.pyw",
            "icon_resources": [(1, "img/mentalcalculation.ico")]}],
        options = {"py2exe" : {"includes" : ["sip"], "compressed": 1, "optimize": 2}},
        zipfile = "lib/library.zip",
        packages = ['gui'],
        data_files = [
            ('.', ['README', 'LISEZMOI', 'COPYING', 'Changelog',
                #'C:\\WINDOWS\\system32\\msvcp90.dll']),
                #'C:\\WINDOWS\\WinSxS\\x86_Microsoft.VC90.CRT_1fc8b3b9a1e18e3b_9.0.30729.1_x-ww_6f74963e\\msvcp90.dll']),
            'C:\\Windows\\WinSxS\\x86_microsoft.vc90.crt_1fc8b3b9a1e18e3b_9.0.30729.9317_none_508dca76bcbcfe81\\msvcp90.dll']),
            ('i18n', glob.glob('i18n/*.qm')),
            ('img', [
                'img/soroban.png',
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
                'sound/3bells.mp3',
                'sound/annoying-sound.mp3'
                ])
            ],
        # use out build_installer class as extended py2exe build command
        cmdclass = {"py2exe": build_installer},
        )
