# -*- coding: utf-8 -*-

import subprocess, io, re, os, configparser

def mplex_remux(video, audio, output):
	"""Run Mplex on a file"""
	proc = subprocess.Popen(["mplex\\mplex1.exe", video.fullpath(), audio.fullpath(), output])
	proc.wait()
	
	print(proc.returncode)
	
	# Remove source files
	os.remove(video.fullpath())
	os.remove(audio.fullpath())