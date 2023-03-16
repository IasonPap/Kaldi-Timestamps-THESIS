######################################
# This is the code base for automatically obtaining aligned lyrics for solo-singing
# in Smule's Sing! karaoke DAMP dataset. It provides a cleaner annotated dataset.
# Please refer to the following paper for more details:
# Chitralekha Gupta, Rong Tong, Haizhou Li, and Ye Wang, "Automatic Sung-Lyrics Data Annotation"
# Accepted in ISMIR 2018.
######################################

# import speech_recognition as sr
import os
import sys
import numpy as np
# from pydub import AudioSegment
import scipy.signal
import scipy.io.wavfile
import matplotlib.pylab as plt
import re
from levenshtein import *
# from httplib import BadStatusLine
# import wave
# import inflect
# from shutil import copyfile
from copy import deepcopy
from subprocess import check_call as subpr_call
from tqdm import tqdm
from functions import *


plot = False
NFFT = 512 # NFFT * 1.0 / fs = 0.128 sec window orginal value: 512
fs = 16000 # sample rate
silence_wav = os.path.join("DAMPB_6903","silence_2seconds.wav")
LOGGING_DIR = "LOGS"
if not os.path.exists(LOGGING_DIR):
	os.mkdir(LOGGING_DIR)

	#########################################################################
def M4AtoWAV16k(M4Afile,WAVfile):
	# Converts .m4a to .wav
	# Input: m4a file, output wavfile name/path
	# Output: wavfile
	#########################################################################
	
	channels = 1 
	overwrite_output = "-y" #this overwrites already existing files. 
	#Simply remove it from command list to not overwrite. 
	command_list = ["ffmpeg", "-i", M4Afile,
					overwrite_output, "-ac",str(channels), "-ar",str(fs), 
					WAVfile]
	subpr_call(command_list)
	# m4a_version = AudioSegment.from_file(M4Afile)
	# m4a_version.export(WAVfile, format="wav")
	# fs_raw,raw_wav_data = scipy.io.wavfile.read(WAVfile)
	# n = raw_wav_data.shape[0]
	# y = np.floor(np.log2(n))
	# nextpow2 = int(np.power(2, y + 1))
	# # print nextpow2, n 
	# # print '#####\t'
	# # print raw_wav_data
	# raw_wav_data = np.pad(raw_wav_data, ((0, nextpow2 - n)), mode='constant')
	# resampled_signal = scipy.signal.resample(raw_wav_data/32768,fs*len(raw_wav_data)*1/fs_raw)
	# if max(resampled_signal)>=1.0:
	# 	resampled_signal = resampled_signal*0.9
	# scipy.io.wavfile.write(WAVfile,16000,resampled_signal)

	#########################################################################
def InitialFinalSilenceRemoved(sig):
	# Removes beginning and end silence periods of a wavfile
	# Input: sig, i.e. wavfile
	# Output: new_sig, i.e. wavfile without beginning and end silence periods
	#########################################################################
	window = NFFT
	
	hop = window/2
	energy = []
	i = 0
	energy_index = []
	sample_duration = 1.0/fs # in seconds
	while i<(len(sig)-window):

		chunk = sig[i:i+window][np.newaxis]
		# print chunk.T
		energy.append(chunk.dot(chunk.T)[0][0])
		energy_index.append(i)
		i = i+hop

	# print "sample rate: {}\tsignal length: {}\t Number of windows in sig: {}\n".format(
	# 											fs,len(sig),len(sig)/window)
	# print sig[-10:-1]
	
	energy = np.array(energy)
	energy_thresh = 0.1*np.mean(energy)
	significant_indices = np.where(energy>energy_thresh)[0]


	if significant_indices[0] == 0:
		start_point_sample = 0
		start_time_sample = 0
	else:
		start_point_sample = (significant_indices[0]-1)*hop
		start_time_sample = (significant_indices[0]-1)*hop*sample_duration
	if significant_indices[-1] == len(energy)-1:
		end_point_sample = len(energy)*hop
		end_time_sample = len(energy)*hop*sample_duration
	else:
		end_point_sample = (significant_indices[-1]+1)*hop
		end_time_sample = (significant_indices[-1]+1)*hop*sample_duration
	new_sig = sig[start_point_sample:end_point_sample+1]
	StartEnd_time_of_sample = [start_time_sample,end_time_sample]
	debug("signal -> start time: %.2f & end time: %.2f \n"%(StartEnd_time_of_sample[0], StartEnd_time_of_sample[1]))
	# print "signal -> start time: %.2f & end time: %.2f \n"%(StartEnd_time_of_sample[0], StartEnd_time_of_sample[1])
	if plot:
		plt.figure('figure from InitialFinalSilenceRemoved')
		plt.subplot(3,1,1)
		plt.plot(range(len(sig)),sig)
		plt.ylabel('amplitude')
		plt.title('Remove initial and final silences')
		plt.subplot(3,1,2)
		plt.plot(energy_index,energy)
		plt.ylabel('energy')
		plt.stem([start_point_sample,end_point_sample],[5,5],'k')
		plt.subplot(3,1,3)
		plt.plot(new_sig)
		plt.ylabel('amplitude')
		plt.xlabel('sample number')
		plt.show()
	return (new_sig, StartEnd_time_of_sample)

	#########################################################################

