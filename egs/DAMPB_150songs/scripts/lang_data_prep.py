import os
import argparse
import sys
from functions import AllWords,read_lines
	
def function1(DataDir,DstDir, UttType):  #FillingG2P
	"""
	This creates the lexicon for the nus-smc-corpus_48. 
	Thus DataDir must be the directory of the corpus. 
	NOT the audio or the lyrics directories inside it.

	"""
	OldDir = os.getcwd()

	os.chdir(DataDir)

	Words_per_song = AllWords(DataDir, f"{OldDir}/data/local/lang")


	phones_per_utt = {}
	"""
	Gathering all phones of the Dataset. And putting them in a dictionary
	 with format 'utt_id': ['phone1','phone2', ...]
	where utt_id is a string with format: '<spkr_id>-<song_id>' (e.g.: 'ADIZ-01')
	
	Also we create a list with all the Utt Names/IDs for quick reference
	"""
	UttNames = []#CreateUttID(DataDir,UttType) 
	for spkr in os.listdir("audio"):
		CWD = f"audio/{spkr}/sing"
		for utt_file in os.listdir(CWD):
			utt_name, utt_ext = os.path.splitext(utt_file)
			# SongID = utt_name.split("-")
			if utt_ext == ".txt":
				phones = []
				with open(f"{CWD}/{utt_file}","r") as fread:
					reader = fread.read()
					#reading the lines of the file
					lines = reader.split("\n")
					for i, line in enumerate(lines):
						if line != "":
							# if utt_name == "ADIZ-09":
							# 	temp = line.split(" ")[2]
							# 	print(temp, i)
							phones.append(line.split(" ")[2])
				phones_per_utt[utt_name] = phones
				UttNames.append(utt_name)
	
	"""Printing statements to help with debugging"""
	# print(phones_per_utt["ADIZ-01"])
	
	# print(Words_per_song["14"])
	# print(phones_per_utt["ZHIY-14"])

	"""
	Creating a list for each utt where we put the splitted phonemes, 
	in hopefully words. 
	"""
	# sil_phones = ["sil","sp"] # find with (sil)?(sp)?
	my_count1 = 0
	my_count2 = 0
	Good_Utts = []
	with open("Good_Transcription.txt","w+"):
		pass
	
	words2phones_AllUtts = []
	for utt in UttNames:
		
		words2phones = {}
		song = utt.split("-")[1]
		
		phones_per_utt[utt] = [x for x in phones_per_utt[utt] if x != "sp"]
		phoneme_seq = ":".join(phones_per_utt[utt]) #phonemes is a list with the phonemes of the current utterance
		# phoneme_seq = phoneme_seq.replace("sp","sil") #replace(old,new)
		phone_per_word = phoneme_seq.split(":sil:")

		phone_per_word[0] = phone_per_word[0].split("sil:")[1]
		max_item = len(phone_per_word)-1
		phone_per_word[max_item] = phone_per_word[max_item].split(":sil")[0]
		
		# Unique_phone_per_word = list(dict.fromkeys(phone_per_word))
		# Unique_Words_per_song = list(dict.fromkeys(Words_per_song[song]))
		# if utt == "ZHIY-14":
		# 	print(phone_per_word)
		"""Assuring that the list with the words of the utterance 
					and the list with the phones splitted to words 
		are equal.
		"""
		diff = len(Words_per_song[song])-len(phone_per_word)	
		if diff != 0:
			"""Counting the number of errors/mismatches"""
			my_count1 += 1
			# print(len(Words_per_song[song]),len(phone_per_word), len(Words_per_song[song])-len(phone_per_word))
			my_count2 += abs(diff)
		else:
			with open(f"G2P/{utt}.txt","w+"):
				pass
			Good_Utts.append(utt)
			with open("Good_Transcription.txt","a") as fappend1:
				fappend1.write(utt +"\n")

			for i, transcription in enumerate(phone_per_word):
				cleared_phones = transcription.split(":")
				cleared_phones = " ".join(cleared_phones)
				cleared_phones = cleared_phones.upper()

				with open(f"G2P/{utt}.txt","a") as fappend2:
					word = Words_per_song[song]
					if word[i] != "": 
						fappend2.write(f"{word[i]} {cleared_phones}\n")
					# if utt == "ZHIY-06" and word[i] == " M": #and word[i+1] == "GOING":
						
					# 	flag = True
					# 	fappend2.write(f"{word[i]} {cleared_phones} ")
					# if flag:
					# 	if word[i-1] == "YOU'RE" and word[i] == "GOING":
					# 		fappend2.write(f"{cleared_phones}\n")
					# 	else:
					# 		fappend2.write(f"{word[i-1]} {cleared_phones}\n")
					# else:		
			words2phones_AllUtts.append(words2phones)

	
	print("# of Faulty Files: "+str(my_count1))
	print("# of Faults: "+ str(my_count2))
			# print(Words_per_song[song])
			# print(phone_per_word)
			# print("\n")
		# if diff < 0 :
		# 	while diff < 0:
		# 		print(phone_per_word[len(phone_per_word) + diff-1] + "\t")
		# 		diff+=1
		# elif diff > 0:
		# 	while diff > 0:
		# 		print(Words_per_song[song][len(Words_per_song[song])-diff-1] + "\t")
		# 		diff-=1
		# try:
		# 	for i in range(len(Words_per_song[song])):
		# 		cleared_phones = phone_per_word[i].split(":")
		# 		word = Words_per_song[song][i]
		# 		words2phones[word] = " ".join(cleared_phones)
		
				


		# if utt == "ZHIY-14":
		# 	print(Words_per_song[song],phone_per_word)	
	os.chdir(OldDir)
			
