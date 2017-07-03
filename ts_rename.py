# -*- coding: utf-8 -*-
from fnmatch import fnmatch
from glob import iglob, glob
from configparser import ConfigParser
import argparse, os, os.path, shutil, io, re

from dvbencode.helpers import load_ini
from dvbencode.DVBViewer import ParseInfo, parse_episode_info
from dvbencode.tools.avs2pipe import avs2pipe_info

def SanitizeFileName(file: str, repl: str):
    """Remove unsupported characters"""
    return re.sub("[?<>:\"\\/|* ]", repl, file)

def GetNextFreePrefix(outdir, prefix):
    """Finds free prefix (no other files starting with same name)"""
    i = 0
    p = prefix
    while len(glob(os.path.join(outdir, p + "*"))) != 0:
        i += 1
        p = prefix + "_" + str(i)
    return p

def RenameFile(file):
    """Renames a single file"""
    src, ext = os.path.splitext(file)

    info = None
    
    if os.path.exists(src + ".txt"):
        info = ParseInfo(src + ".txt")

    if info == None:
        return False # Raise?
    
    epinfo = parse_episode_info(info)
    
    series = None

    for i in iglob("series/*.ini"):
        s = load_ini(i)
        
        if s.get("Series", "name") == epinfo["series"]:
            series = s
            break

    if series == None:
        return False
    
    if "directory" in series["Series"]:
        directory = series.get("Series", "directory")
    else:
        directory = os.path.dirname(file)

    # TODO: Find episode
    
    # Ensure that target exists
    if not os.path.exists(directory):
        os.makedirs(directory)
        
    epcode = ""
    
    for i in s:
        if i == "DEFAULT" or i == "Series":
            continue
       
        if re.sub('[^a-zöä ]', '', s.get(i, "name").lower()) != re.sub('[^a-zöä ]', '', epinfo["name"].strip().lower()):
            continue
			
        curep = s[i]
		
        if "target" in curep:
            curep = s[curep["target"]]
        
        epinfo["season"] = int(curep['season'])
        epinfo["episode"] = int(curep['episode'])
        epinfo["name"] = curep['name']
  
    if epinfo["season"] != -1:
        epcode += "S{0:02d}".format(epinfo["season"])
        
    if epinfo["episode"] != -1:
        epcode += "E{0:02d}".format(epinfo["episode"])
        
    rename_opts = {
        'series': epinfo["series"],
        'episode_code': epcode,
    }
    
    if epcode == "":
        return False
    
    renames = {}
    
    name = SanitizeFileName(
        series.get("Series", "filename").format(**rename_opts),
        '_'
    )
    
    if os.path.basename(file).startswith(name):
        print(file, "Already renamed")
        return
    
    newname = GetNextFreePrefix(
        directory, 
        name
    )

    # Rename all files with same name, but different extension
    for source in iglob(src + ".*"):
        name, ext = os.path.splitext(source)
        target = os.path.join(directory, newname + ext)
        shutil.move(source, target)
        renames[source] = target
        #print(target)

    return renames

def RenameFolder(file_mask):
    for file in iglob(file_mask):
        if RenameFile(file):
            print(file, "was renamed")
        else:
            print(file, "skipped")

	
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='gsf')
    parser.add_argument('file', metavar='FILE', type=str, help='files to process')
    parser.add_argument('--template', type=str, help='avs template', default="default")
    args = parser.parse_args()
	
    RenameFolder(args.file)

