#!/usr/bin/python3


import os, sys, csv
import argparse, random
from tqdm import tqdm
from functions import ClearSentence, read_lines, parse_lyrics,debug


#TODO: 2) documentate what type of folder structure this script works with.

##############################
# returns a list with all the utterances 
# in the MetaDataFile of the dataset given
# Input: MetaDataFile: the path to the csv medatafile
# Output: utt_list: a list with all the utternaces of the csv file
def create_utt_lists(MetaDataFile):
	utt_list = []
	Header = ["singer_account_id","performance_id","song_title","singer_gender","singer_birth_year","","Language"]
	print("~~~~~~~~\nCreating utterance lists")
	with open(MetaDataFile, "r") as csv_read:
		reader = csv.DictReader(csv_read)
		for row in tqdm(reader, desc= "Reading Metadata file", position=2, unit="perfs"):
			utt_list.append(row["performance_id"])
	print("~~~~~~~")
	return utt_list
#######################################
# returns a dictionary with keys: the utterance-ids
# and values: a tuple (singer_id, song) 
# Input: MetaDataFile: the path to the csv medatafile
#		 utt_list: a list with all the utternaces_id of the csv file, e.g 92486317_39827905 
# Output: singer_song_4utt: a dictionary with (singer,song) tuple 
# 							for every utterance in utt_list
def get_singer_song_4utt_dict(MetaDataFile, utt_list):
	singer_song_4utt = {}
	# Header = ["singer_account_id","performance_id","song_title","singer_gender","singer_birth_year","","Language"]
	print("~~~~~~~~\nGetting singer and song for utt in list.~~~~~~~~~~")
	for utt in tqdm(utt_list, desc= ""):
		with open(MetaDataFile, "r") as csv_read:
			reader = csv.DictReader(csv_read)
			for row in reader:
				if row["performance_id"] == utt:
					singer_song_4utt[utt] = (row["singer_account_id"], row["song_title"])
					break
	print("~~~~~~~")
	return singer_song_4utt
#######################################
# return a string with parsed lyrics for the song that corresponds to utt_id. 
# to find the match it needs the song title that corresponds to utt_id
# Input: MetaDataFile: the path to the csv medatafile
# 		song_title: the name of the song that we want the lyrics
# Output: a string of the parsed lyrics of the song
def lyrics4utt(MetaDataFile, song_title="test"): 
	# print(os.getcwd())
	DAMP_folder,_ = os.path.split(MetaDataFile)
	lyrics_folder = os.path.join(DAMP_folder,"lyrics")
	unparsed_lyrics_path = os.path.join(lyrics_folder, song_title + ".txt")
	try:
		out = parse_lyrics(unparsed_lyrics_path)
		return out
	except Exception as e:
		debug("{}: didn't find the lyrics file.".format(e) + \
				" Put the lyrics in the \"lyrics\" folder in the data directory" +\
					" and try again.")
		sys.exit()

	
#######################################
# Splits the dataset into a random split of train,test
# Input: MetaDataFile:  the path to the csv medatafile
# Output: train_data: a list of the utterances in the random TRAIN split
# 		   test_data: a list of the utterances in the random TEST split
# 		    utt_list: a list with all the utternaces of the csv medatafile file
def get_train_test_utts(MetaDataFile):
	utt_list = create_utt_lists(MetaDataFile)
	print("utt_list_length: {}".format(len(utt_list)))

	global test_data_split	
	number_test_utts = int(test_data_split * len(utt_list))
	print("number_test_utts: {}\n".format(number_test_utts))
	# number_train_utts = len(utt_list) - test_data_split

	train_data, test_data = [], []
	try:
		test_indices = random.sample(range(0, len(utt_list)), number_test_utts)
	except ValueError:
		print('Sample size exceeded population size.')
	
	for i, utt in enumerate(utt_list):
		if i in test_indices:
			test_data.append(utt)
		else:
			train_data.append(utt)
	# train_data = [utt for utt in utt_list if utt not in test_data]

	return train_data, test_data, utt_list	