def WavSplit(fs,initialsegmentfolder,file, sig,boundary,hop, start_time, end_time):
	# Splits wavfile into segments based on boundaries provided
	# Input: fs: sampling frequency
	#        initialsegmentfolder: the folder location where all the wav segments are dumped
	#        file: the wavfile to be split into segments
	#        sig: the wavfile data in an array
	#        boundary: pause-based segment boundaries
	#        hop: the hop size for calculating energy. The boundary values are based on this hop size.
	#  start_time: the starting time of the wav date
	#	 end_time: the ending time of the wav data
	# Output: wavfile segments from 0 to N in initialsegmentfolder
	#########################################################################

	ind = 0
	start = 0
	for elem in boundary:

		if start==0 and elem!=0:
			segment = sig[start*hop:elem*hop]
			start = elem
		elif start!=0:
			end = elem
			segment = sig[start * hop:end * hop]
			start=elem
		else:
			start = elem
			continue
		ind = ind + 1
		if ind<10:
			WAVfile = initialsegmentfolder+os.sep+file.replace('.wav','_0'+str(ind)+'.wav')
		else:
			WAVfile = initialsegmentfolder + os.sep + file.replace('.wav', '_' + str(ind) + '.wav')
		debug("calling InitialFinalSilenceRemoved for segment %d"% ind)
		
		segment, start_end_time = InitialFinalSilenceRemoved(segment)
		start_end_time[0] += start_time
		start_end_time[1] += end_time
		debug("~~~~~~~SEGMENTS --> start time: %.2f  end time: %.2f \n"  %(start_end_time[0],start_end_time[1]))
		

		# to avoid less than 2 seconds sounds
		if len(segment)*sample_duration<2:
			continue
		if max(segment)>=1.0:
			print "exceeding beyond 1.0", max(segment)
			if max(segment)<=1.2:
				segment = segment*0.8
				scipy.io.wavfile.write(WAVfile, fs, np.array(segment * 32678.0, dtype=np.int16))
			else:
				scipy.io.wavfile.write(WAVfile, fs, np.array(segment, dtype=np.int16))
		else:
			scipy.io.wavfile.write(WAVfile, fs, np.array(segment*32678.0,dtype=np.int16))

	#last segment
	segment = sig[elem * hop:]
	ind = ind + 1
	if ind < 10:
		WAVfile = initialsegmentfolder + os.sep + file.replace('.wav', '_0' + str(ind) + '.wav')
	else:
		WAVfile = initialsegmentfolder + os.sep + file.replace('.wav', '_' + str(ind) + '.wav')
	debug("calling InitialFinalSilenceRemoved for segment %d"% ind)
	# print "#WavSplit calling InitialFinalSilenceRemoved for segment %d"% ind
	segment, start_end_time  = InitialFinalSilenceRemoved(segment)
	start_end_time[0] += start_time
	start_end_time[1] += end_time
	debug("~~~SEGMENTS --> start time: %.2f  end time: %.2f \n"  %(start_end_time[0],start_end_time[1]))
	# print "#WavSplit~~~SEGMENTS --> start time: %.2f  end time: %.2f \n"  %(start_end_time[0],start_end_time[1])

	if max(segment) >= 1.0:
		print "exceeding beyond 1.0", max(segment)
		if max(segment) <= 1.2:
			segment = segment * 0.8
			scipy.io.wavfile.write(WAVfile, fs, np.array(segment * 32678.0, dtype=np.int16))
		else:
			scipy.io.wavfile.write(WAVfile, fs, np.array(segment, dtype=np.int16))
	else:
		scipy.io.wavfile.write(WAVfile, fs, np.array(segment * 32678.0, dtype=np.int16))

	return start_end_time
	#########################################################################

