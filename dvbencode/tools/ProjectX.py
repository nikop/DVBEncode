# -*- coding: utf-8 -*-

import subprocess, io, re, os, configparser

def ProjectX_demux(filename, target):
	"""Run Comskip on a file"""

	proc = subprocess.Popen(
		["java", "-jar", "ProjectX.jar", "-ini", "X.ini", "-name", "video", "-out", target, "-demux", filename],
		cwd="H:\\DVBEncode\ProjectX\\"
	)
	proc.wait()