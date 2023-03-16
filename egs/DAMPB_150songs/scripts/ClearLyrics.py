import os
import csv
import re

def ClearSentence(sentence): #makes sentence string UPPERCASE and removes NewLines and Pantuation Marks (e.g. "...",".","?") except apostrophs " ' "
    # lower case
    sentence = sentence.lower()

    # GreekAB = "α β γ δ ε ζ η ή θ ι κ λ μ ν ξ ο π ρ σ τ υ φ χ ψ ω ς".split()
	# GreekOtherChars = "ΐ ϊ ΰ ϋ ά έ ή ί ό ύ ώ".split()
    EnglishAB = 'a b c d e f g h i j k l m n o p q r s t u v w x y z'.split(" ")
    Numbers = '0 1 2 3 4 5 6 7 8 9'.split(" ")
    ExtraChars = "[ ] _ / ' - ( )".split(" ")  # maybe try with panctuation marks with different silence phones for each one
    
    allowed = [" "] + EnglishAB + Numbers + ExtraChars #+ GreekAB + GreekOtherChars 
	
    sentence = re.sub("\n+"," ",sentence)

    filtered = "".join([letter for letter in sentence if letter in allowed])

	# remove possible double spaces and spaces at the beginning and at the end of the sentence
    extra_filtered = re.sub(' +', ' ',filtered) # more than one space
    return extra_filtered.upper()

def ClearingLyrics():
    OldLyricsPath = "LyricsText"
    NewLyricsPath = OldLyricsPath + "Clear"
    CurrentSongLyrics = []
    for filename in os.listdir(OldLyricsPath):
        with open(f"{OldLyricsPath}/{filename}","r") as fread:
            
            CurrentSongLyrics=fread.read()
            ClearedCurrentSongLyrics = ClearSentence(CurrentSongLyrics)

            # if filename == "bed_intruder.txt":
            #     print(ClearedCurrentSongLyrics)
        with open(f"{NewLyricsPath}/{filename}","w+") as fwrite:
            fwrite.write(ClearedCurrentSongLyrics)


if __name__ == '__main__':      
    # Calling main() function 
    ClearingLyrics() 