def WavSplitMinXsec(initialsegmentfolder,file, sig,boundary,hop, Xsec, sample_duration, file_start_time, file_end_time):
	# Splits wavfile into X seconds segments based on boundaries provided
	# Input: initialsegmentfolder: the folder location where all the wav segments are dumped
	#        file: the wavfile to be split into segments
	#        sig: the wavfile data in an array
	#        boundary: pause-based segment boundaries
	#        hop: the hop size for calculating energy. The boundary values are based on this hop size.
	#		sample_duration: the duration of 1 sample in seconds
	# 		Xsec: the minimum duration of the segments that we'll split the wavfile 
	# file_start_time: the starting time of the entire wav data
	# file_end_time: the ending time of the entire wav data
	# Output: wavfile segments from 0 to N in initialsegmentfolder
	# 		segments_times: a list of tuples (start_seg_time, end_seg_time) 
	# 						for the wavfile that was segmented
	#########################################################################
	ind = 0
	start = 0
	seg_start_time, seg_end_time = 0,0
	segments_times = []
	
	for elem in boundary:
		
		if start==0 and elem!=0:
			
			duration = (elem -start)*hop*sample_duration
			# debug("start==0 and elem!=0")
			# print elem, start, hop, sample_duration
			# debug("the duration of segment is: %.2f"%duration)
			
			if duration < Xsec:
				# print "\t\t\t\t\t\t SMALLER SEG THAN %d" %Xsec
				continue
			segment = sig[start*hop:elem*hop]
			start = elem
		elif start!=0:
			duration = (elem -start)*hop* sample_duration
			# debug("start!=0")
			# print elem, start, hop, sample_duration
			# debug("the duration of segment is: %.2f"%duration)
			
			if duration < Xsec:
				continue
			end = elem
			segment = sig[start * hop:end * hop]
			start=elem
		else:
			start = elem
			continue
		
		ind += 1
		debug("~~~~~~\t SEGMENT %d \t~~~~~~~~~~"%ind)
		if ind < 10:
			WAVfile = initialsegmentfolder+os.sep+file.replace('.wav','_0'+str(ind)+'.wav')
		else:
			WAVfile = initialsegmentfolder + os.sep + file.replace('.wav', '_' + str(ind) + '.wav')
		debug("calling InitialFinalSilenceRemoved for segment %d"% ind)
		# print "#WavSplitMinXsec calling InitialFinalSilenceRemoved for segment %d"% ind
		segment, start_end_time_seg  = InitialFinalSilenceRemoved(segment)
		debug("file_start_time: %.2f file_end_time: %.2f"%(file_start_time,file_end_time))
		if ind == 1:
			seg_start_time = file_start_time + start_end_time_seg[0] # adding the file start time with the start of 1st segment
			seg_end_time = file_start_time + start_end_time_seg[1] 	# adding the file start time with the end of 1st segment
		else:
			seg_start_time = seg_end_time + start_end_time_seg[0] # adding the end time of the previous segment with the start of current
			seg_end_time = seg_end_time + start_end_time_seg[1]   # adding the end time of the previous segment with the end of current
		
		
		debug("~~~SEGMENTS --> start time: %.2f  end time: %.2f"  % (start_end_time_seg[0], start_end_time_seg[1]))
		segment_start_end = (seg_start_time,seg_end_time)
		segments_times.append(segment_start_end)
		debug(segments_times[-1])
		# to avoid less than 2 seconds sounds
		if len(segment)*sample_duration<2:
			continue

		
		if max(segment)>=1.0:
			print "exceeding beyond 1.0",max(segment)
			if max(segment)<=1.2:
				segment = segment*0.8
				scipy.io.wavfile.write(WAVfile, fs, np.array(segment * 32678.0, dtype=np.int16))
			else:
				scipy.io.wavfile.write(WAVfile, fs, np.array(segment, dtype=np.int16))
		else:
			scipy.io.wavfile.write(WAVfile, fs, np.array(segment*32678.0,dtype=np.int16))

	# my little test to catch the case where the boundary list, with the 
	if boundary == []:
		log_file = os.path.join(LOGGING_DIR,"WavSplitMin{}sec.txt".format(Xsec))
		with open(log_file,"a+") as flog:
			flog.write("~~~~ERROR: No Boundary = {} ...for file {} ###Didn't segment it.\n".format(boundary,file))
		return "No Boundary"
	####last segment###
	debug("~~~~~~\tLAST SEGMENT\t~~~~~~~~~~")
	duration = (len(sig)-elem*hop)*sample_duration
	if duration < Xsec: 
		return segments_times
	segment = sig[elem * hop:]
	ind = ind + 1
	if ind < 10:
		WAVfile = initialsegmentfolder + os.sep + file.replace('.wav', '_0' + str(ind) + '.wav')
	else:
		WAVfile = initialsegmentfolder + os.sep + file.replace('.wav', '_' + str(ind) + '.wav')

	debug("calling InitialFinalSilenceRemoved for segment %d"% ind)
	segment, start_end_time  = InitialFinalSilenceRemoved(segment)
	
	seg_start_time = seg_end_time + start_end_time_seg[0] # adding the end time of the previous segment with the start of last segment
	seg_end_time = seg_end_time + start_end_time_seg[1]   # adding the end time of the previous segment with the end of last segment	
	debug("~~~~SEGMENTS --> start time: %.2f  end time: %.2f"  %(start_end_time[0],start_end_time[1]))
	segment_start_end = (seg_start_time,seg_end_time)
	
	
	segments_times.append(segment_start_end)
	
	# writing the audio segments
	if max(segment) >= 1.0:
		print "exceeding beyond 1.0 \t",max(segment)
		if max(segment) <= 1.2:
			segment = segment * 0.8
			scipy.io.wavfile.write(WAVfile, fs, np.array(segment * 32678.0, dtype=np.int16))
		else:
			scipy.io.wavfile.write(WAVfile, fs, np.array(segment, dtype=np.int16))
	else:
		scipy.io.wavfile.write(WAVfile, fs, np.array(segment * 32678.0, dtype=np.int16))

	return segments_times
	#########################################################################

