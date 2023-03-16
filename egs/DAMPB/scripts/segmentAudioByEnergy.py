#!/bin/python2
import os,sys
import numpy as np
from subprocess import check_call 
from main import WavSplitter
from function import debug
import re
#############
Usage = """Usage: python segmentAudioByEnergy.py <wavfile_dir> <dst_dir> <file> <Xsec> <segments_file_path>
This script segments an wav file from wavfile_dir directory
and splits it in segments of at least length Xsec, based on a threshold
of 0.1 * mean_energy_of_wavfile and outputs the segmented wav files
the segments file with the start and end times of the segments
in reference of the original wavfile.
	Input: 
wavdata_dir: path to the wavfile to be splitted
## song_number: the number of the song that we want (between)
dst_dir: where all the segments will be dumped
Xsec: the minimum duration of the segments that we'll split the wavfile 
	Output: 
wavfile segments together with the segments file 
to be dumped in wavfile_dir"""
###############
if len(sys.argv) != 3:
	print Usage
	sys.exit()


wavfile_dir = sys.argv[1]
dst_dir = sys.argv[2]
Xsec = sys.argv[3]
if not os.path.isdir(wavfile_dir): # checking if the wavfile_dir exists
	debug("{} is not an existing directory.".format(wavfile_dir))
	sys.exit()
# creating the dst dir if id doesn't exist, 
# while cecking if the string given is indeed a directory 
# aka in format string/string/..  
if re.match(r"[A-Za-z._-]+\/[A-Za-z._-]", dst_dir):
	check_call("mkdir -p " + dst_dir + os.sep + file, shell=True)	
else:
	debug("{} is not a valid destination directory.".format(dst_dir))
	sys.exit()


file = os.path.basename(wavfile_dir)
# segments_file_path: the path of the segments file in which 
# we'll append the segments start and end times
segments_file_path = os.path.join(dst_dir, file,"segments")
WavSplitter(wavfile_dir, dst_dir, file, Xsec, segments_file_path)
	