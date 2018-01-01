import subprocess
import os
import os.path
import shutil
import glob
import tarfile
import zipfile
import sys

# get mentalcalculation version
with open('mentalcalculation.py') as f:
    for line in f.readlines():
        if line.startswith('appVersion'):
            version = line.split('=')[1].strip().strip("'")

if sys.platform != 'win32':
    print("Error: pyinstaller and Inno Setup can't be run in non Windows platform", file=sys.stderr)
else:
    # run pyinstaller
    cmd = 'pyinstaller.exe mentalcalculation.py'
    try:
        cp = subprocess.run(cmd.split(' '))
    except FileNotFoundError:
        userprofile = os.environ['USERPROFILE'].replace('\\', '\\\\')
        pyinstaller = os.path.sep.join([userprofile, 'AppData\\Local\\Programs\\Python\\Python36\\Scripts\\pyinstaller.exe'])
        cmd = '%s --noconsole -i img/soro.ico mentalcalculation.py' % pyinstaller
        cp = subprocess.run(cmd.split(' '))

    # copy assets in directory
    print(':: Copying assets into target dir')
    try:
        shutil.copytree('img', 'dist/mentalcalculation/img')
        shutil.copytree('sound', 'dist/mentalcalculation/sound')
        shutil.copytree('gui', 'dist/mentalcalculation/gui')
        shutil.copytree('i18n', 'dist/mentalcalculation/i18n')
    except FileExistsError:
        pass

    name = 'Mental Calculation'
    # generate innosetup script
    print(':: Generating mentalcalculation.iss')
    with open('mentalcalculation.iss', 'w') as ofi:
        print('''[Languages]
Name: "en"; MessagesFile: "compiler:Default.isl"
Name: "fr"; MessagesFile: "compiler:Languages\\French.isl"
Name: "it"; MessagesFile: "compiler:Languages\\Italian.isl"
Name: "es"; MessagesFile: "compiler:Languages\\Spanish.isl"
Name: "cs"; MessagesFile: "compiler:Languages\\Czech.isl"
''', file=ofi)

        print('[Setup]', file=ofi)
        print('AppName="%s"' % name, file=ofi)
        print('AppVersion=%s' % version, file=ofi)
        print('ArchitecturesInstallIn64BitMode=x64', file=ofi)
        print('DefaultDirName="{pf}\%s"' % name, file=ofi)
        print('DefaultGroupName="%s"' % name, file=ofi)
        print(file=ofi)

        print('[Dirs]', file=ofi)
        print('Name: "{app}\\sound"', file=ofi)
        print('Name: "{app}\\img"', file=ofi)
        print('Name: "{app}\\gui"', file=ofi)
        print('Name: "{app}\\i18n"', file=ofi)
        print(file=ofi)

        print('[Files]', file=ofi)
        files = []
        for root, dirs, fn in os.walk('dist\\mentalcalculation'):
            for f in fn:
                files.append(os.path.sep.join([root, f]))
        for f in files:
            destdir = os.path.dirname(f).replace('dist\\mentalcalculation', '')
            print('Source: "%s"; DestDir: "{app}%s"; Flags: ignoreversion' % (f, destdir), file=ofi)
        print(file=ofi)

        print('[Icons]', file=ofi)
        for path in glob.glob('dist\\mentalcalculation\\*.exe'):
            path = path.replace('dist\\mentalcalculation\\', '')
            print('Name: "{group}\\%s"; Filename: "{app}\\%s"; WorkingDir: "{app}"' % (name, path), file=ofi)
        print('Name: "{group}\\Uninstall %s"; Filename: "{uninstallexe}"' % name, file=ofi)

    # run innosetup compiler
    innosetup = '%s\\Inno Setup 5\\ISCC.exe' % os.environ['ProgramFiles(x86)']
    if not os.path.isfile(innosetup):
        print("Error: can't find Inno Setup Command-line Compiler", file=sys.stderr)
    else:
        cmd = '%s mentalcalculation.iss' % innosetup
        subprocess.run(cmd.split(' '))

        print(':: Creating zip file')
        zz = 'mentalcalculation-%s.zip' % version
        if os.path.isfile(zz):
            os.unlink(zz)
        with zipfile.ZipFile(zz, 'w', compression=zipfile.ZIP_DEFLATED) as z:
            files = []
            for root, dirs, fn in os.walk('dist\\mentalcalculation'):
                for f in fn:
                    orig = os.path.sep.join([root, f])
                    dest = orig.replace('dist\\mentalcalculation', '')
                    z.write(orig, arcname='mentalcalculation-%s/%s'% (version, dest))

        print(':: Creating 7z file')
        _7zexe = '%s\\7-Zip\\7z.exe' % os.environ['ProgramFiles']
        if not os.path.isfile(_7zexe):
            print("Error: can't find 7z", file=sys.stderr)
        else:
            _7z = 'mentalcalculation-%s.7z' % version
            if os.path.isfile(_7z):
                os.unlink(_7z)
            shutil.move('dist\\mentalcalculation', 'dist\\mentalcalculation-%s' % version)
            cwd = os.getcwd()
            os.chdir('dist')
            cmd = '%s a %s mentalcalculation-%s' % (_7zexe, _7z, version)
            subprocess.run(cmd.split(' '))
            shutil.move(_7z, '..')
            os.chdir(cwd)

        print(':: Cleaning up 1/2')
        shutil.move('Output\\mysetup.exe', 'mentalcalculation-%s-setup.exe' % version)
        shutil.rmtree('Output')

    print(':: Cleaning up 2/2')
    os.unlink('mentalcalculation.iss')
    os.unlink('mentalcalculation.spec')
    shutil.rmtree('dist')
    shutil.rmtree('build')
    shutil.rmtree('__pycache__')

# source code tarball
__FILES__ = [
'mentalcalculation.py',
'setup.py',
'COPYING',
'README.md',
'Changelog',
'img/soroban.png',
'img/warning.png',
'img/restart.png',
'img/face-sad.png',
'img/face-smile.png',
'img/calculator.png',
'gui/__init__.py',
'gui/main.py',
'gui/settings.py',
'sound/bad.mp3',
'sound/annoying-sound.mp3',
'sound/good.mp3',
'sound/bell.mp3',
'sound/3bells.mp3',
]
# add translation files
__FILES__.extend(glob.glob('i18n/*.qm'))

# create various tarballs
print(':: Creating tar.gz')
targz = 'mentalcalculation-%s.tar.gz' % version
if os.path.isfile(targz):
    os.unlink(targz)
with tarfile.open(targz, 'x:gz') as tar:
    for f in __FILES__:
        tar.add(f, arcname='mentalcalculation-%s/%s'% (version, f))
