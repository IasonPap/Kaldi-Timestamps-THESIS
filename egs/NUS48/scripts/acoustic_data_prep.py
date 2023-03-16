import os
import argparse
import sys



#TODO: 1) make the wav.scp and utt2spk functions that make the corresponding files.
#	   2) documentate what type of folder structure this script works with.

def CreateUttID(UttType):
	# print(os.getcwd())
	root, CurrentCorpus = os.path.split(os.getcwd())
	if CurrentCorpus == "nus-smc-corpus_48":
		if (UttType in ["sing", "read"]): 
			Utt_ID_list = []
			UttPath = []
			for Spk in os.listdir("audio"): #iterating through the Speaker in DataDir
				# UttType = "sing"
				CWD = f"audio/{Spk}/{UttType}" #CWD == Current Working Directory
				# print(Spk, CWD)
				for file in os.listdir(CWD):
					# print(filename)
					FileName, FileExt = os.path.splitext(file)
					# print(FileExt)
					if FileExt == ".wav":
						Utt_ID_list.append(FileName)
						UttPath.append(os.path.abspath(os.curdir) + f"/{CWD}/{file}")
			
			return sorted(Utt_ID_list), UttPath
		else:
			while (UttType  not in ["sing", "read"]):
				print("You must specify the kind of audio to be prepared.")
				UttType = input("Enter wether you want the sung " + \
								"or spoken audio data? [sing/read]")
	else: 
		print("! ! ! Wrong Directory ! ! ! ")
		print(f"Current Directory: {root}/{CurrentCorpus} \n \n")
		sys.exit()

def MakingTextFile(DataDir, DstDir): 
	"""
	Here we make the text file. Which has the format:  utt-id WORD1 WORD2 WORD3 ...

	

	"""
	g2p_lyrics_dir = os.path.join(DataDir,"G2P")

	writer = open(os.path.join(DstDir,"text"),"w+")
	for file in os.listdir(g2p_lyrics_dir):
		file_path = os.path.join(g2p_lyrics_dir,file)
		filename, ext = os.path.splitext(file)
		with open(file_path,"r") as reader:
			lines = reader.read().splitlines(keepends=False)
			words = [line.split(' ')[0] for line in lines]
			transcr = ' '.join(words)
		writer.write(f"{filename} {transcr}")
		writer.close()
		

def MakingWavFile(DataDir, DstDir, UttType):
	"""
	Here we make the text file. Which has the format: file_id path/file

	For NUS48 Dataset:
		1) DataDir must go inside /media/datadisk/greg/Jason/mirex_data/NUS48/ready_good_utts

	"""
	audio_wav_dir = os.path.join(DataDir,"audio")
	with open(os.path.join(DstDir,"wav.scp"),"w+") as writer:	
		for file in os.listdir(audio_wav_dir):
			file_path = os.path.join(audio_wav_dir,file)
			filename,ext=os.path.splitext(file)
			writer.write(f"{filename} {file_path}\n")

def MakingUtt2spkFile(DataDir, DstDir, UttType):
	"""
	Here we make the utt2spk file. Which has the format: utt_id spkr

	For NUS48 Dataset:
		1) DataDir must go inside nus-sms-corpus_48/audio folder.

	"""
	OldDir = os.getcwd()
	os.chdir(DataDir)
	
	print("3rd instance of CreateUttID")
	os.chdir(os.pardir) #FIXME: very very very πρόχειτη λύση
	Utt_ID_list, UttPath = CreateUttID(UttType)
	
	os.chdir("audio")	#FIXME: very very very πρόχειτη λύση
	Spk_ID = os.listdir(os.curdir)	

	os.chdir(OldDir)

	with open(f"{DstDir}/utt2spk","w+") as fwrite:
		for spk in Spk_ID:
			for utt in Utt_ID_list:
				if utt.split("-")[0] == spk:
					fwrite.write(f"{utt} {spk}\n")
	
	root, last_dir = os.path.split(os.getcwd())
	if last_dir == "local":	
		os.chdir(os.pardir)



def main():
	parser = argparse.ArgumentParser(description="Preparing the necessary files for Kaldi.")
	parser.add_argument("DataDir", 
						help="The location to the data files that you want to prepare.", 
						type=str)
	parser.add_argument("DstDir",
						help="The location to sent the processed files.",
						type=str)
	parser.add_argument('-t','--text',
						help="Makes the 'text' file. " + \
							"This file's format is: utt_id WORD1 WORD2 WORD3 ...",
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

	UttType = input("Enter wether you want the sung " +\
					"or spoken audio data? [sing/read]")
	if args.text:
		#Making the text file
		MakingTextFile(args.DataDir,args.DstDir, UttType)
	if args.wav:
		#Making the wav.scp file
		MakingWavFile(args.DataDir, args.DstDir,UttType)
	if args.utt2spk:
		path = args.DataDir + "/audio"
		MakingUtt2spkFile(path,args.DstDir, UttType)

if __name__ == "__main__":
	sys.exit(main())