if false; then
pyuic4 main.ui >| main.py
pyuic4 settings.ui >| settings.py

pylupdate4 settings.py main.py mentalcalculation.py -ts mentalcalculation_fr.ts
sed '$d' mentalcalculation_fr.ts
echo "
<context>
    <name>QDialogButtonBox</name>
    <message>
        <location filename="../src/gui/dialogs/qmessagebox.cpp" line="+1866"/>
        <location line="+464"/>
        <location filename="../src/gui/widgets/qdialogbuttonbox.cpp" line="+561"/>
        <source>OK</source>
        <translation>OK</translation>
    </message>
    <message>
        <location filename="../src/gui/widgets/qdialogbuttonbox.cpp" line="+3"/>
        <source>Save</source>
        <translation>Enregistrer</translation>
    </message>
    <message>
        <location line="+0"/>
        <source>&amp;Save</source>
        <translation>Enregi&amp;strer</translation>
    </message>
    <message>
        <location line="+3"/>
        <source>Open</source>
        <translation>Ouvrir</translation>
    </message>
    <message>
        <location line="+3"/>
        <source>Cancel</source>
        <translation>Annuler</translation>
    </message>
    <message>
        <location line="+0"/>
        <source>&amp;Cancel</source>
        <translation>&amp;Annuler</translation>
    </message>
    <message>
        <location line="+3"/>
        <source>Close</source>
        <translation>Fermer</translation>
    </message>
    <message>
        <location line="+0"/>
        <source>&amp;Close</source>
        <translation>&amp;Fermer</translation>
    </message>
    <message>
        <location line="+3"/>
        <source>Apply</source>
        <translation>Appliquer</translation>
    </message>
    <message>
        <location line="+3"/>
        <source>Reset</source>
        <translation>Réinitialiser</translation>
    </message>
    <message>
        <location line="+3"/>
        <source>Help</source>
        <translation>Aide</translation>
    </message>
    <message>
        <location line="+4"/>
        <source>Don&apos;t Save</source>
        <translation>Ne pas enregistrer</translation>
    </message>
    <message>
        <location line="+4"/>
        <source>Discard</source>
        <translation>Ne pas enregistrer</translation>
    </message>
    <message>
        <location line="+3"/>
        <source>&amp;Yes</source>
        <translation>&amp;Oui</translation>
    </message>
    <message>
        <location line="+3"/>
        <source>Yes to &amp;All</source>
        <translation>Oui à &amp;tout</translation>
    </message>
    <message>
        <location line="+3"/>
        <source>&amp;No</source>
        <translation>&amp;Non</translation>
    </message>
    <message>
        <location line="+3"/>
        <source>N&amp;o to All</source>
        <translation>Non à to&amp;ut</translation>
    </message>
    <message>
        <location line="+3"/>
        <source>Save All</source>
        <translation>Tout Enregistrer</translation>
    </message>
    <message>
        <location line="+3"/>
        <source>Abort</source>
        <translation>Abandonner</translation>
    </message>
    <message>
        <location line="+3"/>
        <source>Retry</source>
        <translation>Réessayer</translation>
    </message>
    <message>
        <location line="+3"/>
        <source>Ignore</source>
        <translation>Ignorer</translation>
    </message>
    <message>
        <location line="+3"/>
        <source>Restore Defaults</source>
        <translation>Restaurer les valeurs par défaut</translation>
    </message>
    <message>
        <location line="-29"/>
        <source>Close without Saving</source>
        <translation>Fermer sans sauvegarder</translation>
    </message>
    <message>
        <location line="-27"/>
        <source>&amp;OK</source>
        <translation>&amp;OK</translation>
    </message>
</context>
</TS>
"  >> mentalcalculation_fr.ts
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

lftp -e "orange; cd data; glob rm mentalcalculation-*; mput mentalcalculation-${version}*;"
