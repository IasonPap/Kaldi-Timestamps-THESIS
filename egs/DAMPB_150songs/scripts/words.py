import os
import re
import sys
import functions as func

if len(sys.argv) >= 2:
	text_file = sys.argv[1] #taking the first argument as the location for the text_file
	
	print(sys.argv[0] + " " + sys.argv[1]) #for log purposes
from_type = input("Get words from 'text' or 'lexicon' file (text/lexicon)")
if from_type == "text":
	unique_words = func.gather_words_from_text(text_file)
elif from_type == "lexicon":
	unique_words = func.gather_words_from_lexicon(text_file)
unique_sorted_words = sorted(unique_words)

words_filename = os.path.splitext(os.path.basename(text_file))[0]
with open(f"{words_filename}.txt","w+") as writer:
	#writing the unique words into a txt file
	exceptions = ["","CLAP","!SIL", "<SPOKEN_NOISE>", "<UNK>"]
	for word in unique_sorted_words:
		if word not in exceptions:
			writer.write(word + "\n")
if len(unique_sorted_words) > 20000:
	func.split_txt_file(words_filename, 10)
