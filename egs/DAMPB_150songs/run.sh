#!/bin/bash

mfccdir=mfcc
stage=$1

. ./cmd.sh
. ./path.sh
. ./utils/parse_options.sh

set -e

# IMPORTANT DIRECTORIES THAT MAYBE NEEDS TO BE CHANGED	
librispeech_dir=../my_librispeech/s5 #CHANGE THIS to the directory where you have your librispeech models

DAMPB_lang_dir=DAMPB_no_extra_prons # where the language Model for the DAMPB dataset will be duilt
# data/lang_no_extra_phones_new # the updated language Model if you run the step 13 for the librispeech model


if [ $stage -eq 1 ]; then
	log_file=stage_$stage.log
	
	# REPLACE "/path/to/wavfiles/" with the folder containing your wavfiles
	echo -e "`date` \nRunning scripts/create_wavscp.py\n" >> $log_file
	python scripts/create_wavscp.py /path/to/wavfiles/ data/train >> $log_file
	echo -e "\n#####\n" >> $log_file
	#creating the spk2utt file and fixing files in data/train
	utils/fix_data_dir.sh data/train >> $log_file

	
	# #populating data/local/lang directory (lexicon.txt already exists)
	# # creating nonsilence_phones.txt. syntax: nonsilence_phones.py <lexicon-dir>
	# python scripts/nonsilence_phones.py data/local/lang/lexicon.txt
	# # creating silence_phones.txt
	# echo -e 'SIL'\\n'SPN'\\n'CLAP' > $lexicon_dir/silence_phones.txt
	# # creating optional_silence.txt
	# echo 'SIL' > $lexicon_dir/optional_silence.txt

	# removing carriage return characters from the data/train files
	for file in lexicon.txt nonsilence_phones.txt silence_phones.txt optional_silence.txt; do
		sed -i 's/\r//g' data/local/dict_DAMPB_no_extra_prons/$file
	done
	echo -e "\n PREPARING LANG DIRECTORY\n" `date` > $log_file
	#populating data/lang
	utils/prepare_lang.sh data/local/$DAMPB_lang_dir '<UNK>'\
						data/local/lang_tmp data/$DAMPB_lang_dir >> $log_file


fi
if [ $stage -eq 2 ]; then
	
	log_file=stage_$stage.log

	#removing carriage return characters from the data/train files
	for file in text utt2spk wav.scp; do
		sed -i 's/\r//g' data/train/$file
	done
	mfccdir=mfcc
	part=train
	#creating MFCC features	
	echo `date` ": making mfcc features" >> $log_file
	steps/make_mfcc.sh --cmd "$train_cmd" --nj 10 data/$part exp/make_mfcc/$part $mfccdir  >> $log_file
	echo `date` ": computing cmvn stats" >> $log_file
	#creating cmvn features
	steps/compute_cmvn_stats.sh data/$part exp/make_mfcc/$part $mfccdir >> $log_file

fi
if [ $stage -eq 3 ]; then
	log_file=exp/tri4b_sing.log

	# CREATING THE HYBRID MODEL
	echo -e "\n " `date` "Aligning DAMPB_150songs dataset using tri4b"  >> $log_file
	steps/align_fmllr.sh --nj 5 --beam 40 --retry_beam 100 --cmd "$train_cmd" \
						data/train data/$DAMPB_lang_dir \
						$librispeech_dir/exp/tri4b exp/tri4b_align >> $log_file
	echo -e "\n " `date` "Training LDA + MLLT + SAT " >> $log_file
	#train a simple triphone model using the singing datasets based on the tri4b from librispeech
	steps/train_sat.sh --beam 40 --retry_beam 100 --cmd "$train_cmd" 10000 200000 \
						data/train data/$DAMPB_lang_dir \
						exp/tri4b_align exp/tri4b_sing >> $log_file

fi
if [ $stage -eq 4 ]; then
  log_file=exp/tri4b_sing_lang.log
  # Now we compute the pronunciation and silence probabilities from training data,
  # and re-create the lang directory.
  echo -e "\nRe-Creating the 'lang' directory" >> $log_file
  echo `date` >> $log_file
  steps/get_prons.sh --cmd "$train_cmd" \
                     data/train data/$DAMPB_lang_dir exp/tri4b_sing >> $log_file
  echo `date` >> $log_file
  utils/dict_dir_add_pronprobs.sh --max-normalize true \
                                  data/$DAMPB_lang_dir \
                                  exp/tri4b_sing/pron_counts_nowb.txt exp/tri4b_sing/sil_counts_nowb.txt \
                                  exp/tri4b_sing/pron_bigram_counts_nowb.txt data/local/$DAMPB_lang_dir\_prons >> $log_file
  echo `date` >> $log_file
  utils/prepare_lang.sh data/local/$DAMPB_lang_dir\_prons \
                        "<UNK>" data/local/lang_tmp data/$DAMPB_lang_dir\_updated_from_data >> $log_file

