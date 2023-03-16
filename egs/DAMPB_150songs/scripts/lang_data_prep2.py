import os
import argparse
import sys
from functions import *
def Make_lexicon(DataDir, DstDir):

	Words_per_song = AllWords(DataDir, DstDir)
	WavDir = os.path.join(DataDir,"ready_good_utts")
	# for spk in os.listdir(os.path.join(DataDir,"audio")):
	#     WavDir = os.path.join(DataDir,"audio",spk,"sing")
	utt_list, _, _ = Create_utt_song_spkr_list(WavDir)
	
	phones_per_utt = phones4utt(DataDir,utt_list)
   
   
	for utt in utt_list:
		curr_song = utt.split("-")[1]
		curr_phones_list = phones_per_utt[utt]
		curr_phones_list = replace(curr_phones_list, "sp", "sil")
		curr_phones_string = ":".join(curr_phones_list)
		phones4word = curr_phones_string.split(":sil:")
		phones4word[0] = phones4word[0].split("sil:")[1]
		max_item = len(phones4word)-1
		phones4word[max_item] = phones4word[max_item].split(":sil")[0]
		
		# check_if_elem_of_2lists_match(Words_per_song[curr_song],phones4word)

def make_lexicon_fast(DataDir,DstDir):
	WavDir = os.path.join(DataDir,"ready_good_utts")
	utt_list, _, _ = Create_utt_song_spkr_list(WavDir)
	
	transcr_list = []
	CWD = 	os.path.join(DataDir,"G2P")
	for file in os.listdir(CWD):
		file_name, _ = os.path.splitext(file)
		file_abs_path = os.path.join(CWD,file)
		if file_name in utt_list:
			with open(file_abs_path,"r") as fread:
				reader=fread.readlines()
				for i in range(len(reader)):
					transcr_list.append(reader[i])
	transcr_list = sorted(list(dict.fromkeys(transcr_list)))


	with open(os.path.join(DstDir,"lexicon.txt"),"w+") as fwrite:
		fwrite.write("<UNK> OOV\n")
		for trans in transcr_list:
			fwrite.write(trans)
		




if __name__ == "__main__":
	
	DataDir = "/home/jason/HDD_Storage/Dev/LyricsToAudio/nus-smc-corpus_48"
	DstDir = "data/local/lang"
	make_lexicon_fast(DataDir, DstDir)
	AllWords(DataDir, DstDir)