def SplitWavdataByEnergy(sig,initialsegmentfolder,file,Xsec, sample_duration,file_start_time, file_end_time):
	# Splits wav data based on energy, i.e. pauses
	# Input: sig: the wavfile data in an array
	#        initialsegmentfolder: the folder location where all the wav segments are dumped
	#        file: the wavfile to be split into segments
	# 		 Xsec: the minimum duration of the segments that we'll split the wavfile 
	#		sample_duration: the duration of 1 sample in seconds
	#  file_start_time: the starting time of the entire wav file
	#	 file_end_time: the ending time of the entire wav file
	# Output: wavfile segments from 0 to N in initialsegmentfolder
	#		segments_times: a list of tuples (start_seg_time, end_seg_time) 
	# 						for the wavfile that was segmented
	#########################################################################

	window = NFFT
	hop = window / 2
	energy = []
	i = 0
	energy_index = []
	debug("sample duration: {}\tsignal length: {}\t Number of windows in sig: {}\n".format(
												sample_duration,len(sig),len(sig)/window))
	# print sig
	while i < (len(sig) - window):
		chunk = sig[i:i + window][np.newaxis]
		energy.append(chunk.dot(chunk.T)[0][0])
		energy_index.append(i)
		i = i + hop

	energy = np.array(energy)
	energy_thresh = 0.1*np.mean(energy) #mean because there might be some spurious peak in energy
	indiceswithlowenergy = np.where(energy <= energy_thresh)
	timeinstance_withlowenergy = indiceswithlowenergy[0] * hop*sample_duration

	### retain those silences which are greater than or equal to 0.2 seconds, and hence find valid silent segments
	sil_dur_cap = 0.2
	num_samp_sil_dur_cap = np.floor(sil_dur_cap*fs*1.0/hop)
	lowenergyindices = indiceswithlowenergy[0]

	validlowenergy_subarray = []
	validlowenergyarray = []
	debug("num_samp_sil_dur_cap = {}".format(num_samp_sil_dur_cap))
	debug("len(lowenergyindices): {}".format(len(lowenergyindices)))
	for ind in range(len(lowenergyindices)-1):
		diff = lowenergyindices[ind+1]-lowenergyindices[ind]
		if diff>1:
			##to account for breathy regions## BUT THIS PIECE OF CODE SPLITS FROM CONSONANTS ## NOT desirable
			# if diff>np.floor(0.2*fs*1.0/hop) and diff<np.floor(0.3*fs*1.0/hop): #0.2-0.3 seconds of breathy voice allowed
			#     for i in range(lowenergyindices[ind],lowenergyindices[ind+1],1):
			#         validlowenergy_subarray.append(i)
			#     continue
			#################################
			if validlowenergy_subarray:
				validlowenergy_subarray.append(lowenergyindices[ind])
				if len(validlowenergy_subarray)>=num_samp_sil_dur_cap:
					validlowenergyarray=validlowenergyarray+validlowenergy_subarray
			validlowenergy_subarray = []
			continue
		validlowenergy_subarray.append(lowenergyindices[ind])
	if len(validlowenergy_subarray) >= num_samp_sil_dur_cap:
		validlowenergyarray = validlowenergyarray + validlowenergy_subarray
	validlowenergy_subarray = []

	#########################
	##Finding center of valid silent regions. These will be boundaries of phrases/segments/song lines
	# print '\nlen(validlowenergyarray): ',len(validlowenergyarray)
	boundary = []
	
	for ind in range(len(validlowenergyarray) - 1):
		diff = validlowenergyarray[ind + 1] - validlowenergyarray[ind]
		if diff > 1:
			if validlowenergy_subarray:
				validlowenergy_subarray.append(validlowenergyarray[ind])
				boundary.append(validlowenergy_subarray[0]+((validlowenergy_subarray[-1]-validlowenergy_subarray[0])/2))
			validlowenergy_subarray = []
			# print '\nSplitWavByEnergy: I\'m before Continue. Current iter is: ',ind,'\n'
			continue
		validlowenergy_subarray.append(validlowenergyarray[ind])
	if validlowenergy_subarray:
		boundary.append(validlowenergy_subarray[0] + ((validlowenergy_subarray[-1] - validlowenergy_subarray[0]) / 2))
	print '#SplitWavdataByEnergy: len(boundary): ', len(boundary)

	segments_times = WavSplitMinXsec(initialsegmentfolder,file, sig, boundary,hop,Xsec, sample_duration, file_start_time, file_end_time)

	##########################
	if plot:
		plt.figure("figure from SplitWavdataByEnergy 1")
		plt.subplot(2,1,1)
		plt.plot(range(len(sig)),sig)
		plt.ylabel('amplitude')
		plt.subplot(2, 1, 2)
		plt.plot(energy_index,energy)
		plt.stem(indiceswithlowenergy[0]*hop, 5*np.ones(len(indiceswithlowenergy[0])), 'k')
		plt.ylabel('energy')
		plt.show()

		plt.figure("figure from SplitWavdataByEnergy 2")
		plt.title('amplitude vs. time')
		plt.subplot(2, 1, 1)
		plt.plot(np.array(range(len(sig)))*sample_duration, sig)
		plt.ylabel('amplitude')
		plt.subplot(2, 1, 2)
		plt.plot(np.array(energy_index)*sample_duration, energy)
		plt.stem(timeinstance_withlowenergy, 5 * np.ones(len(indiceswithlowenergy[0])), 'k')
		plt.ylabel('energy')
		plt.show()

	if plot:
		plt.figure("figure from SplitWavdataByEnergy 3")
		plt.subplot(3,1,1)
		plt.plot(range(len(sig)),sig)
		plt.ylabel('amplitude')
		plt.subplot(3, 1, 2)
		plt.plot(energy_index,energy)
		plt.stem(indiceswithlowenergy[0]*hop, 5*np.ones(len(indiceswithlowenergy[0])), 'k')
		plt.ylabel('energy')
		plt.subplot(3, 1, 3)
		plt.plot(energy_index, energy)
		plt.stem(np.array(validlowenergyarray) * hop, 10 * np.ones(len(validlowenergyarray)), 'k')
		plt.ylabel('energy')
		plt.show()

		plt.figure("figure from SplitWavdataByEnergy 4")
		plt.title('amplitude vs. time')
		plt.subplot(2, 1, 1)
		plt.plot(np.array(range(len(sig)))*sample_duration, sig)
		plt.ylabel('amplitude')
		plt.subplot(2, 1, 2)
		plt.plot(np.array(energy_index)*sample_duration, energy)
		plt.stem(np.array(validlowenergyarray) * hop*sample_duration, 5 * np.ones(len(validlowenergyarray)), 'k')
		plt.ylabel('energy')
		plt.show()

	if plot:
		plt.figure('amplitude vs. time')
		plt.subplot(2, 1, 1)
		plt.plot(np.array(range(len(sig)))*sample_duration, sig)
		plt.ylabel('amplitude')
		plt.subplot(2, 1, 2)
		plt.plot(np.array(energy_index)*sample_duration, energy)
		plt.stem(np.array(validlowenergyarray) * hop*sample_duration, 1 * np.ones(len(validlowenergyarray)), 'k')
		plt.stem(np.array(boundary) * hop * sample_duration, 10 * np.ones(len(boundary)), 'r')
		plt.ylabel('energy')
		plt.show()
	return segments_times

	#########################################################################