#######################################		
# Here we make the text file. Which has the format:  utt-id WORD1 WORD2 WORD3 ...
# Input: DstDir: the directory where the text file will be dumbed
# 		MetaDataFile: the path to the MetaDataFile with all the utt-ids, spk-ids, song names, etc.
# 		utt2singer_song_dict: utt2singer_song_dict: dictionary with keys: utt_ids 
# 										and values: a tuple of (<singer_id>, <song_id>) 
def MakingTextFile(DstDir, MetaDataFile, utt2singer_song_dict): 
	print("############\nCreating text file at {}\n###########".format(DstDir))
	utt_list = utt2singer_song_dict.keys()
	print("\n\n")
	with open(DstDir + os.sep + "text","w+") as text_file:
		for utt in tqdm(utt_list, desc= "TEXT: Iterating through Utts", position=2, unit="perfs"):
			song = utt2singer_song_dict[utt][1]
			lyrics = lyrics4utt(MetaDataFile, song_title=song)
			text_file.write(utt + song + " " + lyrics + "\n")
#############################################
# Here we make the wav.scp file. Which has the format: file_id path/file
# For DAMPB Dataset:
#	1) DataDir must go inside DAMPB_6903 folder.
# 	2) utt_id == recording-id from kaldi.org
# Input: DataDir: the directory where the audio directory and the MetaDataFile are located 
# 		 DstDir: the directory where the wav.scp file will be dumbed
# 		utt2singer_song_dict: dictionary with keys: utt_ids 
# 										and values: a tuple of (<singer_id>, <song_id>) 
def MakingWavFile(DataDir, DstDir, utt2singer_song_dict):
	print("############\nCreating wav.scp file at {}\n###########".format(DstDir))
	utt_list = utt2singer_song_dict.keys()
	
	with open(DstDir + os.sep + "wav.scp","w+") as wav_file:
		for utt in tqdm(utt_list, desc= "WAV.SCP: Iterating through Utts", position=2, unit="perfs"):
			# tqdm(zip(utt_list, singer_list), desc= "WAV: Iterating through Utts&Singers", position=2, leave=True)
			singer = utt2singer_song_dict[utt][0]
			song = utt2singer_song_dict[utt][1]
			utt_path = os.path.join(DataDir,singer,utt + song +".wav")
			wav_file.write(utt + song + " " + utt_path + "\n")
######################################
# Here we make the utt2spk file. Which has the format: <utt_id>_<song_name> <spkr>
# Input: DstDir: the directory where the utt2spk file will be dumbed
# 		 utt2singer_song_dict: dictionary with keys: utt_ids 
# 									  and as values: a tuple of (<singer_id>, <song_id>) 
def MakingUtt2spkFile(DstDir, utt2singer_song_dict):
	print("############\nCreating utt2spk file at {}\n###########".format(DstDir))
	utt_list = utt2singer_song_dict.keys()
	
	with open(DstDir + os.sep + "utt2spk","w+") as utt_file:
		for utt in tqdm(utt_list, desc= "UTT2SPK: Iterating through Utts", position=2, unit="perfs"):
			singer = utt2singer_song_dict[utt][0]
			song = utt2singer_song_dict[utt][1]
			utt_file.write(utt + song + " " + singer + "\n")

