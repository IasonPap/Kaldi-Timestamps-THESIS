import os
import pathlib

AudioPath = "../../../nus-smc-corpus_48/"

os.chdir(AudioPath)


SingerIDs = [] 
SongsDict = {}
DiffUtts = ["read","sing"]

# with open("SPEAKERS.txt","r") as fspk:
#     reader = fspk.read()
#     lines = reader.split("\n")
#     for row in lines:
#         CurrSpkID = row.split("\t")[0]
#         SingerIDs.append(CurrSpkID)
        
#         SongsDict[CurrSpkID] = row.split("\t")[1].split(",")



# print(SingerIDs)
# print(SongsDict)

for CurrSpk in os.listdir("audio"):
    for folder in DiffUtts:
        for filename in os.listdir("audio/" + CurrSpk + "/" + folder):
            # SongsName = filename.split("_")[1]
            dst = f"audio/{CurrSpk}/{folder}/{CurrSpk}-{SongsName}"
            src = f"audio/{CurrSpk}/{folder}/{filename}"
            print(src)
            os.rename(src,dst)
            