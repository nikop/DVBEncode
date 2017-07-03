# -*- coding: utf-8 -*-
import subprocess, io, re
from fnmatch import fnmatch

def write_avs_open(fp, var, track):
	if track.getType() == "video":
		if track.getFormat() == "dgindex":
			fp.write('{0} = MPEG2Source("{1}", cpu=6)'.format(var, track.fullpath()))
		elif track.getFormat() == "mpeg2ts":
			fp.write('{0} = FFVideoSource("{1}")')
	elif track.getType() == "audio":
		if track.getFormat() == "mpa":
			fp.write('{0} = NicMPG123Source("{1}")'.format(var, track.fullpath()))
		
	fp.write("\n")

def write_dgindex_avs(filename, video, audio, template = "default", cuts = []):
	with io.open(filename, 'w', encoding='cp1252') as fp:
		
		write_avs_open(fp, "v", video)
		
		if audio != None:
			write_avs_open(fp, "a", audio)
			fp.write("AudioDub(v, a)\n")
			
			if audio.delay:
				fp.write("DelayAudio({0})\n".format(audio.delay / 1000.0))
			
		else:
			fp.write("v\n")
		i = 0
		
		# Write cuts
		if len(cuts) > 0:
			sects = []
			
			for cut in cuts:
				fp.write("sect{0} = trim({1}, {2}) # {3}\n".format(i, cut[0], cut[1], cut[2]))
				sects.append("sect{0}".format(i))
				i = i + 1
		
		
			fp.write((' ++ '.join(sects)) + "\n")
			
			fp.write("#" + ("\n#".join(sects)) + "\n")
			
		# Write template
		if template != None:
			
			with io.open(template, 'r', encoding='utf_8') as ftemplate:
				for line in ftemplate:
					fp.write(line)
					
def trims_to_chapters(filename):
	with io.open(filename, 'r', encoding='cp1252') as fp:
		avs = fp.read()
		
		sections = {}

		for s in re.findall("(sect\d+) = trim\((\d+)((\+|-)(\d+))?,\s?(-?\d+)((\+|-)(\d+)\))?", avs):			
			start = int(s[1]);
			
			if (s[3] == "+"):
				start += int(s[4])
			elif (s[3] == "-"):
				start -= int(s[4])
			
			end = int(s[5]);
			
			if (s[7] == "+"):
				end += int(s[8])
			elif (s[7] == "-"):
				end -= int(s[8])
				
			sections[s[0]] = [start, end]
			
		kept_sections = []
		
		for line in avs.split('\n'):
			if line.startswith("sect") and not 'trim' in line:
				kept_sections = [l.strip() for l in line.split('++')]
				break

		current_pos = 0
		
		chapters = [0]
		
		for s in kept_sections:
			sect = sections[s]
			
			if current_pos > 0:
				chapters.append(current_pos)
			
			if sect[1] < 0:
				current_pos += abs(sect[1])
			else:
				current_pos += sect[1] - sect[0] + 1
				
		return chapters