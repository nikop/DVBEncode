# -*- coding: utf-8 -*-
import os

from .tracktypes import getTrackInfo

def get_streams(directory, unwanted_audios = []):
	video = None
	audio_main = None
	extra_audios = []
	audioSize = 0
	ChpInfo = None
	
	# Select streams to use
	for f in os.listdir(directory):
		track = getTrackInfo(directory, f)
		
		if track == None:
			continue
		
		if video == None and track.getType() == "video":
			video = track
		elif track.getType() == "audio" and audioSize < track.getSize():
			if audio_main != None:
				if audio_main.language in unwanted_audios:
					os.remove(audio_main.fullpath())
				else:
					extra_audios.append(audio_main)
				
			audio_main = track
			audioSize = track.getSize()
		elif track.getType() == "audio":
			if track.language in unwanted_audios:
				os.remove(track.fullpath())
			else:
				extra_audios.append(track)
		elif track.getType() == "chp":
			ChpInfo = track
			
	return [video, audio_main, extra_audios, ChpInfo]