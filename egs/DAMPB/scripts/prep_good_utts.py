import os
import sys
import argparse
if sys.platform == "linux" or sys.platform == "linux2":
	# linux
	sys.path.append(r"/mnt/HDD_Storage/Dev/LyricsToAudio/Data")
elif sys.platform == "win32":
	# Windows...
	sys.path.append(r"B:\Dev\LyricsToAudio\Data") 
from ClearLyrics import ClearSentence

from functions import *

def Make_text(DataDir,WavDir,DstDir):
	#
	# DstDir = ".../NUS48/data/alignme"
	##########
	
	utt_list,song_list, _ = Create_utt_song_spkr_list(WavDir)
	
	# print(utt_list,song_list)
	song2lyrics_dict = {}
	unique_song_list = list(dict.fromkeys(song_list))
	for song in unique_song_list:
		with open(os.path.join(DataDir,"lyrics",song+".txt"),"r") as fread:
			reader = fread.read()
			cleared_lyrics = ClearSentence(reader)
			song2lyrics_dict[song] = cleared_lyrics
	# print(song2lyrics_dict["08"])
	with open(os.path.join(DstDir,"text"),"w+") as fwrite:    
		for utt, song in zip(utt_list,song_list):    
			print(utt, song)
			fwrite.write(f"{utt} {song2lyrics_dict[song]}\n")

def Make_wav(DataDir,WavDir,DstDir):
	
	utt_list, path_list = Create_utt2paths_lists(WavDir)
	with open(os.path.join(DstDir,"wav.scp"), "w+") as fwrite:
		for utt, path in zip(utt_list,path_list):
			fwrite.write(f"{utt} {path}\n")

def Make_utt2spk(DataDir,WavDir,DstDir):
	
	utt_list, _, spkr_list= Create_utt_song_spkr_list(WavDir)
	with open(os.path.join(DstDir,"utt2spk"), "w+") as fwrite:
		for utt, spkr in zip(utt_list,spkr_list):
			fwrite.write(f"{utt} {spkr}\n")

def parse_args():
	parser = argparse.ArgumentParser(description="Preparing the necessary files for Kaldi.")
	parser.add_argument("DataDir", 
						help="The location to the data files that you want to prepare.", 
						type=str)
	parser.add_argument("DstDir",
						help="The location to write the new files. e.g. text,wav.scp,etc.",
						type=str)

	args = parser.parse_args()
	WavDir = os.path.join(args.DataDir,"good_utts","audio_mono")
	return args.DataDir, WavDir, args.DstDir

if __name__ == "__main__":
	
	DataDir,WavDir, DstDir = parse_args()
	
	print("\n~~~~~~~~~ Creating the text file ~~~~~~~~~~~~~~\n")
	Make_text(DataDir,WavDir, DstDir)

	print("\n~~~~~~~~~ Creating the wav.scp file ~~~~~~~~~~~~~~\n")
	Make_wav(DataDir,WavDir, DstDir)

	print("\n~~~~~~~~~ Creating the utt2spk file ~~~~~~~~~~~~~~\n")
	Make_utt2spk(DataDir,WavDir, DstDir)

	print("##########\tD O N E\t############\n")