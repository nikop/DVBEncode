# -*- coding: utf-8 -*-
from fnmatch import fnmatch
from glob import glob
from configparser import ConfigParser
import argparse, os, os.path, shutil, io, re

from dvbencode.tools.DGIndex import DGIndex
from dvbencode.tools.mplex import mplex_remux
from dvbencode.tools.tsmuxer import tsmuxer_mux
from dvbencode.tools.ProjectX import ProjectX_demux
from dvbencode.tools.Comskip import Comskip
from dvbencode.tools.avs2pipe import avs2pipe_info
from dvbencode.tracks import get_streams
from dvbencode.tracktypes import getTrackInfo, VideoTrack, AudioTrack
from dvbencode.DVBViewer import ParseInfo, parse_episode_info
from dvbencode.helpers import cull_sections, get_overlaping_frames, calculate_sar, get_ar_sections, split_sections_ar, load_ini

import dvbencode.avs as avs, settings

skipStart = 4
skipEnd = 8

def prepare_file(file, template):
	(name, origext) = os.path.splitext(os.path.basename(file))
	target = settings.data_path + "\\" + name + "\\"
	
	if origext != ".ts":
		raise Exception("Only MPEG2-TS sources are supported.")
	elif os.path.exists(target):
		print("Skipping", name)
		return
	
	os.mkdir(target)
	
	# Load template
	tmpl = load_ini("templates\\{0}.ini".format(template))
	
	# Create meta file
	meta = ConfigParser()
	
	meta.add_section("Main")
	meta.add_section("Info")
	meta.add_section("Tags")
	meta.add_section("Video")
	
	meta.set("Main", "source", file)
	meta.set("Main", "temp_path", target)
	meta.set("Main", "template", template)
	
	avs_template = None
	
	# Use template for avs if specified
	if tmpl.has_option("Template", "avs"):
		avs_template = tmpl.get("Template", "avs")
	
	# Parse DVBViewer metadata file
	dvbInfo = ParseInfo(os.path.dirname(file) + "\\" + name + ".txt")

	epinfo = parse_episode_info(dvbInfo)
	
	# Try to parse from file name
	if epinfo["episode"] == -1:
		m = re.search("E(\d+)", name)
		
		if m:
			epinfo["episode"] = int(m.group(1))
	
	if epinfo["season"] == -1:
		m = re.search("S(\d+)", name)
		
		if m:
			epinfo["season"] = int(m.group(1))
	
	meta.set("Info", "title", dvbInfo["title"])
	meta.set("Info", "channel", dvbInfo["channel"])
	meta.set("Info", "desc", dvbInfo["desc"])
	meta.set("Info", "airtime", str(dvbInfo["start_time"]))
	meta.set("Info", "duration", str(dvbInfo["duration"]))
	
	meta.set("Tags", "series", epinfo["series"])
	meta.set("Tags", "season", str(epinfo["season"]))
	meta.set("Tags", "episode", str(epinfo["episode"]))
	meta.set("Tags", "name", epinfo["name"])
	
	# Demux & Fix using ProjectX
	ProjectX_demux(file, target)
	
	# Load Streams info
	(video, audio_main, extra_audios, ChpInfo) = get_streams(target, settings.unwanted_audios)
			
	# Remux for use with Comskip
	tsmuxer_mux(video, audio_main, target + "fixed.ts")
	
	# Remove demuxed video, will use using muxed as input
	os.remove(video.fullpath())
	
	# Create DGIndex for Avisynth
	if True:
		video = DGIndex(target + "fixed.ts", target + "dgindex")
	else:
		raise Exception("Unknown Format")
	
	# Remove Ads
	if True:
		sections = Comskip(target + "fixed.ts")
	else:
		sections = []
	
	# Write avs
	avs.write_dgindex_avs(target + "source.avs", video, audio_main, None)
	
	# Get info (fps, framesize)
	avsinfo = avs2pipe_info(target + "source.avs")
	
	# Calculate main area (without buffers)
	main_start = avsinfo["v:fps"] * 60 * skipStart
	main_end = int(avsinfo["v:frames"]) - avsinfo["v:fps"] * 60 * skipEnd
	
	# Use whole video, if not cutting
	if len(sections) == 0:
		sections.append([0, int(avsinfo["v:frames"]) - 1]);
	
	# Remove sections that are outside of recording area
	sections = cull_sections(sections, main_start, main_end)
	
	# Parse aspect ratio information
	ar_sections = get_ar_sections(ChpInfo, int(avsinfo["v:frames"]) - 1)
		
	(sections, dominant_ar) = split_sections_ar(sections, ar_sections)
	
	meta.set("Video", "ar", "{0}/{1}".format(dominant_ar["x"], dominant_ar["y"]))
	meta.set("Video", "audio", audio_main.fullpath())
	meta.set("Video", "fps", str(avsinfo["v:fps"]))
	
	avs.write_dgindex_avs(settings.data_path + "\\unchecked\\" + name + ".avs", video, audio_main, avs_template, sections)
	
	write_meta(settings.data_path + "\\unchecked\\" + name + ".ini", meta)
	
def write_meta(filename, meta):
	with io.open(filename, 'w', encoding='utf_8_sig') as fp:
		meta.write(fp)

if __name__ == '__main__':
	parser = argparse.ArgumentParser(description='prepare')
	parser.add_argument('file', metavar='FILE', type=str, help='files to process')
	parser.add_argument('--template', type=str, help='avs template', default="default")
	args = parser.parse_args()
	
	for file in glob(args.file):
		prepare_file(file, args.template)