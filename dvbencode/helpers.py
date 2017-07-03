# -*- coding: utf-8 -*-
from fractions import gcd
import configparser, io

def load_ini(file):
	cfg = configparser.ConfigParser()
	with io.open(file, 'r', encoding='utf_8_sig') as fp:
		cfg.readfp(fp)

	return cfg;

def write_ini(file, ini):
	with io.open(file, 'w', encoding='utf_8_sig') as fp:
		ini.write(fp)

def cull_sections(sections, main_start, main_end):
	sections_kept = []
	
	# Remove sections that are useless (ends during start buffer or starts during end buffer)
	for f in sections:
		if (f[0] > main_start or f[1] > main_start) and not f[0] > main_end:
			sections_kept.append(f)
			
	return sections_kept

def get_overlaping_frames(s1_start, s1_end, s2_start, s2_end):
	return max(min(s1_end, s2_end) - max(s1_start, s2_start), 0)

def calculate_sar(width, height, x, y):
	sar = [float(height) * float(x), float(width) * float(y)]
	
	divisor = gcd(sar[0], sar[1])
	
	return ':'.join([str(int(sar[0] / divisor)), str(int(sar[1] / divisor))])

def get_ar_sections(ChpInfo, last_frame):
	last_start = None
	last_ar = None
	
	ar_sections = []

	# Calculate sections for aspect rations
	for ar in ChpInfo.arinfo:
		if last_start != None:
			ar_sections.append({
				"start": last_start,
				"end": ar["start"] - 1,
				"x": last_ar["x"],
				"y": last_ar["y"]
			})
		
		last_start = ar["start"]
		last_ar = {"x": ar["x"], "y": ar["y"]}
		
	ar_sections.append({
		"start": last_start,
		"end": last_frame,
		"x": last_ar["x"],
		"y": last_ar["y"]
	})
	
	return ar_sections

def split_sections_ar(sections, ar_sections, only_dominant_ar = True):
	total_frames_ar = {}
	total_frames = 0
	
	sections_new = []
	
	for ar in ar_sections:
		for section in sections:
			arindex = "{0}/{1}".format(ar["x"], ar["y"])
			
			start = max(ar["start"], section[0])
			end = min(ar["end"], section[1])
			
			frames = max(end - start, 0)
			
			if start < end:	
				sections_new.append([start, end, "{0}/{1}".format(ar["x"], ar["y"])])
				
			if not arindex in total_frames_ar:
				total_frames_ar[arindex] = {
					"x": ar["x"],
					"y": ar["y"],
					"frames": frames
				}
			else:
				total_frames_ar[arindex]["frames"] = total_frames_ar[arindex]["frames"] + frames
				
	dominant_ar = None
				
	for ar in total_frames_ar:
		if dominant_ar == None or dominant_ar["frames"] < total_frames_ar[ar]["frames"]:
			dominant_ar = total_frames_ar[ar]
			
	if only_dominant_ar:
		sections_new = trim_sections_ar(sections_new, dominant_ar)
				
	return [sections_new, dominant_ar]

def trim_sections_ar(sections, ar):
	arindex = "{0}/{1}".format(ar["x"], ar["y"])
	
	sections_kept = []
	
	for f in sections:
		if f[2] == arindex:
			sections_kept.append(f)
			
	return sections_kept