def WavSplitter(wavfile,initialsegmentfolder,file,Xsec, segments_file_path):
	# Wrapper for splitting wavfiles
	# Input: wavfile: path to the wavfile to be splitted
	#        initialsegmentfolder: where all the segments will be dumped
	#        file: name of the wavfile
	#		 Xsec: the minimum duration of the segments that we'll split the wavfile 
	# 		segments_file_path: the path of the segments file in which we'll append the segments start and end times
	# Output: wavfile segments to be dumped in initialsegmentfolder
	################################################################
	sr, wav_data = scipy.io.wavfile.read(wavfile)
	wav_data = wav_data/32768.0 #NOT doing this step as the wav file written is already between -1 to +1
	wav_data = wav_data - np.mean(wav_data)  # remove DC offset
	wav_data, start_end_time  = InitialFinalSilenceRemoved(wav_data)
	debug(start_end_time)
	file_start_time, file_end_time = start_end_time 
	sample_duration = 1.0 / sr
	debug("sample_dur=%f  sample_rate=%d"%(sample_duration,sr))
	segments_times = SplitWavdataByEnergy(wav_data,initialsegmentfolder,file,Xsec, sample_duration,file_start_time, file_end_time)

	ind=1
	
	segments_file_write = open(segments_file_path,"wb")
	for start_end_pair in segments_times:
		start_time, end_time = start_end_pair
		# print start_time, end_time
		utt_id = os.path.basename(wavfile)
		if ind < 10:
			segment_id = utt_id.replace('.wav', '_0' + str(ind))
		else:
			segment_id = utt_id.replace('.wav', '_' + str(ind))
		utt_id = utt_id.split(".")[0]
		# print type(start_time), type(end_time)
		# 1 way to produce the segments file
		# segments_file_write.write("%s %s %.2f %.2f \n"% (segment_id,utt_id,start_time,end_time))
		# the way that long_audio_alignment wants the segments file
		seg_num=segment_id.split("_")[-1]
		segments_file_write.write("segment_%s key_1 %.2f %.2f \n"% (seg_num,start_time,end_time))
		ind +=1
	segments_file_write.close()	
