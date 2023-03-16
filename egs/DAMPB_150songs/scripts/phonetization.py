import nltk
import sys, os
import re


def CreateWords(text_file):  #FillingG2P
	"""
	This takes all the unique words from the transcription data/train/text
	and returns a list containing them.

	"""
	with open(text_file,"r") as reader:
		lines = reader.readlines()
		lines = [line.rstrip() for line in lines]
	all_words = []
	print(lines[:5])
	for line in lines:
		words = line.split(" ")[1:]
		for word in words:
			all_words.append(word)
	unique_words = sorted(list(dict.fromkeys(all_words)))
	with open("words.txt","w+") as writer:
		exceptions = ["","(CLAP)"]
		for word in unique_words:
			if word not in exceptions:
				writer.write(word + "\n")


# cmu_lexicon = nltk.corpus.cmudict.entries()

# phones = []
# for word_phone_tuple in cmu_lexicon:
# 	phones_list = word_phone_tuple[1]
# 	for phone in phones_list:
# 		if phone[-1] not in ["1","2","3","4",'5','6','7','8','9']:
# 			writer.write(phone + "\n")
# 		elif phone[-1] == "0":
# 		phones.append(phone)
# unique_phones = list(dict.fromkeys(phones))
# unique_phones.sort()
# with open("phones.txt","w+") as writer:
# 	for phone in unique_phones:
# 		if phone[-1] not in ["1","2","3","4",'5','6','7','8','9']:
# 			writer.write(phone + "\n")
# 		elif phone[-1] == "0":
# 			print(phone)

# with open("lexicon-draft.txt","r") as reader:
# 	lexicon = reader.readlines()
# my_lexicon_phones=[]
# for line in lexicon:
# 	stripped_line_ending = line.rstrip()
# 	# print(stripped_line_ending)
# 	splitted_line = re.split(r'\t+', stripped_line_ending)
# 	# print(splitted_line)
# 	phones = stripped_line_ending.split("\t")[1]
# 	if " " in phones:
# 		phones = phones.split(" ")
# 	for phone in phones:
# 		my_lexicon_phones.append(phone)
# with open("phones_my_lex.txt","w+") as writer:
# 	my_phones = sorted(list(dict.fromkeys(my_lexicon_phones)))
# 	for item in my_phones:
# 		writer.write(item + )

 
if __name__ == '__main__':
	if len(sys.argv) == 2:
		text_file = sys.argv[1]
		if os.path.isfile(text_file):
			 CreateWords(text_file)
		else:
			print("there is no file with that path.")
	else:
		print("this script takes EXACTLY 1 argument. The 'text' file.")

