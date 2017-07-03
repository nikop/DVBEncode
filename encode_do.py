# -*- coding: utf-8 -*-
from configparser import ConfigParser
from glob import glob
import argparse, os, os.path, shutil, io, re, subprocess

from dvbencode.helpers import load_ini
from dvbencode.tools.avs2pipe import avs2pipe_info
import dvbencode.avs as avs, settings

def encode_file(file):
	source_dir = os.path.dirname(file)
	(name, origext) = os.path.splitext(os.path.basename(file))
	
	if origext != ".avs":
		raise Exception("Only AVS files can be encoded.")
	
	meta = load_ini("{0}\{1}.ini".format(source_dir, name))
	tmpl = load_ini("templates\{0}.ini".format(meta.get("Main", "template")))
	
	epcode = ""
	
	if int(meta.get("Tags", "season")) != -1:
		epcode += "S{0:02d}".format(int(meta.get("Tags", "season")))
	if int(meta.get("Tags", "episode")) != -1:
		epcode += "E{0:02d}".format(int(meta.get("Tags", "episode")))
	
	encode_opts = {
		'orig': name,
		'series': meta.get("Tags", "series"),
		'episode_code': epcode,
		'episode_name': meta.get("Tags", "name"),
		'airtime': meta.get("Info", "airtime"),
		'title': '',
		'input': file,
		'aspect': meta.get("Video", "ar"),
		'fps': float(meta.get("Video", "fps")),
		'output': ''
	}
	
	encode_opts['output'] = tmpl.get("Output", "name").format(**encode_opts)
	encode_opts['title'] = re.sub('\s+', ' ', tmpl.get("Tags", "title").format(**encode_opts)).strip()

	if os.path.exists(encode_opts['output']):
		print("Skipping {0} output ({1}) exists".format(name, encode_opts["output"]))
		return False
	
	avsinfo = avs2pipe_info(file)
	
	fps = avsinfo["v:fps"]
	
	if 'Chapters' in tmpl:
		chapSettings = tmpl['Chapters']
		
		chapters = [0]
		
		if 'use_trims' in chapSettings and chapSettings.getboolean('use_trims'):
			chapters = avs.trims_to_chapters(file)
		
		if 'chapters' in chapSettings:
			for s in chapSettings['chapters'].split(','):
				t = s[-1]
				p = int(s[0:-1])
					
				if t == 's':
					p = int(p * fps)
					
				if p < 0:
					p = int(avsinfo['v:frames']) + p
				
				chapters.append(p)
				
			chapters.sort()

		# Write chapters file
		i = 1
		
		encode_opts['chapters_frames'] = ','.join([str(f) for f in chapters])
		encode_opts['chapters_file'] = meta['Main']['temp_path'] + 'chapters.txt'
		
		with io.open(encode_opts['chapters_file'], 'w', encoding='ascii') as fp:
			for ch in chapters:
				fp.write("CHAPTER{n:02d}={ts}\nCHAPTER{n:02d}NAME=Chapter {n}\n".format(n=i, ts=format_timestamp(ch / fps)))
				i += 1
	
	current = tmpl["Encoder"]
	
	while current != None:
		if current["codec"] == 'ffmpeg':
			cmd = current["cmd"].format(**encode_opts)
			
			subprocess.call("ffmpeg\\ffmpeg.exe {0}".format(cmd), shell=True)
			
		elif current["codec"] == 'custom':
			cmd = current["cmd"].format(**encode_opts)
			
			subprocess.call('"{0}" {1}'.format(current['program'], cmd), shell=True)
		else:
			raise Exception("Unsupported encoder")
		
		if 'next' in current:
			current = tmpl[current['next']]
		else:
			current = None
	
	return True


def format_timestamp(s):
	m = s // 60
	s = s % 60
	h = m // 60
	m = m % 60

	return '{:02.0f}:{:02.0f}:{:06.3f}'.format(h, m, s)

if __name__ == '__main__':
	#parser = argparse.ArgumentParser(description='gsf')
	#parser.add_argument('file', metavar='FILE', type=str, help='files to process')
	#args = parser.parse_args()
	
	# Ensure files added during encoding gets checked
	while True:
		i = 0
		
		for file in glob(settings.data_path + "\\*.avs"):
			if encode_file(file):
				i = i + 1
			
		if i == 0:
			break