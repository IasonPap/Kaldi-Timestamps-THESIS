#!/usr/bin/python

# Copyright 2017  Speech Lab, EE Dept., IITM (Author: Srinivas Venkattaramanujam)

import sys

arkFilePath=sys.argv[1]
audioDurationRange=10 # in seconds
frameLength = 10 # in ms
# number of frames in audioDurationRange
SegmentFrameNumber = int(audioDurationRange * 1000 / frameLength)
with open(arkFilePath) as f:
	contents=f.read()
# print '~~~\nsplit_vad.py:  '
with open("data/local/tmp_files/log/vad.log","w") as f:
	f.write(contents)
	f.write("\n  framecount: {}".format(len(contents)))
i=0 # the i-th frame
segcount=0
framecount=0
# print '	length: ', len(contents)
while i < len(contents):
	try:
		# k = how many frames away from the 10sec mark is the silence
		k=contents[i+SegmentFrameNumber:].index('0')
		
		segment=contents[i:i+SegmentFrameNumber+k]
	except ValueError:
		# print(contents[i+SegmentFrameNumber:])	
		segment=contents[i:]
		k=len(segment)-SegmentFrameNumber
		if k>0:
			print("ValueError: split_vad: there is no silence frames (0 energy)", k)
	# tunring the frame number to time(seconds): 
	# frameNum * 10ms = frameNum * 10 * 10^(-3) = frameNum / 100
	frameLengthSec = (frameLength / 1000) # for 10ms window = 0.01
	begin_time=i * frameLengthSec 
	end_time=(i+SegmentFrameNumber+k) * frameLengthSec
	if (end_time-begin_time) >= frameLengthSec: # duration should be atleast 10ms for feature extraction in my setup.
		if segcount < 10:
			print("	segment_0"+str(segcount)+" key_1 "+str(i/100.0)+" "+str((i+1000+k)/100.0))
		else:
			print("	segment_"+str(segcount)+" key_1 "+str(i/100.0)+" "+str((i+1000+k)/100.0))
	framecount+=len(segment)
	i += 1000+k
	# print("framecount:",framecount,"iter:",i)
	segcount+=1

# print ('	Framecount is',framecount)
# print "~~~"