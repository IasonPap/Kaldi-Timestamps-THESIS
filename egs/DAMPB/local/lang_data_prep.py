#!/usr/bin/python3

import os
import argparse
import sys
from tqdm import tqdm
from functions import parse_lyrics

#######################################
# Gathering AllWords of the Dataset. Uniquefy them 
# And Also having a dictionary with format 'Song_ID': ['WORD1','WORD2', ...]
# where Song_ID is a string: 01,02,03, ..., 19,20
# returning the dictionary and writing a file called words.txt with the unique words
# needs tweeking for this dataset
def AllWords(lyrics_folder,DstDir):
	AllWords_list = []
	
	for song_file in tqdm(os.listdir(lyrics_folder), desc="Looking up songs", leave= True):
		current_lyrics_path = os.path.join(lyrics_folder,song_file)
		parsed_curr_lyrics = parse_lyrics(current_lyrics_path)
		clear_lyrics_list = parsed_curr_lyrics.split(" ")
		for word in clear_lyrics_list:
			AllWords_list.append(word)
	AllWords_list = list(dict.fromkeys(AllWords_list))
	AllWords_list = sorted(AllWords_list)
	with open(DstDir + os.sep + "my_words.txt", "w+") as words_file:
		for i, word in enumerate(AllWords_list):
			if word != "":
				if i < len(AllWords_list)-1:
					words_file.write(word + "\n")
				else:
					words_file.write(word)
	
	return AllWords_list
def Make_lexicon(DataDir, DstDir):
	pass
	# AllWords_list = AllWords(DataDir, DstDir)
	# WavDir = os.path.join(DataDir,"ready_good_utts")
	# # for spk in os.listdir(os.path.join(DataDir,"audio")):
	# #     WavDir = os.path.join(DataDir,"audio",spk,"sing")
	# utt_list, _, _ = Create_utt_singer_song_list(WavDir)
	
	# phones_per_utt = phones4utt(DataDir,utt_list)
   
   
	# for utt in utt_list:
	# 	curr_song = utt.split("-")[1]
	# 	curr_phones_list = phones_per_utt[utt]
	# 	curr_phones_list = replace(curr_phones_list, "sp", "sil")
	# 	curr_phones_string = ":".join(curr_phones_list)
	# 	phones4word = curr_phones_string.split(":sil:")
	# 	phones4word[0] = phones4word[0].split("sil:")[1]
	# 	max_item = len(phones4word)-1
	# 	phones4word[max_item] = phones4word[max_item].split(":sil")[0]
		
	# 	# check_if_elem_of_2lists_match(Words_per_song[curr_song],phones4word)

def make_lexicon_fast(DataDir,DstDir):
	pass
	# WavDir = os.path.join(DataDir,"ready_good_utts")
	# utt_list, _, _ = Create_utt_song_spkr_list(WavDir)
	
	# transcr_list = []
	# CWD = 	os.path.join(DataDir,"G2P")
	# for file in os.listdir(CWD):
	# 	file_name, _ = os.path.splitext(file)
	# 	file_abs_path = os.path.join(CWD,file)
	# 	if file_name in utt_list:
	# 		with open(file_abs_path,"r") as fread:
	# 			reader=fread.readlines()
	# 			for i in range(len(reader)):
	# 				transcr_list.append(reader[i])
	# transcr_list = sorted(list(dict.fromkeys(transcr_list)))


	# with open(os.path.join(DstDir,"lexicon.txt"),"w+") as fwrite:
	# 	fwrite.write("<UNK> OOV\n")
	# 	for trans in transcr_list:
	# 		fwrite.write(trans)
		
if __name__ == "__main__":
	parser = argparse.ArgumentParser(description="Preparing the necessary files for Kaldi.")
	parser.add_argument("DataDir", 
						help="The location of the data files that you want to prepare.", 
						type=str)
	parser.add_argument("DstDir",
						help="The location to write the new files. e.g. text,wav.scp,etc.",
						type=str)
	parser.add_argument('-l','--lexicon',
						help="Makes the 'lexicon.txt' file. " + \
							"This file's format is: WORD (transcription in phonemes) PHON1 PHON2 ...\n",
						action="store_true")
	parser.add_argument('-w', '--words',
						help="Makes the \"words.txt\" file. "+ \
							"which contains all the unique words in the lyrics.",
						action="store_true")
	
	args = parser.parse_args()
	########################
	# CONSTANTS

	
	DATA_PATH =	args.DataDir
	DST_PATH = args.DstDir
	
	try:
		LYRICS_PATH = os.path.join(DATA_PATH,"lyrics")
	except Exception as e:
		print("{}: Didn't found the lyrics folder."+
			"Make sure to enter as DataDir the main Data Directory(a.k.a DataDir).")
		sys.exit()

	###############
	if args.words:
		#Making the text file
		AllWords(lyrics_folder=LYRICS_PATH, DstDir=DST_PATH)
	if args.lexicon:
		#Making the wav.scp file
		Make_lexicon(DataDir=DATA_PATH, DstDir=DST_PATH)
