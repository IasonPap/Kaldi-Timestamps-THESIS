import os
import sys
from copy import deepcopy
from tqdm import tqdm
# from PySimpleGui import popup_get_folder, popup_get_file

#CONSTANTS
#############
SIL_PHONE = "<eps>"
SAMPLE_RATE = "16000Hz"
BOOST_SILENCE = "1.2"
suffix = f"_{SAMPLE_RATE}_{BOOST_SILENCE}"

##############
def read_lines(path_to_file):
	"""	
	Reads a txt file and returns a list 
	with all the lines as separate values.
	Throws an error if path_to_file doesn't exist.
	"""
	try:
		with open(path_to_file,"r") as fread:
			reader = fread.read()
			lines = reader.split("\n")
			if "" in lines: #removes empty lines if they exist
				lines.remove("") 
			return lines
	except IOError as IOE:
		sys.exit(f"{IOE}: the file with path: {path_to_file}\n doesn't exist.")
#############################################################
def Separate_to_files(all_files_file, sep_files_dir):
	"""
	Seperates ctm file based on utt with format: "<start-time> <end-time> <word>"
	needs the ctm file to be of format: "<utt-id> <start-time> <end-time> <word>"

	Inputs: 
	all_files_file: the master ctm file with all the detected word boundaries (for all utterances)
	sep_files_dir: the path to the directory where the separated ctm files will be saved.
	"""
	# if "Kaldi" in os.path.basename(sep_files_dir):
	# 	extension = ".final.txt"
	# else:
	extension = ".final.txt"
	
	lines = read_lines(all_files_file)
	old_utt = ""
	for line in tqdm(lines, desc="Separating ctm for every utt"): #
		line_list = line.split(" ",3)
		new_utt = line_list[0]
		out_file = os.path.join(sep_files_dir, new_utt + extension)
		start = float(line_list[1])
		end = float(line_list[2])
		if new_utt != old_utt:
			with open(out_file,"w+") as fwrite:
				out_str = f"{start:.2f} {end:.2f} {line_list[-1]}"
				fwrite.write(out_str + "\n")
		else:
			with open(out_file,"a") as fwrite:
				out_str =  f"{start:.2f} {end:.2f} {line_list[-1]}"
				fwrite.write(out_str + "\n")
		
		old_utt = deepcopy(new_utt)
#############################################################
def prep_ctm_file(path_to_ctm,dst_dir, kaldi_word_dir):
	"""
	Reads the output ctm file for one model from Kaldi, 
	turns to format "<Utt_ID> <start_time> <end_time> <word>"
	and then splits the master ctm file to separate according to the utterance with the format:
	"<start_time> <end_time> <word>".

	Inputs:
	path_to_ctm: the path to the ctm file for which 
				 we want to create the folder with the detected word boundaries
	dst_dir: the path to the destination directory where the processed master ctm file will be saved
	kaldi_word_dir: the path to the directory where the ctm master file 
					for the currect model will be split to different song word boundaries 
	"""
	ctm_lines = read_lines(path_to_ctm)
	_,base_file = os.path.split(path_to_ctm)
	base_name, ext = os.path.splitext(base_file)
	output_file = os.path.join(dst_dir,f"{base_name}_prepared{ext}")
	with open(output_file,"w+"):
		pass

	for line in tqdm(ctm_lines, desc="Preparing the ctm file for separation."):
		line_list = line.split(" ")
		line_list.pop(1)
		new_utt = line_list[0]
				
		start = float(line_list[1])
		end = start + float(line_list[2])
		word = line_list[3]
		# if word == SIL_PHONE:
		# 	word = "SIL"
		with open(output_file,"a") as fappend:
			fappend.write(f"{new_utt} {start:.3f} {end:.3f} {word}\n")
	Separate_to_files(output_file, kaldi_word_dir)
#############################################################
if __name__ == "__main__":
	

	# if len(sys.argv) == 3:
	# 	CTM_FILE_ALL = sys.argv[1]
	# 	KALDI_WORD_DIR = sys.argv[2]
	# else:

	## easy way to get files and folders with the popup browse window (needs installed the PySimpleGUI package) 
	
	# ctm_file_raw = popup_get_file('Please select the ctm master RAW file:')
	detect_words_dir = input("Input the directory where you want to save "+
							"the different detected word boundaries for all the models:\n")
	detect_words_dir = os.path.join("local-files", "KaldiWordCTM_ALL_MODELS")
	
	for model in ["tri4b","tri4b_sing", "tri3_sing_only"]: # creating the ctm files for all the models
		print(f"PREPARING {model}")
		if "sing" in model:
			suffix = "speech+sing"
		elif "sing_only" in model:
			suffix = "sing_only"
		else:
			suffix = "speech"
	
	kaldi_word_dir = os.path.join(detect_words_dir,f'KaldiWordCTM_{suffix}')
	ctm_file_raw = os.path.join("local-files","KaldiWordCTM_all48_utts",f"ctm_all48utts_MDL_{model}_RAW.txt")

	if not os.path.isdir(kaldi_word_dir):
		os.makedirs(os.path.abspath(kaldi_word_dir))
	prep_ctm_file(ctm_file_raw, kaldi_word_dir)