# def GetLyrics(lyricsfolder,songname):
# 	# Get lyrics of a particular song
# 	# Input: lyricsfolder: where lyrics files of all the songs are kept
# 	#        songname: the name of the song for which lyrics is needed
# 	# Output: all_lines: all the lines of the lyrics file in one variable
# 	########################################################################
# 	for dir,sub,files in os.walk(lyricsfolder):
# 		for file in files:
# 			if songname in file:
# 				fin = open(lyricsfolder+os.sep+file,'r')
# 				flines = fin.readlines()
# 				fin.close()
# 				break
# 	all_lines = []
# 	for line in flines:
# 		line = line.lower()
# 		regex = re.compile(r'[,\.!?"\n]')
# 		stripped_line = regex.sub('', line)
# 		if stripped_line == '': continue
# 		check_for_bracket_words = stripped_line.split(' ')
# 		non_bracket_words = []

# 		for elem in check_for_bracket_words:
# 			if elem == "": continue #remove extra space
# 			if '(' in elem or ')' in elem: continue
# 			if elem[-1] == '\'': elem = elem.replace('\'','g') #Check if "'" is at the end of a word, then replace it with "g", eg. makin' => making
# 			if elem=="'cause": elem="cuz" #the ASR detects "'cause" as "cuz"
# 			elem=elem.replace('-',' ')
# 			non_bracket_words.append(elem)
# 		stripped_line = ' '.join(non_bracket_words)
# 		all_lines.append(stripped_line)
# 	all_lines =  ' '.join(all_lines)
# 	return all_lines.upper()

# 	#########################################################################

# def CheckForNumerals(ASRtranscript_array):
# 	# Checks if there are numbers in a given transcript array, and converts them to words
# 	# eg. 16 will be converted to sixteen
# 	# Input: ASRtranscript_array: transcript array of words
# 	# Output: data: Converted/Same text depending on whether numerals are present
# 	######################################################################################
# 	data = []
# 	for item in ASRtranscript_array:
# 		if bool(re.search(r'\d', item)):
# 			p = inflect.engine()
# 			word = p.number_to_words(item)
# 			data.append(word)
# 		else:
# 			data.append(item)
# 	return data

# 	#########################################################################

# def GetLevenshteinScore(ASRtranscript,lyrics):
# 	#Creates an error matrix between transcript and lyrics using Levenshtein distance
# 	# Input: ASRtranscript, lyrics
# 	# Output: score: i.e. the error score obtained from levenshtein distance
# 	#         final_lyric_transcript: the resultant transcript after ASR transcript is "corrected" by the published lyrics
# 	#         (Refer to the paper on top of this script for me details)
# 	################################################################################
# 	ASRtranscript_array = ASRtranscript.split(' ')
# 	ASRtranscript_array = CheckForNumerals(ASRtranscript_array)
# 	lyrics_array = lyrics.split(' ')
# 	error_matrix = np.zeros(shape=(len(lyrics_array)-len(ASRtranscript_array),5)) #num words in transcript by 5 types of lengths of windows on lyrics
# 	N = len(ASRtranscript_array)
# 	for lyric_index in range(len(lyrics_array)-len(ASRtranscript_array)):
# 		for window_ind in range(5):
# 			if lyric_index+N+window_ind>len(lyrics_array):
# 				error_matrix[lyric_index][window_ind] = np.nan
# 				continue
# 			lyric_window = lyrics_array[lyric_index:lyric_index+N+window_ind]
# 			num_errors,error_pattern = levenshtein(ASRtranscript_array,lyric_window)
# 			error_matrix[lyric_index][window_ind]=num_errors*1.0/len(lyric_window)

# 	min_lyric_index, min_lyric_window = np.unravel_index(np.nanargmin(error_matrix), error_matrix.shape)
# 	score = 1.0-np.nanmin(error_matrix)
# 	final_lyric_transcript = ' '.join(lyrics_array[min_lyric_index:min_lyric_index+N+min_lyric_window])
# 	return score, final_lyric_transcript

# 	#########################################################################

# def GetScoreAndTranscript_LevenshteinMethod(N,lyrics,dict):
# 	# Create error matrix for 5 windows of words, and calculate the minimum cost transcription from the lyrics.
# 	# This has to happen for every ASR output
# 	# The ASR transcript with minimum error with its corresponding lyrics window is chosen.
# 	# Input: N: total number of recognition outputs
# 	#        lyrics: string of the published lyrics
# 	#        dict: the dictionary of possible transcriptions obtained from the ASR
# 	# Output: percent_correct[max_score_index]: the error score of the best matching transcript
# 	#         lyric_transcripts[max_score_index]: the resultant published lyrics of the best matching transcript
# 	#         ASRtranscript_array: the actual ASR transcript corresponding to the best match
# 	######################################################################################
# 	percent_correct = [0]*N
# 	lyric_transcripts = []
# 	for i in range(N):
# 		transcript = dict["alternative"][i]["transcript"]
# 		percent_correct[i],lyric_transcript = GetLevenshteinScore(transcript.lower(),lyrics)
# 		lyric_transcripts.append(lyric_transcript)

