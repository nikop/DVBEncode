# DVBEncode

Toolset for semiautomatic encoding of mpeg2-ts files recorded by DVBViewer.

## Required Tools

### Avisynth

http://avisynth.nl

Installed anywhere. Using 32-bit version is recommended.

### DGIndex

https://www.videohelp.com/software/DGMPGDec

1. Install to folder "dgindex"
2. Remember to install its Avisynth Plugin

### avs2pipemod

http://avisynth.nl/index.php/Avs2pipemod

1. Install to folder "avs2pipe"

### comskip

http://www.kaashoek.com/comskip/

1. Install to folder "avs2pipe"

### ffmpeg

https://ffmpeg.org/

1. Install to folder "ffmpeg"

32-bit version is recommended. Must match bitness of Avisynth.

### tsmuxer

1. Install to folder "tsmuxer"

### ProjectX

1. Install to folder "ProjectX"

## Configuration

### Settings

Copy "settings.py.sample" as "settings.py". 

Edit Following settings as you want:

data_path: Path where store temporary files and avs templates.

unwanted_audios: array of audio languages to leave out (like dutch for Finnish broadcasts)

### Series

Series -folder contains information about name pattern for each series.
Name should be same as EPG Title for match to be success.

### Templates

Templates -folder contains used templates. 
Template is given as parameter to prepare tool and name doesn't have to match anything.

ini file contains actual encoding settings and used avs-template.

## Tools

There are three tools, that are ran in order to each file.

### Renamer

Command: ts_rename.py directory 

Renames original ts files according to pattern.

Duplicates are detected and renamed sequentially. 
They should be removed before running preprocss tool.

### Preprocess

Creates AVS templates

Command: encode_prepare.py *.ts --template default

#### Steps

1. File is demuxed using ProjectX to repair errors and fix audio/video sync.

2. Remuxed back to .ts using tsmuxer (mainly so comskip can use audio to determine cuts)

3. DGIndex is used to index .ts file for opening with avisynth

4. Comskip is ran to detect commercial breaks

5. ProjectX output and avs2pipe is used to determine video information like frame rate, lenght and aspect ratio. This is used in cutting.

6. AVS template is written

### Encode

Runs actual encoder (FFMpeg) using settings from template ini.

Command: encode_do.py

No parameter is used, all avs files in data_path are encdoded, if output file doesn't exists.