#!/bin/bash


# Set this to somewhere where you want to put your data, or where
# someone else has already put it.    You'll want to change this
# if you're not on the CLSP grid.
data=/media/datadisk/greg/Jason/mirex_data/DAMPB_6903

# base url for downloads.
# data_url=www.openslr.org/resources/12
# lm_url=www.openslr.org/resources/11
mfccdir=mfcc
stage=$1
train=$2
. ./cmd.sh
. ./path.sh
. ./utils/parse_options.sh

# you might not want to do this for interactive shells.
set -e

export LC_ALL=C

if [ $stage -eq 1 ]; then
	
	#creating text, wav.scp and utt2spk files
	echo "Preparing text, wav.scp and utt2spk"
	# python3 local/acoust_data_prep.py $data data --text --wav --utt2spk

	#creating spk2utt and fixing data
	for part in train0.8 test0.2; do
		sort -k1,1 -u -o data/$part/text data/$part/text
		sort -k1,1 -u -o data/$part/wav.scp data/$part/wav.scp
		sort -k1,1 -u -o data/$part/utt2spk data/$part/utt2spk
		utils/utt2spk_to_spk2utt.pl data/$part/utt2spk > data/$part/spk2utt
		./utils/validate_data_dir.sh --no-feats data/$part || exit 1;
		./utils/fix_data_dir.sh data/$part || exit 1;
		
	done
	# # Creating the words.txt file
	# # cut -d ' ' -f 2- text | sed 's/ /\n/g' | sort -u > words.txt
	# echo "Parsing Lyrics for all the songs in dataset"
	# python local/lang_data_prep.py $data data/local/lang -w
