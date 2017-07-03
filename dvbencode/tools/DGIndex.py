# -*- coding: utf-8 -*-
import subprocess, os, os.path
from ..tracktypes import getTrackInfo

def DGIndex(filename, output):
	"""Run DGIndex on filename"""

	proc = subprocess.Popen(["dgindex\\dgindex.exe", "-i", filename, "-o", output, "-om", "0", "-hide", "-exit"])
	proc.wait()
	
	return getTrackInfo(os.path.dirname(output), os.path.basename(output) + ".d2v")