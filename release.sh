if false; then
	pyuic4 main.ui >| main.py
	pyuic4 settings.ui >| settings.py
fi
if false; then
	pylupdate4 gui/settings.py gui/main.py mentalcalculation.py -ts mentalcalculation.ts
	# update translation file to include translation for QDialogButtonBox
	sed -i '/^<\/TS>/i\
<context>\
   <name>QDialogButtonBox</name>\
   <message>\
       <source>OK</source>\
       <translation type="unfinished"></translation>\
   </message>\
   <message>\
       <source>Cancel</source>\
       <translation type="unfinished"></translation>\
   </message>\
</context>' mentalcalculation.ts
	# remove obsolete entry
	#sed -i 's/ type=\"obsolete\"//g' mentalcalculation.ts
	#lrelease mentalcalculation_fr.ts -qm mentalcalculation_fr.qm
fi

version=`grep appVersion mentalcalculation.py|cut -f 3 -d ' '|tr -d "'"`
archive="mentalcalculation-${version}.tar.gz"
rm -f $archive
cd ..
__FILES="
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
mentalcalculation/gui/__init__.py
mentalcalculation/gui/main.py
mentalcalculation/gui/settings.py
mentalcalculation/mentalcalculation.py
mentalcalculation/sound/bad.mp3
mentalcalculation/sound/annoying-sound.mp3
mentalcalculation/sound/good.mp3
mentalcalculation/sound/bell.mp3
mentalcalculation/sound/3bells.mp3"

/bin/echo -e "$__FILES\n`ls -1 mentalcalculation/i18n/*.qm`" | apack ./mentalcalculation/$archive
unset __FILES

cd mentalcalculation
# run the following command in windows: python.exe innosetup.py py2exe
if [ -d dist ] ; then
	# use the build made by py2exe with InnoSetup
	if [ -f dist/Output/mysetup.exe ] ;then
		mv -f dist/Output/mysetup.exe mentalcalculation-${version}-setup.exe
		rmdir dist/Output
	fi
	rm -f dist/mentalcalculation.iss dist/setup.py
	mv dist mentalcalculation-${version}
	rm -f mentalcalculation-${version}.7z mentalcalculation-${version}.zip
	apack mentalcalculation-${version}.zip mentalcalculation-${version}
	apack mentalcalculation-${version}.7z mentalcalculation-${version}
	rm -rf mentalcalculation-${version} build
fi