# 	max_score_index = np.argmax(percent_correct)

# 	ASRtranscript = (dict["alternative"][max_score_index]["transcript"]).lower()
# 	ASRtranscript_array = ' '.join(CheckForNumerals(ASRtranscript.split(' ')))
# 	# print percent_correct[max_score_index], lyric_transcripts[max_score_index], ASRtranscript_array

# 	return percent_correct[max_score_index], lyric_transcripts[max_score_index], ASRtranscript_array

# 	#########################################################################

# def RecognitionAndMatching(initialsegmentfolder,targetfile,finalsegmentfolder,songname,lyricsfolder,fout1,fout2):
# 	# Iterate through all the segments of that particular rendition (song)
# 	# For every segment, do recognition using google API
# 	# After recognition, do a word string alignment with the lyrics
# 	# If the resultant word string had more than or equal to 10 words, then the wav segment is finalized and dumped into finalsegmentfolder
# 	# Output files:
# 	## 1. fulloutput.txt contains all valid wav files, lyric window transcript, ASR transcript, %correct
# 	## 2. resultant.txt: contains the valid wav filenames whose resultant transcript has >=10 words
# 	##################################################################
# 	###### Capture lyrics of the song into a string variable
# 	lyrics = GetLyrics(lyricsfolder,songname)

# 	###### Recognize the audio using Google API
# 	targetfile = targetfile.replace('.m4a','')
# 	newfile = ''
# 	for dir,sub,files in os.walk(initialsegmentfolder):
# 		for file in files:
# 			if targetfile in file:
# 				filename = file
# 				## add silence at the beginning and end for better recognition
# 				infiles = [silence_wav, initialsegmentfolder + os.sep + filename, silence_wav]
# 				data = []
# 				for infile in infiles:
# 					w = wave.open(infile, 'rb')
# 					data.append([w.getparams(), w.readframes(w.getnframes())])
# 					w.close()
# 				newfile = initialsegmentfolder + os.sep + filename
# 				output = wave.open(newfile, 'w')
# 				output.setparams(data[0][0])
# 				output.writeframes(data[0][1])
# 				output.writeframes(data[1][1])
# 				output.writeframes(data[2][1])
# 				output.close()

# 				AUDIO_FILE = newfile
# 				print '\n' + AUDIO_FILE

# 				# Use the audio file as the audio source
# 				r = sr.Recognizer()
# 				with sr.AudioFile(AUDIO_FILE) as source:
# 					audio = r.record(source)  # read the entire audio file

# 				# Recognize speech using Google Speech Recognition
# 				try:
# 					dict = r.recognize_google(audio, show_all=True)
# 					if not dict:
# 						print "Google API cannot recognise this clip"
# 						continue
# 					N = (len(dict["alternative"]))

# 					## Algorithm for getting the best transcription
# 					score, lyric_transcript, ASR_transcript = GetScoreAndTranscript_LevenshteinMethod(N,lyrics,dict)


# 					# 1. fulloutput.txt contains all valid wav files, lyric window transcript, ASR transcript, %correct
# 					fout1.write(filename + ',' + lyric_transcript + ','+ASR_transcript+','+str(score)+'\n')

# 					# 2. resultant.txt: contains the valid wav filenames whose resultant transcript has >=10 words
# 					# Transcription is that of the lyrics window
# 					if len(lyric_transcript.split(' ')) >= 10:
# 						fout2.write(filename + ' ' + lyric_transcript + '\n')
# 						copyfile(AUDIO_FILE, finalsegmentfolder + os.sep + filename)


# 				except BadStatusLine:
# 					print "could not fetch Google URL"
# 					continue
# 				except sr.UnknownValueError:
# 					print("Google Speech Recognition could not understand audio")
# 				except sr.RequestError as e:
# 					print("Could not request results from Google Speech Recognition service; {0}".format(e))
# 				##########################

