import os
import sys
import re
import functions as func

def create_word_prons_tuples_from_lexicon(word_prons_lines):
	# the input must be a list with "\t" between word and pronunciation 
	# for every iteam in the list
	##################
	lexicon = []
	for line in word_prons_lines:
		word, pronunciation = line.split("\t")
		word_prons = (word, pronunciation)
		lexicon.append(word_prons)
	return lexicon

if __name__ == "__main__":
	if len(sys.argv) == 3:
		source_dict_path = sys.argv[1]
		dest_dict_path = sys.argv[2]
	print(sys.argv)

	# reading the lines from the dictionaries files
	source_dict_lines = func.read_lines_and_strip_ends(source_dict_path)
	dest_dict_lines = func.read_lines_and_strip_ends(dest_dict_path)

	# creating dictionary with keys: words and values: phonemes pronunciations
	# for source
	source_dict = create_word_prons_tuples_from_lexicon(source_dict_lines)
	# for dest
	dest_dict = create_word_prons_tuples_from_lexicon(dest_dict_lines)
	
	# creating word list for source_dict so we then find 
	# the word we're lookign for
	source_words_list = [word_pron_pair[0] for word_pron_pair in source_dict]


	out_dict_path = os.path.join(os.path.split(dest_dict_path)[0],"mixed_lexicon.txt")
	fwrite = open(out_dict_path,"w+")
	
	# we iterate through all the words of the source dict
		
	for i, word_pron in enumerate(dest_dict):
		# separating the word pronunciations pairs from dest_dict
		word = word_pron[0]
		pron = word_pron[1]

		if word != word.split("(")[0]:
			print(f"~~~~~{word}~~~~~~~{word.split('(')[0]}")
			continue
		
		# get the index of the current word from the source dictionary
		index = func.find_string(source_words_list, word)
		
		if index == None: 
			# if the word isn't in the source_dict go to the next one
			# and write it as is
			fwrite.write(f"{word}\t{pron}\n")
		else:	
			# go back the source list to get 
			# to the first pronunciation of current word
			tmp_word = word
			first_pron_index = index
			while tmp_word == word:
				first_pron_index -= 1
				tmp_word = source_dict[first_pron_index][0]
			first_pron_index += 1
			# after we reached the first pron, 
			# continue to write the pronunciations for the current word 
			# from the source dictionary
			tmp_word = source_dict[first_pron_index][0]
			while tmp_word == word:
				fwrite.write(f"{tmp_word}\t{source_dict[first_pron_index][1]}\n")
				first_pron_index += 1
				tmp_word = source_dict[first_pron_index][0]
			
			# print(re.findall(r"[AEIOU][YWHROEA]\d",source_dict[first_pron_index][1]))
			# print(re.sub())
			# print("######################")
			
	fwrite.close()
	# print("\ntesting output list")
	# out_dict_lines = func.read_lines_and_strip_ends(out_dict_path)
	# func.check_list_elems_1_by_1(out_dict_lines, dest_dict_lines)
		
		
	
	
	
	
