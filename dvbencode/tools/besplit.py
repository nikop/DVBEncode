# -*- coding: utf-8 -*-
import subprocess, re

def besplit_split(directory, audio, cuts, fps):
	# BeSplit.exe -core( -input test.mp2 -prefix split -type mp2 ) -split( 0 10.5 20.2 66.66 )
	
	prevStart = -1
	prevEnd = -1
	
	cutspos = []
	
	for split in cuts:
		# If there's no frames between cuts (AR switch)
		if cuts[0] == prevEnd + 1:
			prevEnd = cuts[1]
		elif prevStart != -1:
			cutspos.append(prevStart / float(fps))
			cutspos.append(prevEnd / float(fps))
			
		prevStart = cuts[0]
		prevEnd = cuts[1]
		
	cutspos.append(prevStart / float(fps))
	cutspos.append(prevEnd / float(fps))
	
	subprocess.call(['besplit\\besplit.exe -core( -input "{0}\\{1}" -prefix "{0}\\{2}" -type mp2 ) -split( {3} )'.format( directory, audio, "split", ' '.join(cutpos) )])
	
def besplit_join(directory, parts, output):
	
	listfile = directory + "\\audio.lst"
	
	with io.open(listfile, 'w', encoding='utf_8_sig') as fp:
		for part in parts:
			fp.write(part)
			fp.write("\n")
	
	subprocess.call(['besplit\\besplit.exe -core( -input "{0}" -prefix "{1}" -type mp2 -join )'.format(listfile, output)])
	
	