# -*- coding: utf-8 -*-
import subprocess, io, re, os, os.path, configparser
from datetime import timedelta

def parseTimestamp(s):
    if s is None:
        return None
    d = re.match(
            r'(?P<hours>\d+):(?P<minutes>\d+):(?P<seconds>\d+\.\d+)',
            str(s)).groupdict(0)
    return timedelta(**dict(( (key, float(value))
                              for key, value in d.items() )))

def getTrackInfo(directory, filename):
	(fn, ext) = os.path.splitext(filename)
	
	if ext == ".m2v" or ext == ".d2v" or ext == ".ts":
		track = VideoTrack(directory, filename)
	elif ext == ".mp1" or ext == ".mp2" or ext == ".mp3":
		track = AudioTrack(directory, filename)
	elif ext == ".txt" and fn[-4:] == '.chp':
		track = ChpInfoTrack(directory, filename)
	else:
		track = None
		
	return track



class BaseTrack():
	def __init__(self, directory, filename):
		self.directory = directory
		self.filename = filename
		(self.basename, self.ext) = os.path.splitext(filename)
		
	def getType(self):
		return "INVALID"
	
	def getFormat(self):
		return "INVALID"
	
	def getSize(self):
		return os.path.getsize(self.fullpath())

	def fullpath(self):
		return self.directory + "\\" + self.filename
	
class ChpInfoTrack(BaseTrack):
	def __init__(self, directory, filename):
		super().__init__(directory, filename)
		
		self.arinfo = []
		
		with io.open(directory + "\\" + filename, 'r', encoding='ascii') as fp:
			for line in fp:
				(ts, info) = line.split(';')
				ts = parseTimestamp(ts.strip())
				info = info.strip()
				
				# 00:00:00.000 ; -> video basics: 720*576 @ 25fps @ 0.7031 (16:9) @ 15000000 bps - vbv 98
				if info[:16] == "-> video basics:":
					(resolution, fps, ar, bitrate) = info[17:].split('@')

					fps = float(fps.strip()[:-3])
					
					i = {
						'start': int(ts.total_seconds() * fps),
						'x': 1,
						'y': 1
					}
					
					m_ar = re.search("\((\d+):(\d+)\)", ar.strip())
					
					if m_ar:
						i["x"] = int(m_ar.group(1))
						i["y"] = int(m_ar.group(2))
					
					self.arinfo.append(i)
	
	def getType(self):
		return "chp"
		
	def getFormat(self):
		return "chp"
		
	def __str__(self):
		return "ChaptersInfo - {2}".format(self.getType(), self.getFormat(), self.filename)


class VideoTrack(BaseTrack):
	def __init__(self, directory, filename):
		super().__init__(directory, filename)
	
	def getType(self):
		return "video"
		
	def getFormat(self):
		if self.ext == ".m2v":
			return "mpeg2"
		elif self.ext == ".ts":
			return "mpeg2ts"
		elif self.ext == ".d2v":
			return "dgindex"
		
	def __str__(self):
		return "{0} ({1}) - {2}".format(self.getType(), self.getFormat(), self.filename)

class AudioTrack(BaseTrack):
	def __init__(self, directory, filename):
		super().__init__(directory, filename)
		
		m = re.search('_([a-z]{3})[^a-zA-Z]', filename)
		
		if m:
			self.language = m.group(1)
		else:
			self.language = 'eng'
		
		m = re.search("DELAY ((-)?\d+)ms", filename)
		
		if m:
			self.delay = int(m.group(1))
		else:
			self.delay = 0
		
	def getType(self):
		return "audio"
	
	def getFormat(self):
		if self.ext == ".mp1" or self.ext == ".mp2" or self.ext == ".mp3":
			return "mpa"
		
	def __str__(self):
		return "{0} ({3} language: {1}, delay: {2} ms) - {4}".format(self.getType(), self.language, self.delay, self.getFormat(), self.filename)