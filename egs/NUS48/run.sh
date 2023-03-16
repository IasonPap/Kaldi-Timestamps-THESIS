#!/bin/bash


# Set this to somewhere where you want to put your NUS48 data, or where
# someone else has already put it.    You'll want to change this
# if you're not on the CLSP grid.
data=/media/datadisk/greg/Jason/mirex_data/NUS48/ready_good_utts/audio # CHANGE THIS


. ./cmd.sh
. ./path.sh
. ./utils/parse_options.sh

# you might not want to do this for interactive shells.
set -e

mfccdir=mfcc #mfcc dir inside /exp folder

librispeech_dir=../my_librispeech/s5
DAMPB_dir=../DAMPB_150songs

# train and lang directories inside /data folder
train_dir=train_all48utts # directory with text, wav.scp etc. files for NUS48
lang_dir=lang_all48utts_no_extra_phones

if [ $stage -eq 1 ]; then
	log_file=stage_$stage.log

	# creating the wav.scp file 

	# REPLACE "/path/to/wavfiles/" with the folder containing your wavfiles
	echo -e "\n" `date` "Running scripts/create_wavscp.py\n" >> $log_file
	python scripts/create_wavscp.py /path/to/wavfiles/ data/train >> $log_file
	echo -e "\n#####\n" >> $log_file
fi

if [ $stage -eq 2 ]; then
	log_file=stage_$stage.log

	for file in text utt2spk wav.scp; do
		sed -i 's/\r//g' data/train_all48utts/$file
	done
	
	utils/fix_data_dir.sh data/train_all48utts >> $log_file

fi

if [ $stage -eq 3 ]; then
	log_file=stage_$stage.log


	echo `date` ": making mfcc features" >> $log_file
	steps/make_mfcc.sh --cmd "$train_cmd" --write_utt2dur false data/$part exp/make_mfcc/$part $mfccdir >> $log_file
	

	
	echo `date` ": computing cmvn stats" >> $log_file
	steps/compute_cmvn_stats.sh data/train_all48utts exp/make_mfcc/train_all48utts $mfccdir >> $log_file
	echo `date` ": Done cmvn stats" >> $log_file
	 
	utils/validate_data_dir.sh data/train_all48utts >> $log_file
	utils/fix_data_dir.sh data/train_all48utts >> $log_file
	echo `date` ": Done fixing and validating data" >> $log_file
	# done

fi

if [ $stage -eq 4 ]; then
	log_file=stage_$stage.log

	

	#removing carriage return characters from the data/train files
	for file in lexicon.txt nonsilence_phones.txt silence_phones.txt optional_silence.txt; do
		sed -i 's/\r//g' data/local/$lang_dir/$file
	done

	echo -e "\n" `date` " PREPARING LANG DIRECTORY\n" >> $log_file
		#populating data/lang
	./utils/prepare_lang.sh data/local/$lang_dir '<UNK>' \
							data/local/lang_tmp data/$lang_dir >> $log_file


#    # Create ConstArpaLm format language model for full 3-gram and 4-gram LMs
#    utils/build_const_arpa_lm.sh data/local/lm/lm_tglarge.arpa.gz \
#        data/lang_nosp data/lang_nosp_test_tglarge
#    utils/build_const_arpa_lm.sh data/local/lm/lm_fglarge.arpa.gz \
#        data/lang_nosp data/lang_nosp_test_fglarge
fi

if [ $stage -eq 5 ]; then
	log_file=stage_$stage\_speech.log

	# EVALUATING THE SPEECH ONLY MODEL
	model=exp/tri4b
	
	# RE-CREATING THE LANG DIRECTORY ACCORDING TO THE tri4b SPEECH MODEL
	# Now we compute the pronunciation and silence probabilities from training data,
	# and re-create the lang directory.
	echo -e "\n" `date` "Re-Creating the 'lang' directory for SPEECH MODEL" >> $log_file
	steps/get_prons.sh --cmd "$train_cmd" \
                     data/$train_dir data/$lang_dir exp/$model\_align >> $log_file
	echo `date` >> $log_file
	utils/dict_dir_add_pronprobs.sh --max-normalize true \
                                  $librispeech_dir/data/local/dict_nosp \
                                  $librispeech_dir/$model/pron_counts_nowb.txt $librispeech/$model/sil_counts_nowb.txt \
                                  $librispeech_dir/$model/pron_bigram_counts_nowb.txt data/local/lang_$model\_prons >> $log_file
	echo `date` >> $log_file
	utils/prepare_lang.sh data/local/lang_$model\_prons \
                        "<UNK>" data/local/lang_tmp data/lang_$model\_updated_from_data >> $log_file
#   echo `date` >> $log_file
#   local/format_lms.sh --src-dir data/lang data/local/lm>> $log_file
#   echo `date` >> $log_file
#   utils/build_const_arpa_lm.sh \
#     data/local/lm/lm_tglarge.arpa.gz data/lang data/lang_tglarge >> $log_file

	updated_lang_dir=lang_$model\_updated_from_data

	echo -e "\n " `date` "Aligning NUS48 dataset using tri4b and the updated lang directory" >> $log_file
	
	steps/align_fmllr.sh --nj 5 --beam 40 --retry_beam 100 --cmd "$train_cmd" \
						data/$train_dir data/$updated_lang_dir \ #replace $lang_dir if you want to align with og lang dir
						$librispeech_dir/$model exp/$model\_align >> $log_file

	echo `date` "Creating the time alignment file" >> $log_file
	steps/get_train_ctm.sh --cmd "$train_cmd" --use-segments false --frame_shift 0.01\
							data/$train_dir data/$lang_dir \
							exp/$model\_align exp/$model\_align/ctm_align >> $log_file