def main():
	parser = argparse.ArgumentParser(description="Preparing the necessary files for Kaldi.")
	parser.add_argument("DataDir", 
						help="The location of the data files that you want to prepare.", 
						type=str)
	parser.add_argument("DstDir",
						help="The location to write the new files. e.g. text,wav.scp,etc.",
						type=str)
	parser.add_argument('-t','--text',
						help="Makes the 'text' file. " + \
							"This file's format is: utt_id WORD1 WORD2 WORD3 ...\n"+
							"Also the \"words.txt\" file is created,\n"+
							"which contains all the unique words in the lyrics.",
						action="store_true")
	parser.add_argument('-w', '--wav',
						help="Makes the 'wav.scp' file. "+ \
							"This file's format is: file_id path/file",
						action="store_true")
	parser.add_argument('-u','--utt2spk',
						help="Makes the the 'utt2spk' file. "+ \
							"This file's format is: utt_id speaker_id",
						action="store_true")
	
	args = parser.parse_args()
	########################
	# CONSTANTS
	try:
		METADATA_FILE = os.path.join(args.DataDir,"DAMPBperfs.csv")
	except Exception as e:
		print("{}: Didn't found the metadata file DAMPBperfs.csv.".format(e)+
			"Make sure to put inside the main Data Directory(a.k.a DataDir).")
		sys.exit()
	
	DATA_PATH =	args.DataDir
	WAV_DIR = os.path.join(DATA_PATH,"audio_16000Hz_wav")
	
	global test_data_split
	test_data_split = 0.2  # train= 0.8
	TRAIN_DIR = "train" + str(1-test_data_split)
	TEST_DIR = "test" + str(test_data_split)

	###############
	# # to produce wav.scp file for random train/test data
	# train_data, test_data, all_utts = get_train_test_utts(METADATA_FILE)
	# print(len(train_data), len(test_data))
	# if len(train_data)+len(test_data) == len(all_utts):
	# 	print("true\n")
	# else:
	# 	print("false\n")
	# train_set = train_data
	# test_set = test_data
	############################
	# TO produce the wav.scp file using the existing selection of train/test data
	# creating the utt lists for the already existing dataset 
	train_set=[]
	test_set=[]
	for row in read_lines(os.path.join("data",TRAIN_DIR,"utt2spk")):
		utt_song = row.split(" ")[0]
		utt_clean = "_".join(utt_song.split("_")[:2])
		train_set.append(utt_clean)
	for row in read_lines(os.path.join("data",TEST_DIR,"utt2spk")):
		utt_song = row.split(" ")[0]
		utt_clean = "_".join(utt_song.split("_")[:2])
		test_set.append(utt_clean)
	utt2singer_song_train = get_singer_song_4utt_dict(METADATA_FILE, train_set)
	utt2singer_song_test = get_singer_song_4utt_dict(METADATA_FILE, test_set)
	
	if args.text:
		#Making the text file for training 
		DST_PATH = os.path.join(args.DstDir, TRAIN_DIR)
		if not os.path.exists(DST_PATH):
			os.mkdir(DST_PATH)
		
		MakingTextFile(DST_PATH, METADATA_FILE,utt2singer_song_train)
		#Making the text file for testing 
		DST_PATH = os.path.join(args.DstDir, TEST_DIR)
		if not os.path.exists(DST_PATH):
			os.mkdir(DST_PATH)
		
		MakingTextFile(DST_PATH, METADATA_FILE,utt2singer_song_test)
	if args.wav:
		#Making the wav.scp file for training 
		DST_PATH = os.path.join(args.DstDir, TRAIN_DIR)
		
		MakingWavFile(WAV_DIR, DST_PATH, utt2singer_song_train)
		#Making the wav.scp file for testing
		DST_PATH = os.path.join(args.DstDir, TEST_DIR)
		
		MakingWavFile(WAV_DIR, DST_PATH, utt2singer_song_test)
	if args.utt2spk:
		#Making the utt2spk file for training
		DST_PATH = os.path.join(args.DstDir, TRAIN_DIR)
		MakingUtt2spkFile(DST_PATH, utt2singer_song_train)
		#Making the utt2spk file for testing
		DST_PATH = os.path.join(args.DstDir, TEST_DIR)
		MakingUtt2spkFile(DST_PATH, utt2singer_song_test)


if __name__ == "__main__":
	sys.exit(main())