fi
if [ $stage -eq 2 ]; then
	
	# turning all the audio data to RIFF-wav sr=44.1kHz mono 1 channel
	pre_wav_dir=$data/audio
	echo $pre_wav_dir
	after_wav_dir=$data/audio_44100Hz

	for singer in $pre_wav_dir/* ; do
		for part in  $singer/*.wav ; do
			ffmpeg -i $part -ac 1 -ar 44100 \
			$after_wav_dir/$(echo $part | egrep -o "[[:upper:]]{4}\-[[:digit:]]{2}\.wav")
			# /mnt/HDD_Storage/Dev/LyricsToAudio/nus-smc-corpus_48/good_utts/SAMF-09.wav
			echo $(echo $part | egrep -o "[[:upper:]]{4}\-[[:digit:]]{2}\.wav")
			echo $part
		
		done 
		echo "\n###DONE with $singer \n"
	done
	echo "\nDONE Converting files!!\n"
	
fi

## Optional text corpus normalization and LM training
## These scripts are here primarily as a documentation of the process that has been
## used to build the LM. Most users of this recipe will NOT need/want to run
## this step. The pre-built language models and the pronunciation lexicon, as
## well as some intermediate data(e.g. the normalized text used for LM training),
## are available for download at http://www.openslr.org/11/
#local/lm/train_lm.sh $LM_CORPUS_ROOT \
#    data/local/lm/norm/tmp data/local/lm/norm/norm_texts data/local/lm

## Optional G2P training scripts.
## As the LM training scripts above, this script is intended primarily to
## document our G2P model creation process
#local/g2p/train_g2p.sh data/local/dict/cmudict data/local/lm

if [ $stage -eq 3 ]; then
	# when the "--stage 3" option is used below we skip the G2P steps, and use the
	# lexicon we have already downloaded from openslr.org/11/

	lexicon_dir=data/local/lang

	#creating nonsilence_phones.txt
	# local/prepare_dict.sh --stage 3 --nj 10 --cmd "$train_cmd" \
	#    data/local/lm data/local/lm data/local/lang
	
	(cut -d ' ' -f 2- $lexicon_dir/lexicon.txt | \
	sed "s/ /\n/g" | sort -u ) > $lexicon_dir/nonsilence_phones.txt


	#creating silence_phones
	echo -e 'SIL\nOOV' > $lexicon_dir/silence_phones.txt

	#creating optional silence phones
	echo 'SIL' > $lexicon_dir/optional_silence.txt

	utils/prepare_lang.sh data/local/lang \
	"OOV" data/local data/lang
	# cat data/lang/phones/sets.txt | \
	# utils/sym2int.pl data/lang/phones.txt >data/lang/phones/sets.int || exit 1;

	# local/format_lms.sh --src-dir data/lang_nosp data/local/lm
fi

if [ $stage -eq 4 ]; then
   # Create ConstArpaLm format language model for full 3-gram and 4-gram LMs
   utils/build_const_arpa_lm.sh data/local/lm/lm_tglarge.arpa.gz \
       data/lang_nosp data/lang_nosp_test_tglarge
   utils/build_const_arpa_lm.sh data/local/lm/lm_fglarge.arpa.gz \
       data/lang_nosp data/lang_nosp_test_fglarge
fi

if [ $stage -eq 5 ]; then
#    # spread the mfccs over various machines, as this data-set is quite large.
#    if [[    $(hostname -f) ==    *.clsp.jhu.edu ]]; then
#        mfcc=$(basename mfccdir) # in case was absolute pathname (unlikely), get basename.
#        utils/create_split_dir.pl /export/b{02,11,12,13}/$USER/kaldi-data/egs/librispeech/s5/$mfcc/storage \
#         $mfccdir/storage
#    fi

	# turning all the audio data to RIFF-wav sr=44.1kHz mono 1 channel
	pre_wav_dir=$data/good_utts/audio
	echo $pre_wav_dir
	after_wav_dir=$data/good_utts/audio_mono
	# if ! [ -d after_wav_dir ]; then #ΓΙΑ ΚΑΠΟΙΟ
	#        # CWD=`pwd`
	#        # cd $data
	#        echo "hello"
	#        mkdir after_wav_dir
	#        # cd CWD
	# fi
	if [ -d after_wav_dir ]; then
	for part in $pre_wav_dir/*.wav; do
		ffmpeg -i $part -ac 1 -ar 44100 \
		$after_wav_dir/$(echo $part | egrep -o "[[:upper:]]{4}\-[[:digit:]]{2}\.wav")
		# /mnt/HDD_Storage/Dev/LyricsToAudio/nus-smc-corpus_48/good_utts/SAMF-09.wav
		echo $(echo $part | egrep -o "[[:upper:]]{4}\-[[:digit:]]{2}\.wav")
		echo $part
		
		# echo $part 
	done
	echo "\nDONE Converting files!!\n"
	fi
fi



if [ $stage -eq 6 ]; then #MAKE MFCC
	# # splitting the training data in smaller chunk so to be quick 
	# # with the first training steps
	# utils/subset_data_dir.sh --shortest data/train0.8 2000 data/train_2kshort

	# part=train
	mfccdir=mfcc
	for part in train0.8 test0.2; do  
		steps/make_mfcc.sh --nj 40 --cmd "$train_cmd" data/$part exp/make_mfcc/$part $mfccdir
		utils/validate_data_dir.sh data/$part
		utils/fix_data_dir.sh data/$part
		echo "computing cmvn stats"
		steps/compute_cmvn_stats.sh data/$part exp/make_mfcc/$part $mfccdir
		echo "Done cmvn stats"
		utils/validate_data_dir.sh data/$part
		utils/fix_data_dir.sh data/$part
		echo "Done fixing and validating data"
	done
fi
if [  $stage -eq 7 ]; then
	# utils/subset_data_dir.sh --shortest data/train0.8 2000 data/train_2kshort;\
	utils/subset_data_dir.sh --shortest data/train0.8 800 data/train_800short;\
	utils/subset_data_dir.sh --shortest data/train0.8 100 data/train_100short
	utils/subset_data_dir.sh --shortest data/train0.8 200 data/train_200short
	
	# # train a monophone system	
	# steps/train_mono.sh --boost-silence 1.25 --nj 40 --cmd "$train_cmd" \
    #                   --careful true --regular_beam 40 --retry_beam 100 \
	# 				  data/train_2kshort data/lang exp/mono/2kshort &
	# wait $!
	# steps/train_mono.sh --boost-silence 1.25 --nj 20 --cmd "$train_cmd" \
    #                   --totgauss 3000 --regular_beam 40 --retry_beam 100 \
	# 				  data/train_800short data/lang exp/mono/800short 
				  
	# steps/train_mono.sh --boost-silence 1.25 --nj 20 --cmd "$train_cmd" \
    #                   --totgauss 3000 --regular_beam 40 --retry_beam 100 \
	# 				  data/train_400short data/lang exp/mono/400short 
	
	# # decode using the monophone model
	# (
	# echo "making_graph"
	# utils/mkgraph.sh data/lang_nosp_test_tgsmall \
    #                  exp/mono exp/mono/graph_2ksmall
    # test=test0.2
    # echo "decoding"
	# steps/decode.sh --nj 10 --cmd "$decode_cmd" exp/mono/graph_2ksmall \
    #                   data/$test exp/mono/decode_2ksmall_$test
    # echo "done"
	# )&
fi

if [ $stage -eq 8 ]; then
  steps/align_si.sh --boost-silence 1.25 --nj 10 --cmd "$train_cmd" \
                    data/train0.8 data/lang exp/mono/400short exp/mono_ali

  # train a first delta + delta-delta triphone system on a subset of train utterances
  steps/train_deltas.sh --boost-silence 1.25 --cmd "$train_cmd" \
                        2000 10000 data/train0.8 data/lang exp/mono_ali_train0.8 exp/tri1

  # decode using the tri1 model
  (
    utils/mkgraph.sh data/lang_nosp_test_tgsmall \
                     exp/tri1 exp/tri1/graph_2ksmall
    for test in test_clean test_other dev_clean dev_other; do
      steps/decode.sh --nj 20 --cmd "$decode_cmd" exp/tri1/graph_2ksmall \
                      data/$test exp/tri1/decode_nosp_tgsmall_$test
      steps/lmrescore.sh --cmd "$decode_cmd" data/lang \
                         data/$test exp/tri1/decode_graph_2ksmall_$test
      steps/lmrescore_const_arpa.sh \
        --cmd "$decode_cmd" data/lang \
        data/$test exp/tri1/decode
    done
  )&
fi
if [ $stage -eq 10 ]; then
	steps/align_si.sh --nj 10 --cmd "$train_cmd" \
					data/alignme data/lang exp/tri1 exp/tri1_alignme

	
fi
if [ $stage -eq 11 ]; then # aligning and get ctm
	part=alignme$sample_rate
	boost_sil=0.5

	steps/align_fmllr.sh --nj 1 --cmd "$train_cmd" --boost_silence $boost_sil \
							data/$part data/lang exp/tri3b exp/tri3b_$part

	steps/get_train_ctm.sh --nj 1 --cmd "$train_cmd" --use-segments false --frame_shift 0.01\
							data/$part data/lang exp/tri3b_$part exp/tri3b_$part/ctm
	cp exp/tri3b_$part/ctm/ctm \
	/home/jason/HDD_Storage/Dev/LyricsToAudio/nus-smc-corpus_48/KaldiFiles/KaldiAlignment/get_ctm_all_utts.txt

	## a worst way to produce ctm from alignment
	# part=alignme$sample_rate
	# mfccdir=mfcc$sample_rate
	# boost_sil=0.5
	

	# # align the entire train_clean_100 subset using the tri3b model
	# steps/align_fmllr.sh --nj 1 --cmd "$train_cmd" --boost_silence $boost_sil \
	# 						data/$part data/lang exp/tri3b exp/tri3b_$part

	# for i in  exp/tri3b_$part/ali.*.gz;
	# do src/bin/ali-to-phones --ctm-output exp/tri3b/final.mdl \
	# 	ark:"gunzip -c $i|" -> ${i%.gz}.ctm;
	# done;

	# cat exp/tri3b_$part/*.ctm > exp/tri3b_$part/merged_alignment$sample_rate-$boost_sil.txt
	# cp exp/tri3b_$part/merged_alignment$sample_rate-$boost_sil.txt \
	#    /home/jason/HDD_Storage/Dev/LyricsToAudio/nus-smc-corpus_48/KaldiFiles/KaldiAlignment
fi
if [ $stage -eq 12 ]; then
	#folders: 
	# tri2c_all: model LDA+MLLT trained on the entire train_clean_100 hrs subset
	# tri3b: model LDA+MLLT+SAT trained on librispeech 10k utts
	# tri3b_ali_clean_100: aligned the entire train_clean_100 subset using the tri3b model
	# tri4b: model LDA+MLLT+SAT trained on the entire train_clean_100 hrs subset
	# tri4b_ali_clean_100: aligned the entire train_clean_100 subset using the tri4b model
	# training LDA+MLLT+SAT model on 200 and 100 utts
	for part in 100 200 400; do
		./steps/train_sat.sh --beam 40 --retry-beam 80 \
						5000 50000 \
						data/train_${part}short data/lang ../librispeech/s5/exp/tri4b_ali_clean_100 \
						exp/tri4short_${part}utts	
	done
fi

# if [ $stage -eq 13 ]; then
#    # Now we compute the pronunciation and silence probabilities from training data,
#    # and re-create the lang directory.
#    steps/get_prons.sh --cmd "$train_cmd" \
#                                 data/train_clean_100 data/lang_nosp exp/tri4b
#    utils/dict_dir_add_pronprobs.sh --max-normalize true \
#                                                    data/local/dict_nosp \
#                                                    exp/tri4b/pron_counts_nowb.txt exp/tri4b/sil_counts_nowb.txt \
#                                                    exp/tri4b/pron_bigram_counts_nowb.txt data/local/dict

#    utils/prepare_lang.sh data/local/dict \
#                                     "<UNK>" data/local/lang_tmp data/lang
#    local/format_lms.sh --src-dir data/lang data/local/lm

#    utils/build_const_arpa_lm.sh \
#        data/local/lm/lm_tglarge.arpa.gz data/lang data/lang_test_tglarge
#    utils/build_const_arpa_lm.sh \
#        data/local/lm/lm_fglarge.arpa.gz data/lang data/lang_test_fglarge

#    # decode using the tri4b model with pronunciation and silence probabilities
#    (
#        utils/mkgraph.sh \
#            data/lang_test_tgsmall exp/tri4b exp/tri4b/graph_tgsmall
#        for test in test_clean test_other dev_clean dev_other; do
#            steps/decode_fmllr.sh --nj 20 --cmd "$decode_cmd" \
#                                            exp/tri4b/graph_tgsmall data/$test \
#                                            exp/tri4b/decode_tgsmall_$test
#            steps/lmrescore.sh --cmd "$decode_cmd" data/lang_test_{tgsmall,tgmed} \
#                                        data/$test exp/tri4b/decode_{tgsmall,tgmed}_$test
#            steps/lmrescore_const_arpa.sh \
#             --cmd "$decode_cmd" data/lang_test_{tgsmall,tglarge} \
#             data/$test exp/tri4b/decode_{tgsmall,tglarge}_$test
#            steps/lmrescore_const_arpa.sh \
#             --cmd "$decode_cmd" data/lang_test_{tgsmall,fglarge} \
#             data/$test exp/tri4b/decode_{tgsmall,fglarge}_$test
#        done
#    )&
# fi

# if [ $stage -eq 14 ] && false; then
#    # This stage is for nnet2 training on 100 hours; we're commenting it out
#    # as it's deprecated.
#    # align train_clean_100 using the tri4b model
#    steps/align_fmllr.sh --nj 30 --cmd "$train_cmd" \
#        data/train_clean_100 data/lang exp/tri4b exp/tri4b_ali_clean_100

#    # This nnet2 training script is deprecated.
#    local/nnet2/run_5a_clean_100.sh
# fi

# if [ $stage -eq 15 ]; then
#    local/download_and_untar.sh $data $data_url train-clean-360

#    # now add the "clean-360" subset to the mix ...
#    local/data_prep.sh \
#        $data/LibriSpeech/train-clean-360 data/train_clean_360
#    steps/make_mfcc.sh --cmd "$train_cmd" --nj 40 data/train_clean_360 \
#                                 exp/make_mfcc/train_clean_360 $mfccdir
#    steps/compute_cmvn_stats.sh \
#        data/train_clean_360 exp/make_mfcc/train_clean_360 $mfccdir

#    # ... and then combine the two sets into a 460 hour one
#    utils/combine_data.sh \
#        data/train_clean_460 data/train_clean_100 data/train_clean_360
# fi

# if [ $stage -eq 16 ]; then
#    # align the new, combined set, using the tri4b model
#    steps/align_fmllr.sh --nj 40 --cmd "$train_cmd" \
#                                    data/train_clean_460 data/lang exp/tri4b exp/tri4b_ali_clean_460

#    # create a larger SAT model, trained on the 460 hours of data.
#    steps/train_sat.sh    --cmd "$train_cmd" 5000 100000 \
#                                    data/train_clean_460 data/lang exp/tri4b_ali_clean_460 exp/tri5b

#    # decode using the tri5b model
#    (
#        utils/mkgraph.sh data/lang_test_tgsmall \
#                                 exp/tri5b exp/tri5b/graph_tgsmall
#        for test in test_clean test_other dev_clean dev_other; do
#            steps/decode_fmllr.sh --nj 20 --cmd "$decode_cmd" \
#                                            exp/tri5b/graph_tgsmall data/$test \
#                                            exp/tri5b/decode_tgsmall_$test
#            steps/lmrescore.sh --cmd "$decode_cmd" data/lang_test_{tgsmall,tgmed} \
#                                        data/$test exp/tri5b/decode_{tgsmall,tgmed}_$test
#            steps/lmrescore_const_arpa.sh \
#             --cmd "$decode_cmd" data/lang_test_{tgsmall,tglarge} \
#             data/$test exp/tri5b/decode_{tgsmall,tglarge}_$test
#            steps/lmrescore_const_arpa.sh \
#             --cmd "$decode_cmd" data/lang_test_{tgsmall,fglarge} \
#             data/$test exp/tri5b/decode_{tgsmall,fglarge}_$test
#        done
#    )&
# fi


# # The following command trains an nnet3 model on the 460 hour setup.    This
# # is deprecated now.
# ## train a NN model on the 460 hour set
# #local/nnet2/run_6a_clean_460.sh

# if [ $stage -eq 17 ]; then
#    # prepare the remaining 500 hours of data
#    local/download_and_untar.sh $data $data_url train-other-500

#    # prepare the 500 hour subset.
#    local/data_prep.sh \
#        $data/LibriSpeech/train-other-500 data/train_other_500
#    steps/make_mfcc.sh --cmd "$train_cmd" --nj 40 data/train_other_500 \
#                                 exp/make_mfcc/train_other_500 $mfccdir
#    steps/compute_cmvn_stats.sh \
#        data/train_other_500 exp/make_mfcc/train_other_500 $mfccdir

#    # combine all the data
#    utils/combine_data.sh \
#        data/train_960 data/train_clean_460 data/train_other_500
# fi

# if [ $stage -eq 18 ]; then
#    steps/align_fmllr.sh --nj 40 --cmd "$train_cmd" \
#                                    data/train_960 data/lang exp/tri5b exp/tri5b_ali_960

#    # train a SAT model on the 960 hour mixed data.    Use the train_quick.sh script
#    # as it is faster.
#    steps/train_quick.sh --cmd "$train_cmd" \
#                                    7000 150000 data/train_960 data/lang exp/tri5b_ali_960 exp/tri6b

#    # decode using the tri6b model
#    (
#        utils/mkgraph.sh data/lang_test_tgsmall \
#                                 exp/tri6b exp/tri6b/graph_tgsmall
#        for test in test_clean test_other dev_clean dev_other; do
#            steps/decode_fmllr.sh --nj 20 --cmd "$decode_cmd" \
#                                            exp/tri6b/graph_tgsmall data/$test exp/tri6b/decode_tgsmall_$test
#            steps/lmrescore.sh --cmd "$decode_cmd" data/lang_test_{tgsmall,tgmed} \
#                                        data/$test exp/tri6b/decode_{tgsmall,tgmed}_$test
#            steps/lmrescore_const_arpa.sh \
#             --cmd "$decode_cmd" data/lang_test_{tgsmall,tglarge} \
#             data/$test exp/tri6b/decode_{tgsmall,tglarge}_$test
#            steps/lmrescore_const_arpa.sh \
#             --cmd "$decode_cmd" data/lang_test_{tgsmall,fglarge} \
#             data/$test exp/tri6b/decode_{tgsmall,fglarge}_$test
#        done
#    )&
# fi


# if [ $stage -eq 19 ]; then
#    # this does some data-cleaning. The cleaned data should be useful when we add
#    # the neural net and chain systems.    (although actually it was pretty clean already.)
#    local/run_cleanup_segmentation.sh
# fi

# # steps/cleanup/debug_lexicon.sh --remove-stress true    --nj 200 --cmd "$train_cmd" data/train_clean_100 \
# #        data/lang exp/tri6b data/local/dict/lexicon.txt exp/debug_lexicon_100h

# # #Perform rescoring of tri6b be means of faster-rnnlm
# # #Attention: with default settings requires 4 GB of memory per rescoring job, so commenting this out by default
# # wait && local/run_rnnlm.sh \
# #        --rnnlm-ver "faster-rnnlm" \
# #        --rnnlm-options "-hidden 150 -direct 1000 -direct-order 5" \
# #        --rnnlm-tag "h150-me5-1000" $data data/local/lm

# # #Perform rescoring of tri6b be means of faster-rnnlm using Noise contrastive estimation
# # #Note, that could be extremely slow without CUDA
# # #We use smaller direct layer size so that it could be stored in GPU memory (~2Gb)
# # #Suprisingly, bottleneck here is validation rather then learning
# # #Therefore you can use smaller validation dataset to speed up training
# # wait && local/run_rnnlm.sh \
# #        --rnnlm-ver "faster-rnnlm" \
# #        --rnnlm-options "-hidden 150 -direct 400 -direct-order 3 --nce 20" \
# #        --rnnlm-tag "h150-me3-400-nce20" $data data/local/lm


# if [ $stage -eq 20 ]; then
#    # train and test nnet3 tdnn models on the entire data with data-cleaning.
#    local/chain/run_tdnn.sh # set "--stage 11" if you have already run local/nnet3/run_tdnn.sh
# fi

# # The nnet3 TDNN recipe:
# # local/nnet3/run_tdnn.sh # set "--stage 11" if you have already run local/chain/run_tdnn.sh

# # # train models on cleaned-up data
# # # we've found that this isn't helpful-- see the comments in local/run_data_cleaning.sh
# # local/run_data_cleaning.sh

# # # The following is the current online-nnet2 recipe, with "multi-splice".
# # local/online/run_nnet2_ms.sh

# # # The following is the discriminative-training continuation of the above.
# # local/online/run_nnet2_ms_disc.sh

# # ## The following is an older version of the online-nnet2 recipe, without "multi-splice".    It's faster
# # ## to train but slightly worse.
# # # local/online/run_nnet2.sh

# Wait for decodings in the background
wait