fi
if [ $stage -eq 6 ]; then
	log_file=stage_$stage\_speech+sing.log

	# EVALUATING THE HYBRID (speech+sing) MODEL
	model=$DAMPB_dir/exp/tri5b_sing 
	
	# RE-CREATING THE LANG DIRECTORY ACCORDING TO THE tri5b_sing HYBRID MODEL
	# Now we compute the pronunciation and silence probabilities from training data,
	# and re-create the lang directory.
	echo -e "\n" `date` "Re-Creating the 'lang' directory for SPEECH MODEL" >> $log_file
	steps/get_prons.sh --cmd "$train_cmd" \
                     data/$train_dir data/$lang_dir exp/$model\_align >> $log_file
	echo `date` >> $log_file
	utils/dict_dir_add_pronprobs.sh --max-normalize true \
                                  $librispeech_dir/data/local/dict_nosp \
                                  $librispeech_dir/$model/pron_counts_nowb.txt $librispeech/$model/sil_counts_nowb.txt \
                                  $librispeech_dir/$model/pron_bigram_counts_nowb.txt data/local/lang_$model\_prons >> $log_file
	echo `date` >> $log_file
	utils/prepare_lang.sh data/local/lang_$model\_prons \
                        "<UNK>" data/local/lang_tmp data/lang_$model\_updated_from_data >> $log_file
#   echo `date` >> $log_file
#   local/format_lms.sh --src-dir data/lang data/local/lm>> $log_file
#   echo `date` >> $log_file
#   utils/build_const_arpa_lm.sh \
#     data/local/lm/lm_tglarge.arpa.gz data/lang data/lang_tglarge >> $log_file

	updated_lang_dir=lang_$model\_updated_from_data

	echo -e "\n " `date` "Aligning NUS48 dataset using tri4b and the updated lang directory" >> $log_file
	
	steps/align_fmllr.sh --nj 5 --beam 40 --retry_beam 100 --cmd "$train_cmd" \
						data/$train_dir data/$updated_lang_dir \ #replace $lang_dir if you want to align with og lang dir
						$librispeech_dir/$model exp/$model\_align >> $log_file

	echo `date` "Creating the time alignment file" >> $log_file
	steps/get_train_ctm.sh --cmd "$train_cmd" --use-segments false --frame_shift 0.01\
							data/$train_dir data/$lang_dir \
							exp/$model\_align exp/$model\_align/ctm_align >> $log_file
	
fi
if [ $stage -eq 7 ]; then
	log_file=stage_$stage.log

	# EVALUATING THE Sing only MODEL
	model=$DAMPB_dir/exp/tri3_singOnly 
	
	# RE-CREATING THE LANG DIRECTORY ACCORDING TO THE tri3_singOnly SING MODEL
	# Now we compute the pronunciation and silence probabilities from training data,
	# and re-create the lang directory.
	echo -e "\n" `date` "Re-Creating the 'lang' directory for SPEECH MODEL" >> $log_file
	steps/get_prons.sh --cmd "$train_cmd" \
                     data/$train_dir data/$lang_dir exp/$model\_align >> $log_file
	echo `date` >> $log_file
	utils/dict_dir_add_pronprobs.sh --max-normalize true \
                                  $librispeech_dir/data/local/dict_nosp \
                                  $librispeech_dir/$model/pron_counts_nowb.txt $librispeech/$model/sil_counts_nowb.txt \
                                  $librispeech_dir/$model/pron_bigram_counts_nowb.txt data/local/lang_$model\_prons >> $log_file
	echo `date` >> $log_file
	utils/prepare_lang.sh data/local/lang_$model\_prons \
                        "<UNK>" data/local/lang_tmp data/lang_$model\_updated_from_data >> $log_file
#   echo `date` >> $log_file
#   local/format_lms.sh --src-dir data/lang data/local/lm>> $log_file
#   echo `date` >> $log_file
#   utils/build_const_arpa_lm.sh \
#     data/local/lm/lm_tglarge.arpa.gz data/lang data/lang_tglarge >> $log_file

	updated_lang_dir=lang_$model\_updated_from_data

	echo -e "\n " `date` "Aligning NUS48 dataset using tri4b and the updated lang directory" >> $log_file
	
	steps/align_fmllr.sh --nj 5 --beam 40 --retry_beam 100 --cmd "$train_cmd" \
						data/$train_dir data/$updated_lang_dir \ #replace $lang_dir if you want to align with og lang dir
						$librispeech_dir/$model exp/$model\_align >> $log_file

	echo `date` "Creating the time alignment file" >> $log_file
	steps/get_train_ctm.sh --cmd "$train_cmd" --use-segments false --frame_shift 0.01\
							data/$train_dir data/$lang_dir \
							exp/$model\_align exp/$model\_align/ctm_align >> $log_file
	
	
fi
if [ $stage -eq 8 ]; then
	log_file=stage_$stage.log

	

	
fi
if [ $stage -eq 9 ]; then
	log_file=stage_$stage.log

	

	
fi
if [ $stage -eq 10 ]; then
	log_file=stage_$stage.log
	
	# $DAMPB_dir/exp/tri5b_sing # HYBRID sing+speech model
	# $DAMPB_dir/exp/tri3_singOnly # sing only model
	
fi
if [ $stage -eq 11 ]; then
  log_file=stage_$stage.log
  
  
fi

