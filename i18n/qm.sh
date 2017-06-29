#!/bin/bash
ls -1 *.ts|while read ts
do
	lrelease $ts -qm ${ts/.ts}.qm
done