def function2(DataDir,DstDir): #MakingLexicon

	# print(os.getcwd())
	OldDir = os.getcwd()
	NewDir = f"{DataDir}/G2P"
	
	lexicon_dir = f"{OldDir}/{DstDir}"
	os.chdir(NewDir)
	Utt_names = []
	# print("lexicon_dir = "+lexicon_dir)
	with open(f"{lexicon_dir}/lexicon.txt","w+"):
		pass
	lexicon_lines = []
	for file in os.listdir():
		file_name,_ = os.path.splitext(file)
		Utt_names.append(file_name)

		rows = read_lines(file) #reading line by line the current 

		for row in rows:
			if row[0] == " ":
				print(row.split(" "),file)
			# print(row.split(" ",1))
			word, phones = row.split(" ",1)
			# print(word,phones)
			lexicon_lines.append(f"{word} {phones}")
			
	# import re
	# lexicon_lines = re.replace
	lexicon_lines = sorted(lexicon_lines)
	
	lexicon_lines_unique = list(dict.fromkeys(lexicon_lines))
	# for i in lexicon_lines_unique:
	# 	print(i.split(" ",1))
	
	
	with open(f"{lexicon_dir}/lexicon.txt","a") as fappend:
		write_seq = "\n".join(lexicon_lines_unique)
		fappend.writelines(write_seq)
		fappend.write("\n")




def function3(DataDir,DstDir):
	pass
	
def main():
	parser = argparse.ArgumentParser(description="Preparing the necessary files for Kaldi.")
	parser.add_argument("DataDir", 
						help="The location to the data files that you want to prepare.", 
						type=str)
	parser.add_argument("DstDir",
						help="The location to write the new files. e.g. text,wav.scp,etc.",
						type=str)
	# parser.add_argument('-l','--lex',
	# 					help="Makes the lexicon.txt. " + \
	# 						"Contains the transcription of all words into phonemes." + \
	# 						"This file's format is: WORD W ER D   \\n" + \
	# 											    "LEXICON L EH K S IH K AH N" ,
	# 					action="store_true")
	parser.add_argument("-f1", help="calls function 1", action="store_true")
	parser.add_argument("-f2", help="calls function 2", action="store_true")
	parser.add_argument("-f3", help="calls function 3", action="store_true")
	parser.add_argument("-ut","--UttType", 
						help="2 option for audio, sang and spoken."+\
							"Available option sing,read. Default='sing'",
						nargs='?', default='sing')
	# parser.add_argument('-w', '--wav',
	# 					help="Makes the 'wav.scp' file. "+ \
	# 						"This file's format is: file_id path/file",
	# 					action="store_true")
	# parser.add_argument('-u','--utt2spk',
	# 					help="Makes the the 'utt2spk' file. "+ \
	# 						"This file's format is: utt_id speaker_id",
	# 					action="store_true")
	args = parser.parse_args()

	# UttType = input("Enter wether you want the sung " +\
	# 				"or spoken audio data? [sing/read]")
	if args.f1:
		function1(args.DataDir,args.DstDir, args.UttType)
	if args.f2:
    	#Making the text file
		function2(args.DataDir,args.DstDir)
	if args.f3:
		function3(args.DataDir,args.DstDir)
	# if args.wav:
	# 	#Making the wav.scp file
	# 	MakingWavFile(args.DataDir, UttType)
	# if args.utt2spk:
	# 	path = args.DataDir + "/audio"
	# 	MakingUtt2spkFile(path, UttType)

if __name__ == "__main__":
	sys.exit(main())