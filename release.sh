if false; then
pyuic4 main.ui >| main.py
pyuic4 settings.ui >| settings.py

pylupdate4 settings.py main.py mentalcalculation.py -ts mentalcalculation_fr.ts
# update translation file to include translation for QDialogButtonBox
sed -i 's/ type=\"obsolete\"//g' mentalcalculation_fr.ts
lrelease mentalcalculation_fr.ts -qm mentalcalculation_fr.qm
fi

version=`grep appVersion mentalcalculation.py|cut -f 3 -d ' '|tr -d "'"`
archive="mentalcalculation-${version}.tar.gz"
rm -f $archive
cd ..
echo "
mentalcalculation/setup.py
mentalcalculation/COPYING
mentalcalculation/README
mentalcalculation/LISEZMOI
mentalcalculation/Changelog
mentalcalculation/img/soroban.png
mentalcalculation/img/warning.png
mentalcalculation/img/restart.png
mentalcalculation/img/face-sad.png
mentalcalculation/img/face-smile.png
mentalcalculation/img/calculator.png
mentalcalculation/pymentalcalculation/__init__.py
mentalcalculation/pymentalcalculation/main.py
mentalcalculation/pymentalcalculation/settings.py
mentalcalculation/mentalcalculation.py
mentalcalculation/i18n/mentalcalculation_fr.qm
mentalcalculation/sound/bad.mp3
mentalcalculation/sound/annoying-sound.mp3
mentalcalculation/sound/good.mp3
mentalcalculation/sound/bell.mp3
mentalcalculation/sound/3bells.mp3" | apack ./mentalcalculation/$archive

cd mentalcalculation
# run the following command in windows: python.exe setup.py py2exe
if [ -d dist ] ; then
	# use the build made by py2exe with InnoSetup
	if [ -f dist/Output/setup.exe ] ;then
		mv -f dist/Output/setup.exe mentalcalculation-${version}-setup.exe
		rmdir dist/Output
	fi
	rm -f dist/mentalcalculation.iss dist/setup.py
	mv dist mentalcalculation-${version}
	rm -f mentalcalculation-${version}.{7z,zip}
	apack mentalcalculation-${version}.zip mentalcalculation-${version}
	apack mentalcalculation-${version}.7z mentalcalculation-${version}
	rm -rf mentalcalculation-${version} build
fi