fi
if [ $stage -eq 5 ]; then
log_file=exp/tri5b_sing.log

	updated_lang_dir=data/$DAMPB_lang_dir\_updated_from_data # replace this if you want to use the original lang dir

	echo -e "\n " `date` " Aligning DAMPB_150songs dataset using tri4b with the updated lang dir"  >> $log_file
	steps/align_fmllr.sh --nj 5 --beam 40 --retry_beam 80 --cmd "$train_cmd" \
						data/train $updated_lang_dir \
						exp/tri4b_sing exp/tri4b_sing_align >> $log_file
	echo -e "\n " `date` " Training LDA + MLLT + SAT "  >> $log_file
	#train a simple triphone model using the singing datasets based on the tri4b from librispeech
	steps/train_sat.sh --beam 40 --retry_beam 100 --cmd "$train_cmd" 10000 200000 \
						data/train $updated_lang_dir \
						exp/tri4b_sing_align exp/tri5b_sing >> $log_file

fi
# creating a model on singing data from scratch
if [ $stage -eq 6 ]; then
	log_file=exp/mono_singOnly.log
	echo -e "\n " `date` "Training a MONOPHONE model\n"  >> $log_file
	# trains a monophone model on the train_2kshort set (default num_iters=40)
	steps/train_mono.sh --boost-silence 1.25 --num_iters 40 --totgauss 2000 --retry_beam 80 \
						--nj 10 --cmd "run.pl" \
						data/train \
						$DAMPB_lang_dir \
						exp/mono_singOnly >> $log_file
	
	echo "FINISHED with mono at:" `date` >> $log_file
	
fi
if [ $stage -eq 7 ]; then
  log_file=exp/tri1_singOnly.log
  echo -e "\n " `date` " Aligning using the monophone model\n" >> $log_file
  steps/align_si.sh --boost-silence 1.25 --nj 10 --cmd "$train_cmd" --retry_beam 80 \
                    data/train data/$DAMPB_lang_dir \
					exp/mono_singOnly exp/mono_singOnly_ali >> $log_file
  echo -e "\n " `date` " Training triphone with deltas \n" >> $log_file
  # train a first delta + delta-delta triphone system on a subset of 5000 utterances  # num_iters = 35 default
  # original: numleaves=2000 totgauss=50000
  steps/train_deltas.sh --boost-silence 1.25 --cmd "$train_cmd" \
                        2000 50000 \
						data/train data/$DAMPB_lang_dir \
						exp/mono_singOnly_ali exp/tri1_singOnly >> $log_file


fi
if [ $stage -eq 8 ]; then
  log_file=exp/tri2b_singOnly.log
  echo -e "\n " `date` " aligning using tri1_sing" >> $log_file
  steps/align_si.sh --nj 10 --cmd "$train_cmd" \
                    data/train data/$DAMPB_lang_dir exp/tri1_singOnly exp/tri1_singOnly_ali >> $log_file


  # train an LDA+MLLT system.  # num_iters = 35 default
  #original: numleaves=5000 totgauss=50000 (from github: numleaves=2500 totgauss=15000) TODO: binary search to find optimal
  #original: left-context=3 right-context=3 (same as github) TODO: binary search to find optimal
  
	echo -e"\n" `date` " training triphone with LDA+MLLT" >> $log_file
  #best configuration
	steps/train_lda_mllt.sh --cmd "$train_cmd" --splice-opts "--left-context=10 --right-context=10" \
						  4370 75000 \
                          data/train data/$DAMPB_lang_dir exp/tri1_singOnly_ali exp/tri2_singOnly >> $log_file
	# echo `date` >> $log_file
	# utils/mkgraph.sh data/lang_no_extra_phones \
    #                  exp/tri2_sing exp/tri2_sing/graph_no_extra_phones  >> $log_file
	echo "FINISHED with tri2_sing at:" `date` >> $log_file

fi

if [ $stage -eq 9 ]; then
log_file=exp/tri3_singOnly.log


  # Align a 10k utts subset using the tri2b model
  echo -e "\n " `date` " Aligning with tri2_sing" >> $log_file
  steps/align_si.sh  --nj 10 --cmd "$train_cmd" --use-graphs true --beam 30 --retry_beam 80 \
                     data/train data/$DAMPB_lang_dir exp/tri2_singOnly exp/tri2_singOnly_ali >> $log_file
  

  #typing the time when the training step started started
	echo -e "\n" `date` " Training with LDA + MLLT + SAT: " >> $log_file  
  # Train tri3b, which is LDA+MLLT+SAT on 10k utts # num_iters = 35 default
  #original: numleaves=2500 totgauss=15000 (same as github) TODO: binary search to find optimal
  steps/train_sat.sh --cmd "$train_cmd" 10000 200000 \
                    data/train data/$DAMPB_lang_dir exp/tri2_singOnly_ali exp/tri3_singOnly >> $log_file
  

  # decode using the tri3b model
#   (
#     echo -e "\n Making graph with tri3_sing" `date` >> $log_file  
#     utils/mkgraph.sh data/lang_no_extra_phones \
#                      exp/tri3_sing exp/tri3_sing/graph_no_extra_phones >> $log_file
 

fi
# extra steps if you want to split the functions above or you want to train more models
if [ $stage -eq 10 ]; then
log_file=stage_$stage.log


fi
if [ $stage -eq 11 ]; then
log_file=stage_$stage.log


fi
if [ $stage -eq 12 ]; then
log_file=stage_$stage.log


fi
if [ $stage -eq 13 ]; then
log_file=stage_$stage.log


fi
if [ $stage -eq 14 ]; then
log_file=stage_$stage.log


fi
