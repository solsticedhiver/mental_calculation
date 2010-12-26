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
./mentalcalculation/COPYING
./mentalcalculation/README
./mentalcalculation/LISEZMOI
./mentalcalculation/Changelog
./mentalcalculation/img/soro.jpg
./mentalcalculation/img/face-sad.png
./mentalcalculation/img/face-smile.png
./mentalcalculation/img/calculator.png
./mentalcalculation/main.py
./mentalcalculation/settings.py
./mentalcalculation/mentalcalculation.py
./mentalcalculation/mentalcalculation_fr.qm
./mentalcalculation/sound/bad.mp3
./mentalcalculation/sound/good.mp3
./mentalcalculation/sound/bell.mp3" | apack ./mentalcalculation/$archive

cd mentalcalculation
# use the build made by py2exe with InnoSetup
# run the follwoing command in windows: python.exe setup.py py2exe
if [ -d dist ] ; then
	if [ -f dist/Output/setup.exe ] ;then
		mv -f dist/Output/setup.exe mentalcalculation-${version}-setup.exe
		rmdir dist/Output
	fi
	mv dist mentalcalculation-${version}
	rm -f mentalcalculation-${version}.zip
	rm -f dist/mentalcalculation.iss
	apack mentalcalculation-${version}.zip mentalcalculation-${version}
	rm -rf mentalcalculation-${version} build
fi

#lftp -e "orange; cd data; glob rm mentalcalculation-*; mput mentalcalculation-${version}*;"
