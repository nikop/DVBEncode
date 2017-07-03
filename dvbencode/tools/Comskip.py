# -*- coding: utf-8 -*-

import subprocess, io, re, os, configparser

def Comskip(filename):
	"""Run Comskip on a file"""

	proc = subprocess.Popen(["comskip\\comskip.exe", filename])
	proc.wait()
		
	with io.open(filename + ".avs", 'r', encoding='utf_8_sig') as fp:
		avs = fp.read()

		sections = []

		for s in re.findall("trim\((\d+),(\d+)\)", avs):
			sections.append([int(s[0]), int(s[1]), ""])
			
	os.remove(filename + ".avs")
			
	return sections