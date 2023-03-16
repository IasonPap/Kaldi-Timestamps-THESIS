import os
import sys

def CreateUttID(text_file):
	"""
	takes as input the "text" file with the transcriptions and 
	returns the list of the utterances ids (<speaker_id>_<performance_id>_<song_title>_<segment_number>, 
	i.e. 212904266_47746177_beautiful_07)
	in the "text" file. 
	"""
	utt_id_list = []
	with open(text_file,"r") as reader:
		lines = reader.read().splitlines()
	for line in lines: # iterating through all the lines of the 'text' file
		# picking the first column from each line (containg the utterance if text file is correct)
		utt_id = line.split(" ")[0] 
		utt_id_list.append(utt_id)
	return utt_id_list

def MakingWavFile(DataDir, DstDir):
	"""
	Here we make the text file. Which has the format: file_id path/file

	For DAMPB_150songs Dataset:
		1) DataDir must be the folder where the wavfiles for the training are located.
		2) I have segmented the audio files in 30sec segments so: file_id == utt_id

	"""
	text_file = os.path.join(DstDir,"text")
	utt_id_list = CreateUttID(text_file)

	wav_files_in_DataDir = os.listdir(DataDir)
	# print(wav_files_in_DataDir)

	print(f"Creating the wav.scp file in directory: {DstDir}")
	with open(os.path.join(DstDir,"wav.scp"),"w+") as writer:
		for utt in utt_id_list:
			wav_file = f"{utt}.wav"

			wav_path = os.path.join(os.path.abspath(DataDir),wav_file)
			if wav_file in wav_files_in_DataDir:
				writer.write(f"{utt} {wav_path}\n")
			else:
				print(f"there is no wav file with the name '{utt}.wav' in {DataDir}.  Skipping...")

if __name__ == '__main__':

	if len(sys.argv) != 3:
		print("#############################################################")
		print("Please input exactly 2 Inputs. DATADIR and DSTDIR")
		print("DATADIR: path to the folder containing the wavfiles we want to use for training")
		print("DSTDIR: path to the folder containing the data files (text, utt2spk etc.) and soon wav.scp")
		print("#############################################################")
		sys.exit()

	# this is the folder that you have your wav files
	DATADIR = sys.argv[1]
	
	# DSTDIR points to the folder where you want to create the wav.scp file 
	# it's the same file containing the 'text' file with transcription of your data.
	DSTDIR = sys.argv[2]
	print(f"Running: {sys.argv[0]} \t WITH arguments: {sys.argv[1:]}")
	print(f"Creating the 'wav.scp' file in: {DSTDIR} \n with data from: {DATADIR}.")

	MakingWavFile(DATADIR, DSTDIR)