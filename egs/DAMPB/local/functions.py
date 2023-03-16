#!/usr/bin/python3


import os
import sys
import re
######################################
# replaces all instances of old_str 
# with new_str in my_list
def replace(my_list , old_str, new_str): 
	return [new_str if x == old_str else x for x in my_list]
######################################
# reads file in file_path and returns the lines 
# as a list without the "\n".
# Also removes empty lines if the exist
def read_lines(file_path): 
	with open(file_path,"r") as fread:
		reader= fread.read()
		rows = reader.split("\n")
		if rows[-1] == "" :
			# print(f"i'm in file: {file_path}\n rows[-2]== \"{rows[-2]}\"\n")
			rows = rows[:-1]
			# print("~~~~~I'm inside IF in read_lines")
			
	return rows
###########################################
# returns the sentence as one line, ALL CAPS.
# keeps any numeral and anyone of "[ ] _ / ' - ( )" these characters
def ClearSentence(sentence): 
	# makes sentence string UPPERCASE and removes NewLines 
	# and Pantuation Marks (e.g. "...",".","?") except apostrophs " ' "
    #####################################
	# lower case
    sentence = sentence.lower()

   
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
###########################################
# parses the lyrics from unparsed_lyrics file_path
# and returns the parsed lyrics as a string
def parse_lyrics(unparsed_lyrics_file):
	with open(unparsed_lyrics_file,"r") as fread:
		reader = fread.read()
	
	parsed_lyrics = ClearSentence(reader)
	return parsed_lyrics
################################################
# 
def check_if_elem_of_2lists_match(list1,list2):
	c1,c2,c3 = 0,0,0
	diff = len(list1)-len(list2)	
		
	if diff > 0:
		i=0
		print("\n#############")
		print("WRONG!\n")
		
		for i, phone_seq in enumerate(list2):
			phones = phone_seq.replace(":"," ")
			
			print(list1[i]+" "+phones)
		print("#############\n")
		c1+=1
	elif diff<0:
		print("\n#############")
		print("WRONG!\n")
		for i in range(len(list1)):
			phones = list2[i].replace(":"," ")
			
			print(list1[i]+" "+phones)
		print("#############\n")
		c2+=1
	else:
		print("right!")
		c3+=1
	cwrong = c1+c2
	tot = c1+c2+c3
	print("Number of mismatches: {0}/{2} \nNumber of matches: {1}/{2}".format(cwrong,c3,tot))
###########################
# for debugging purposes 
# printing the function, line and a debug message 
# from when the function is called
def debug(message):
    import inspect
    callerframerecord = inspect.stack()[1]
    frame = callerframerecord[0]
    info = inspect.getframeinfo(frame)
    print('func={}, line={}: {}'.format(info.function,info.lineno, message)) 
############################
# Desc:
# Input: lyricsFolder: the rel path of the folder, which contains all the lyrics 
# 					   of the songs that we will use as our language model
# 		 dstDir: the rel path of the destination directory 
# 				 where the lm_text file will be created
def make_lm_text_from_lyrics(lyricsFolder, dstDir):
	out_string = ""
	for songfile in os.listdir(lyricsFolder):
		out_string += "<s> " + parse_lyrics(os.path.join(lyricsFolder,songfile)) + " </s>\n"
	with open(os.path.join(dstDir,"lm_text"),"w+") as fwrite:
		fwrite.write(out_string)
if __name__ == "__main__":
	print("running functions")
	if len(sys.argv)-1 == 2 and type(sys.argv[1]) == str and type(sys.argv[2]):
		print("running make_lm_text_from_lyrics")
		lyricsFolder=sys.argv[1]
		dstDir=sys.argv[2]
		print(sys.argv)
		make_lm_text_from_lyrics(lyricsFolder,dstDir)
		sys.exit()
>>>>>>> 2f83eda73a976dc2bec88618b881b37727db31eb
