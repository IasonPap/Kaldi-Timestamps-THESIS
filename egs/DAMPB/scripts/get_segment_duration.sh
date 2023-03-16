#!/bin/bash

###################################
# This script has:
# 	INPUT
#		perf_dir: the directory of an performance	
#	OUTPUT
#		dst_dir: the directory where it puts the segments file 
#				 with the timestamps of beginning and end, in format:
#				 <segment_id> <perf_id> <seg-start-time> <seg-end-time>
###################################




# start configuration section
# test_perf_dir: DAMPB_6903/wavsegments_30sec/68922370/68922370_28088456
# test_dst_dir: LOGS/tmp_segments
perf_dir=$1
dst_dir=$2
# end configuration section

# makes the working directory if id doesn't exist
mkdir -p $dst_dir 
for segment in $perf_dir/*; do
	perf_id=$(echo "$segment" | cut -d "/" -f 4) 
	seg_id=$(echo "$segment" | cut -d "/" -f 5 | cut -d "." -f 1)
	seg_num=$(echo "$segment" | cut -d "/" -f 5 | rev |\
			 cut -d "_" -f 1 | cut -d "." -f 2 | rev)
	# get the duration for each segment
	segment_dur=$(ffmpeg -i $segment 2>&1 |	grep -e "Duration: 00:00:[0-9][0-9]\.[0-9][0-9]" |\
		awk -F'00:00:' '{print $2}' |\
		awk -F', ' '{print $1}')
	if [[ "$seg_num" == "01" ]]; then
		start_time="0.00"
		end_time=$segment_dur
		echo "$seg_id $perf_id $start_time $end_time"  > $dst_dir/segments
		
	else
		start_time=$end_time
		
		end_time=$(echo "$start_time + $segment_dur" | bc)
		# exit 1s
		echo "$seg_id $perf_id $start_time $end_time"  >> $dst_dir/segments
	fi
	echo $seg_num	
	# i=$(echo "$i ++" | bc)
done