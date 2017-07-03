# -*- coding: utf-8 -*-
import configparser, io, re
from datetime import datetime, timedelta

def parseTimeDelta(s):
    """Create timedelta object representing time delta
       expressed in a string
   
    Takes a string in the format produced by calling str() on
    a python timedelta object and returns a timedelta instance
    that would produce that string.
   
    Acceptable formats are: "X days, HH:MM:SS" or "HH:MM:SS".
    """
    if s is None:
        return None
    d = re.match(
            r'((?P<days>\d+) days, )?(?P<hours>\d+):'
            r'(?P<minutes>\d+):(?P<seconds>\d+)',
            str(s)).groupdict(0)
    return timedelta(**dict(( (key, int(value))
                              for key, value in d.items() )))

def ParseInfo(file):
    cfg = configparser.ConfigParser()
    with io.open(file, 'r', encoding='utf_8_sig') as fp:
        cfg.readfp(fp)

    info = {
        'channel': cfg["Media"]["Channel"],
        'title': cfg["0"]["Title"],
        'desc': cfg["0"]["Info"],
        'start_time': datetime.strptime(cfg["0"]["Date"] + " " + cfg["0"]["Time"], "%d.%m.%Y %H:%M:%S"),
        'duration': parseTimeDelta(cfg["0"]["Duration"]),
        'end_time': None
    }
    info["end_time"] = info["start_time"] + info["duration"]

    return info

def parse_episode_info(info):
    # Jakso n. Jakso nimi.
    # Osa n. Jakso nimi.
    # Osa n: Jakso nimi
	# n: Jakso nimi
    j1 = re.compile("(?:Jakso |Osa )?(\d+)(?:\.|:) (?:\"?)([^\.^\"]+?)(?:\"?)(\.|$)")
    # Osa n/n: Jakson nimi
    # n/n: Jakson nimi
    # Osa 1/101. Jakson nimi
    j2 = re.compile("(?:Osa )?(\d+)/(\d+)(?:[:.]) ([^\.]+)\.")
    # Osa n: "Jakso nimi"
    j3 = re.compile("Osa (\d+): \"([^\"]+)\"")

    epinfo = {
        'series': info["title"],
        'season': -1,
        'episode': -1,
        'name': ''
    }

    m1 = j1.search(info["desc"])
    m2 = j2.search(info["desc"])
    m3 = j3.search(info["desc"])
    
    if m1:
        epinfo["episode"] = int(m1.group(1))
        epinfo["name"] = m1.group(2)
        
    elif m2:
        epinfo["episode"] = int(m2.group(1))
        epinfo["name"] = m2.group(3)
        
    elif m3:
        epinfo["episode"] = int(m3.group(1))
        epinfo["name"] = m3.group(2)
    else:
        m = re.search("(\.|!|\?)(\s|$)", info["desc"])
            
        if m:
            epinfo["name"] = info["desc"][0:m.start() + 1].strip('. ')
        else:
            epinfo["name"] = info["desc"]
            
    epinfo["series"] = re.sub('\((S|\d{1,2})\)$', '', epinfo["series"]).strip()
            
    return epinfo