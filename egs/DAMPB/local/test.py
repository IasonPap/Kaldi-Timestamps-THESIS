#!/usr/bin/python3


import csv, os
METADATA_PATH = "/media/datadisk/greg/Jason/mirex_data/DAMPB_6903/DAMPBperfs.csv"

# with open(METADATA_PATH, "r") as fread:
# 		Header = ["singer_account_id","performance_id","song_title","singer_gender","singer_birth_year","","Language"]
# 		reader = csv.DictReader(fread, fieldnames=Header)
# 		for row in reader:
# 			print(row["song_title"])

print(os.getcwd())        