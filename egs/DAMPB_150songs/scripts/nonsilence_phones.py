import sys, os
import functions 

if len(sys.argv) != 2:
	print("THis function accepts exactly 1 input. The path to the lexicon.")
	sys.exit()

lexicon_file = sys.argv[1]

all_phones = []
with open(lexicon_file,"r") as reader:
	text=reader.read()
	text_lines = text.splitlines(keepends=False)
	
	for line in text_lines:
		phones = line.split('\t')[1]
		phones = phones.split(' ')
		for phone in phones:		
			all_phones.append(phone)
unique_phones = sorted(functions.uniquefy(all_phones))

lexicon_dir = os.path.split(lexicon_file)[0]

with open(os.path.join(lexicon_dir,"nonsilence_phones.txt"),"w+") as writer:
	for phone in unique_phones:
		writer.write(phone+"\n")


