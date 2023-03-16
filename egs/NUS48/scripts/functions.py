import os, re
import sys
from copy import deepcopy
from tqdm import tqdm

def uniquefy(my_list):
	# Takes a list and returns only the unique elements of that list
	return list(dict.fromkeys(my_list))

def find_string(my_list, target):
	# 
	# takes a "target" string and searches "my_list" to find it.
	# if target is not in the list return None
	# else returns the target and the position on the list that the target was found
	#################
	# first we sort the list
	my_list = sorted(my_list)
	# then we implement binary search to find the target string
	start = 0
	end = len(my_list) - 1

	while start <= end:
		middle = (start + end)// 2
		midpoint = my_list[middle]
		if midpoint > target:
			end = middle - 1
		elif midpoint < target:
			start = middle + 1
		else:
			return middle

def replace_elems_in_list(list , old_str, new_str):
	return [new_str if x == old_str else x for x in list]

def read_lines_and_strip_ends(txt_file):
	with open(txt_file) as fread:
		lines = fread.readlines()
	# stripping the "\n" line endings from each line in the text_file
	lines = [line.rstrip() for line in lines]
	return lines
			
	return rows

def AllWords(DataDir,DstDir):
	# """
	# Gathering AllWords of the Dataset. Uniquefy them 
	# And Also having a dictionary with format 'Song_ID': ['WORD1','WORD2', ...]
	# where Song_ID is a string: 01,02,03, ..., 19,20
	# returning the dictionary and writing a file called words.txt with the unique words
	# """
	AllWords = []
	All_Words_song_dict = {}
	
	for song_file in os.listdir(f"{DataDir}/lyrics"):
		with open(f"{DataDir}/lyrics/{song_file}","r") as fread:
			CurrLyrics = fread.read()
			# print(CurrLyrics)
			
			song, _ = os.path.splitext(song_file)
			clear_lyrics_list = ClearSentence(CurrLyrics).split(" ")
			All_Words_song_dict[song] = clear_lyrics_list
			for word in clear_lyrics_list:
				AllWords.append(word)
	
	# AllWords_list = AllWords.split(" ")
	UniqueWords = sorted(list(dict.fromkeys(AllWords))) # we sort and uniquefy the words.
	UniqueWords = UniqueWords[1:]	#we remove a blank "" element
	with open(f"{DstDir}/words.txt","w+") as fwrite:
		writer = "\n".join(UniqueWords)
		fwrite.writelines(writer)
	# print(UniqueWords)
	# print(Words_per_song)
	return All_Words_song_dict
###########################################
def ClearSentence(sentence): 
	# makes sentence string UPPERCASE and removes NewLines 
	# and Pantuation Marks (e.g. "...",".","?") except apostrophs " ' "
    #####################################
	# lower case
    sentence = sentence.lower()

    # GreekAB = "α β γ δ ε ζ η ή θ ι κ λ μ ν ξ ο π ρ σ τ υ φ χ ψ ω ς".split()
	# GreekOtherChars = "ΐ ϊ ΰ ϋ ά έ ή ί ό ύ ώ".split()
    EnglishAB = 'a b c d e f g h i j k l m n o p q r s t u v w x y z'.split(" ")
    Numbers = '0 1 2 3 4 5 6 7 8 9'.split(" ")
    ExtraChars = "[ ] _ / ' - ( )".split(" ")  # maybe try with panctuation marks with different silence phones for each one
    
    allowed = [" "] + EnglishAB + Numbers + ExtraChars #+ GreekAB + GreekOtherChars 
	
    sentence = re.sub("\n+"," ",sentence)
    sentence = re.sub("-"," ", sentence)

    filtered = "".join([letter for letter in sentence if letter in allowed])

	# remove possible double spaces and spaces at the beginning and at the end of the sentence
    extra_filtered = re.sub(' +', ' ',filtered) # more than one space
    return extra_filtered.upper()
################################################
def phones4utt(DataDir,utt_list):
	#
	#where utt_id is a string with format: '<spkr_id>-<song_id>' (e.g.: 'ADIZ-01')
	#Input: 
	# 		DataDIr: the general directory of the Dataset
	#		utt_list: a list with all the utts we want phones for
	#Output:
	#		phones_per_utt: dictionary with keys the utt_id 
	# 									and values a list with all the phones for each utt
	#################
	phones_per_utt = {}
	for utt in utt_list:
		spkr = utt.split("-")[0]
		CWD = os.path.join(DataDir,"audio",spkr,"sing")
		utt_file = f"{utt}.txt"
		phones = []
		with open(os.path.join(CWD,utt_file),"r") as fread:
			reader = fread.read()
			#reading the lines of the file
			lines = reader.split("\n")
			for line in lines:
				if line != "":
					# if utt_name == "ADIZ-09":
					# 	temp = line.split(" ")[2]
					# 	print(temp, i)
					phones.append(line.split(" ")[2])
		phones_per_utt[utt] = phones
	return phones_per_utt
