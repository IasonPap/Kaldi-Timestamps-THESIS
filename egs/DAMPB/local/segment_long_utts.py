#!/usr/bin/python2


import os, sys
from functions import read_lines, debug
import subprocess
from tqdm import tqdm
from main import WavSplitter

############################
# CONSTANTS
# first set the variables in longaudio-align/longaudio_vars.sh 
# for lang dir and data dir (although data dir doesn't need to change)

DATASET_TO_SEGMENT = "train0.8"

BASH_ALIGN_SCRIPT = "longaudio_alignment.sh"
SCRIPT_DIR = "longaudio-align"

DATA_FILES = ["text", "wav.scp", "utt2spk"]#, "spk2utt"]

###########################

DATA_DIR = os.path.join("data", DATASET_TO_SEGMENT)

utt2spk_lines = read_lines(os.path.join(DATA_DIR,"utt2spk"))
text_lines = read_lines(os.path.join(DATA_DIR,"text"))
wav_lines = read_lines(os.path.join(DATA_DIR,"wav.scp"))
spk2utt_lines = read_lines(os.path.join(DATA_DIR,"spk2utt"))



if len(utt2spk_lines)!=len(text_lines) and len(wav_lines)!=len(text_lines):
	print "The lengths of text, wav, utt2pk, spk2utt don't match."+\
		" \nSomething is wrong! Exiting."
	sys.exit()

temp_test_dir="data/local/tmp_files/temp_1utt"
#len(utt2spk_lines)
for i in range(len(utt2spk_lines)):# ,desc="Files to be Segmented", position=2, unit="files"):
	i=4780
	output_for_i = [text_lines[i], wav_lines[i], utt2spk_lines[i]]
	# removing utt2num_frames
	if os.path.exists(temp_test_dir + os.sep + "utt2num_frames"):
		subprocess.check_call(["rm","-v", temp_test_dir + os.sep + "utt2num_frames"])
	# splitting the wavfile by Energy in segments of duration Xsec
	data_dir="data/local/tmp_files/temp_1utt"
	log_dir="data/local/tmp_files/log"
	if os.path.exists(data_dir) and os.path.exists(log_dir):
		# subprocess.check_call(["mkdir","-p",data_dir])
		subprocess.check_call(["sh","backup_for_tmp.sh",data_dir,log_dir])
		subprocess.check_call(["mkdir","-p",data_dir])
	dst_dir="data/local/tmp_files/audio"
	if os.path.exists(dst_dir):
		subprocess.check_call(["rm","-r",dst_dir])
	subprocess.check_call(["mkdir","-p",dst_dir])
	WavSplitter(wavfile=wav_lines[i].split(" ")[1], 
				initialsegmentfolder=dst_dir, 
				file=os.path.basename(wav_lines[i].split(" ")[1]), 
				Xsec=10, 
				segments_file_path=os.path.join(temp_test_dir, "segments"))
	# generating text, wav.scp, spk2utt, utt2spk	
	# wav_write = open(temp_test_dir + os.sep + "wav.scp","w+")
	with open(temp_test_dir + os.sep + "utt2spk","w+"):
		pass
	for file,output in zip(DATA_FILES,output_for_i):
		if file == "text" or file == "wav.scp":
			info = " ".join(output.split(" ")[1:])
			debug(info)
			with open(temp_test_dir + os.sep + file,"w+") as fwrite:
				fwrite.write("key_1" + " "+info+ "\n")
		else:
			# debug(temp_test_dir + os.sep + file)
			
			for root,_, files in os.walk(dst_dir):
				files.sort()
				for segment in files:
					seg_id,_ = os.path.splitext(segment)
					utt = "_".join(seg_id.split("_")[:-1])
					if file == "utt2spk":
						singer_id = segment.split(" ")[0].split("_")[0]
						# debug("{} {}\n".format(seg_id, singer_id))
						seg_num=seg_id.split("_")[-1]
						with open(temp_test_dir + os.sep + "utt2spk","a") as utt2spk_write:
							utt2spk_write.write("segment_{} {}\n".format(seg_num, seg_id)) # singer_id
	# wav_write.close()
	OldDir = os.getcwd()
	# os.chdir("local/longaudio-align")
	# print(os.listdir())
	
	script_name = ["./longaudio_alignment.sh"]
	working_dir = ["data/local/tmp_files"]
	new_dir = [str(utt2spk_lines[i].split(" ")[0])]
	stage = ["15"]
	segments_bool = ["--create_dir", "true"]

	subprocess.call(script_name + working_dir + new_dir + stage + segments_bool)

	os.chdir(OldDir)
	break