###############################################################################################
if __name__ == "__main__":
	# This is the main function for this task
	# The input and output folders and files are already defined below
	# You will find the cleaned up subset of segments in the folder "wavsegments_final"
	# and the resultant lyrics transcriptions in "resultant.txt"
	# All the wavsegments are in wavsegments_initial, and fulloutput.txt contains complete information about all the wavsegments
	# This function runs for one .m4a file from DAMP dataset that is present in the folder "audio"
	# For the complete dataset clean up, keep all the m4a files in the "audio" folder
	#############################################################################################

	rawfolder = os.path.join(os.pardir,os.pardir,"mirex_data","DAMPB_6903","audio")# from Smule's Sing! Karaoke dataset (DAMP) here: https://ccrma.stanford.edu/damp/
	wavfolder = os.path.join(os.pardir,os.pardir,"mirex_data","DAMPB_6903","audio_16000Hz_wav")
	initialsegmentfolder = 'data/local/tmp_files/tmp_audio_segs' # wavsegments_10sec'
	finalsegmentfolder = 'wavsegments_final'
	lyricsfolder =  os.path.join(os.pardir,os.pardir,"mirex_data","DAMPB_6903",'lyrics')
	metadatafile = os.path.join(os.pardir,os.pardir,"mirex_data","DAMPB_6903",'DAMPBperfs.csv') # Kruspe's dataset, given here: http://www.music-ir.org/mirex/wiki/2017:Automatic_Lyrics-to-Audio_Alignment
	
	#creating the directories as needed
	subpr_call("mkdir -p " + wavfolder, shell=True)
	subpr_call("mkdir -p " + initialsegmentfolder, shell=True)
	subpr_call("mkdir -p " + finalsegmentfolder, shell=True)


	## output files
	fout1 = open('fulloutput.txt', 'w')
	fout2 = open('resultant.txt', 'w')


	textFromCSV = np.loadtxt(metadatafile, dtype=str, comments='#', delimiter=',')
	textFromCSV = np.delete(textFromCSV, 0, 0)
	
	# # checking how many singers we've compiled comment out the last for before using this.
	# utts_done = []
	# for singer_folder in tqdm(os.listdir(initialsegmentfolder),desc="Creating Done Utts"):
	# 	for utt in os.listdir(os.path.join(initialsegmentfolder,singer_folder)):
	# 		utts_done.append(utt)
	# print len(utts_done)		
	
	# LOG = open(os.path.join(LOGGING_DIR,"main.txt"),"w+")
	# # ## creating copy of textFromCSV
	# # textFromCSV_compiled_rows = []

	# # ## looping through textFromCSV and delete any 
	# # # rows with elements we have compiled already
	# # for i in tqdm(range(0,len(textFromCSV),1),desc="Creating_list_ToDelete"):
	# # 	## textFromCSV[i][1] : the utt-id of the i-th row of metadata
	# # 	if textFromCSV[i][1] in utts_done: 
	# # 		LOG.write("######14:24 ~~~ DELETING: {}{}\n".format(textFromCSV[i][1],textFromCSV[i][2]))
	# # 		# textFromCSV_partial=np.vstack((textFromCSV[:i,:],textFromCSV[i+1:,:]))
	# # 		textFromCSV_compiled_rows.append(i)
	# # 		utts_done.remove(textFromCSV[i][1])
	# # np.delete(textFromCSV, textFromCSV_compiled_rows, axis = 0)
	# LOG.close()

	segments_file_path = os.path.join(initialsegmentfolder,"segments")
	with open(segments_file_path, "w+"):
		pass
	
	for i in tqdm(range(0,len(textFromCSV),1)):
		i=4987 # for the particular file in the  audio folder currently, provided as an example
		curr_files = []
		# for f in os.listdir(rawfolder):
		# 	f_name,_ = os.path.splitext(f)
		# 	curr_files.append(f_name)
		# # print curr_files
		
		# if textFromCSV[i][1] in curr_files:
		print '\n#####################################'
		print 'CSV index = ',i, textFromCSV[i]
		print "{} iteration of {}".format(i, len(textFromCSV)-1)
		print '#####################################\n'
		utt = textFromCSV[i][1]
		file = utt +'.m4a'
		singer = textFromCSV[i][0]
		songname = textFromCSV[i][2]
		
		print '## convert M4A to wav, downsampling to 16kHz ##' ## keeping the sample frequency at 22.5kHz ##
		rawfile = os.path.join(rawfolder,singer,file)
		
		segment_dir = os.path.join(initialsegmentfolder,singer, utt)
		subpr_call("rm -r -v " + segment_dir, shell=True)
		subpr_call("mkdir -p " + segment_dir, shell=True)
		
		wav_file_name = file.replace('.m4a',songname+'.wav')
		wavfile = os.path.join(wavfolder, singer, wav_file_name)
		# M4AtoWAV16k(rawfile, wavfile)
		
		print '## segment the wavfile to audio segments ##'
		
		# Xsec: the minimum duration of the segments that we'll split the wavfiles 	
		Xsec = 10
		WavSplitter(wavfile,segment_dir,wav_file_name,Xsec, segments_file_path)
		
		# print '## segment recognition and string matching with ground truth lyrics to eliminate bad segments ##'
		# RecognitionAndMatching(initialsegmentfolder,file,finalsegmentfolder,songname,lyricsfolder,fout1,fout2)
		break #remove to run for all the files
	fout1.close()
	fout2.close()
	
	