###############################################################
def Create_utt2paths_lists(WavDir):
	print("#######\nExtracting abs paths for Utts" + \
		f"in directory {WavDir}\n#######")
	utt_list, path_list = [], []
	for file in os.listdir(WavDir):
		file_name, _= os.path.splitext(file)
		path_list.append(os.path.join(WavDir,file))
		utt_list.append(file_name)
	return utt_list, path_list

def Create_utt_song_spkr_list(WavDir):
	print("#######\nExtracting Utts and songs names from file names" + \
		f"from directory:\n{WavDir}\n########")
	# good_utts_dir = "ready_good_utts"
	utt_list, song_list, spkr_list= [],[],[]
	for file in os.listdir(WavDir):
		file_name, file_ext = os.path.splitext(file)
		if file_ext == ".wav":
			utt_list.append(file_name)
	utt_list = sorted(utt_list)
	for utt in utt_list:
		spkr,song = utt.split("-")
		song_list.append(song)
		spkr_list.append(spkr)
		print(utt,spkr,song)

	return utt_list,song_list, spkr_list

def check_if_elem_of_2lists_match(list1,list2):
	c1,c2,c3 = 0,0,0
	diff = len(list1)-len(list2)	
		
	if diff > 0:
		i=0
		print("\n#############")
		print("WRONG!\n")
		
		for i, phone_seq in enumerate(list2):
			phones = phone_seq.replace_elem_in_list(":"," ")
			
			print(list1[i]+" "+phones)
		print("#############\n")
		c1+=1
	elif diff<0:
		print("\n#############")
		print("WRONG!\n")
		for i in range(len(list1)):
			phones = list2[i].replace_elem_in_list(":"," ")
			
			print(list1[i]+" "+phones)
		print("#############\n")
		c2+=1
	else:
		print("right!")
		c3+=1
	cwrong = c1+c2
	tot = c1+c2+c3
	print(f"Number of mismatches: {cwrong}/{tot} \nNumber of matches: {c3}/{tot}")

def gather_words_from_text(text_file):
	# 
	#  extracts all the unique words from the text file
	############################
	lines = read_lines_and_strip_ends(text_file)
	all_words=[]
	for line in lines:
		words = line.split(" ")[1:]
		for word in words:
			all_words.append(word)
	unique_words = uniquefy(all_words)
	return unique_words

def gather_words_from_lexicon(lexicon_file):
	# 
	#  extracts all the unique words from the lexicon.txt file
	############################
	lines = read_lines_and_strip_ends(lexicon_file)
	all_words=[]
	for line in lines:
		word = line.split("\t")[0]
		all_words.append(word)
	unique_words = uniquefy(all_words)
	return unique_words

def check_list_elems_1_by_1(listA, listB):
	smaller_list = listA if len(listA) < len(listB) else listB
	other_list = listA if len(listA) > len(listB) else listB

	for i, elemA in enumerate(smaller_list):
		if elemA != other_list[i]:
			print(f"\n~~~{elemA}!={other_list[i]}~~~")

def split_txt_file(txt_file, split_num=1):
	# creating a list with the lines of the file separated
	lines = read_lines_and_strip_ends(txt_file)
	
	# getting the path and name of the file
	file_dir, filename = os.path.split(txt_file)
	# insert the current working dir if no full path is provided
	if file_dir == "":
		file_dir = os.getcwd()
	# split the filename of the file into basename name and extension (.txt)
	basename, ext = os.path.splitext(filename)
	# exit if the extension is not ".txt"
	if ext != ".txt":
		print("####### only '.txt' files are acceptable #########")
		return
	# the lines below are only for testing purposes
	# # delete existing files with the same name.
	# for file_part in os.listdir(file_dir):
	# 	tmp = file_part
	# 	if re.sub(r"_\d+\.txt",".txt", tmp) == file and re.search(r"_\d+\.txt", tmp):
	# 		print("removing file:" + file_part)
	# 		os.remove(file_part)

	# creating a new directory to store the splitted txt file
	dest_dir = os.path.join(file_dir, f"{basename}_split_{split_num}")
	if not os.path.isdir(dest_dir):
		os.mkdir(dest_dir)

	# # again for testing purposes
	# # deleting files that maybe already exist 
	# # in the directory where we save our splitted files
	# for file_part in os.listdir(dest_dir):
	# 	tmp = file_part
	# 	if re.sub(r"_\d+\.txt",".txt", tmp) == file and re.search(r"_\d+\.txt", tmp):
	# 		print("removing file:" + file_part)
	# 		os.remove(os.path.join(dest_dir, file_part))
	count = 1
	# get a cap on the lines that each split will include
	line_number_per_file = len(lines) / split_num
	line_limit = line_number_per_file
	
	# iterating through the txt file so we can split it
	for i, line in tqdm(enumerate(lines), unit="lines", ):
		# creating a unique file name for each split
		n_file_path = os.path.join(dest_dir,f"{basename}_{count}.txt")
		# writing the line into the current split
		with open(n_file_path,"a+") as fwrite:
			fwrite.write(line + "\n")
		# when we reach the line_limit increase the line_limit and count
		# so we can go to the next split
		if i > line_limit:
			line_limit += line_number_per_file
			print(f"writing file: {n_file_path}")
			count += 1