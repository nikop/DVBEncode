# -*- coding: utf-8 -*-
import subprocess, io, re, os, configparser

def tsmuxer_mux(video, audio, output):
	"""Run Tsmuxer on a file"""
	
	with io.open(output + ".meta", 'w', encoding='cp1252') as fp:
		fp.write("MUXOPT\n")
		
		write_track_meta(fp, video)
		write_track_meta(fp, audio)
	
	proc = subprocess.Popen(["tsmuxer\\tsMuxeR.exe", output + ".meta", output])
	proc.wait()
	
	os.remove(output + ".meta")
	
def write_track_meta(fp, track):
	t = ""
	f = ""
	
	if track.getType() == "video":
		t = "V"
		
		if track.getFormat() == "mpeg2":
			f = "MPEG-2"
		
	elif track.getType() == "audio":
		t = "A"
		
		if track.getFormat() == "mpa":
			f = "MP3"
		
	if t == "" or f == "":
		raise Exception("Invalid Track Format " + str(track))
	
	fp.write("{0}_{1}, {2}\n".format(t, f, track.fullpath()))