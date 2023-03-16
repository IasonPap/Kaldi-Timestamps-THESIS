65 #!/bin/bash


# Set this to somewhere where you want to put your data, or where
# someone else has already put it.  You'll want to change this
# if you're not on the CLSP grid.
PATH_TO_YOUR_DATA_FOLDER=/media/datadisk/greg/Jason # CHANGE THIS
data=$PATH_TO_YOUR_DATA_FOLDER/librispeech_data

# base url for downloads.
data_url=www.openslr.org/resources/12
lm_url=www.openslr.org/resources/11
mfccdir=mfcc
stage=$1
##USEFUL_TIP: You can increase the number of threads on the decode.sh. So the job can done quicker
NumThreads=15 
train=false
timestamps=false

. ./cmd.sh
. ./path.sh
. ./utils/parse_options.sh

# you might not want to do this for interactive shells.
set -e


if [ $stage -eq
 1 ]; then
  # download the data.  Note: we're using the 100 hour setup for
  # now; later in the script we'll download more and use it to train neural
  # nets.
  for part in dev-other test-other train-clean-360; do  #  dev-clean test-clean train-clean-100
    local/download_and_untar.sh $data $data_url $part
  done


  # download the LM resources
  #local/download_lm.sh $lm_url data/local/lm
fi

if [ $stage -eq 2 ]; then
  # format the data as Kaldi data directories (extra_datasets dev-other and test-other)
  for part in dev-other test-other; do #dev-clean test-clean train-clean-100 
    # use underscore-separated names in data directories.
    local/data_prep.sh $data/$part data/$(echo $part | sed s/-/_/g)
  done
fi


if [ $stage -eq 3 ]; then #modified 10-3-2021
  # creating and formating the language model
  # dict_no_extra_phones has the extra Silence_phone 'CLAP'. 
  # You can remove it from the lexicon to experiment with results
  utils/prepare_lang.sh data/local/dict_no_extra_phones \
   "<UNK>" data/local/lang_tmp_no_extra_phones data/lang_no_extra_phones

  local/format_lms.sh --src-dir data/lang_no_extra_phones data/local/lm

#   # creating the neccessary files for LM with increased silence propability 0.65
#   utils/prepare_lang.sh --sil-prob 0.65 data/local/dict_nosp \
#    "<UNK>" data/local/lang_tmp_nosp data/lang_nosp_65silprob

# local/format_lms.sh --src-dir data/lang_nosp_65silprob data/local/lm
fi

## Skip this since we don't create a Language Model (aka G.fst)
# if [ $stage -eq 4 ]; then #modified 10-3-2021
 
#   # Create ConstArpaLm format language model for full 3-gram and 4-gram LMs
#   utils/build_const_arpa_lm.sh data/local/lm/lm_tglarge.arpa.gz \
#     data/lang_no_extra_phones_new data/lang_no_extra_phones_test_tglarge
  
#   ## we haven't downloaded the 4gram_large, that's why we ignore this
#   # utils/build_const_arpa_lm.sh data/local/lm/lm_fglarge.arpa.gz \
#   #   data/lang_no_exta_phones data/lang_no_extra_phones_test_fglarge

# fi

## skip this if you training the models localy on your own PC
# if [ $stage -eq 5 ]; then
#   # spread the mfccs over various machines, as this data-set is quite large.
#   if [[  $(hostname -f) ==  *.clsp.jhu.edu ]]; then
#     mfcc=$(basename mfccdir) # in case was absolute pathname (unlikely), get basename.
#     utils/create_split_dir.pl /export/b{02,11,12,13}/$USER/kaldi-data/egs/librispeech/s5/$mfcc/storage \
#      $mfccdir/storage
#   fi
# fi

# Creating the MFCC and CMVN features
if [ $stage -eq 6 ]; then
  for part in dev_clean test_clean train_clean_100 test_other dev_other; do
    steps/make_mfcc.sh --cmd "$train_cmd" --nj 10 data/$part exp/make_mfcc/$part $mfccdir
    steps/compute_cmvn_stats.sh data/$part exp/make_mfcc/$part $mfccdir
  done
fi

if [ $stage -eq 7 ]; then
  # Make some small data subsets for early system-build stages.  Note, there are 29k
  # utterances in the train_clean_100 directory which has 100 hours of data.
  # For the monophone stages we select the shortest utterances, which should make it
  # easier to align the data from a flat start.

  utils/subset_data_dir.sh --shortest data/train_clean_100 2000 data/train_2kshort
  utils/subset_data_dir.sh data/train_clean_100 5000 data/train_5k
  utils/subset_data_dir.sh data/train_clean_100 10000 data/train_10k
fi

if [ $stage -eq 8 ]; then #modified 12-3-2021
  log_file=exp/mono-out.log
  echo `date` >> $log_file
  # train a monophone system
  if [ $train ]; then
  ## trains a monophone model on the train_2kshort set (default num_iters=40)
  #original: num_iters=40 totgauss=2000 (github: num_iters=40 totgauss=1000) DONE: optimal setting num_iters=40 totgauss=2000
 	steps/train_mono.sh --boost-silence 1.25 --num_iters 40 \
                      --totgauss 2000 --nj 10 --cmd "run.pl" \
                      data/train_2kshort data/lang_no_extra_phones exp/mono-2_new >> $log_file
    # steps/train_mono.sh --boost-silence 1.25 --nj 20 --cmd "run.pl" \     ## train a monophone model with the new 65silprob lm
    #                   data/train_2kshort data/lang_nosp_65silprob exp/mono                  
  fi
  
  echo "FINISHED with mono at:" `date` >> $log_file

fi

if [ $stage -le 9 ]; then #moidifed 10-3-2021
  log_file=exp/tri1_out.log
  
  echo -e "\n Aligning using the monophone model mono-2 \n" `date` >> $log_file
  steps/align_si.sh --boost-silence 1.25 --nj 10 --cmd "$train_cmd" \
                    data/train_5k data/lang_no_extra_phones exp/mono-2 exp/mono_ali_5k >> $log_file
  
  echo -e "\n Training triphone with deltas \n" `date` >> $log_file
  # train a first delta + delta-delta triphone system on a subset of 5000 utterances  # num_iters = 35 default
  # original: numleaves=2000 totgauss=10000 (same as github) DONE: for results look at tri1_out.log
  steps/train_deltas.sh --boost-silence 1.25 --cmd "$train_cmd" \
                        2000 50000 data/train_5k data/lang_no_extra_phones exp/mono_ali_5k exp/tri1 >> $log_file
  
  echo "FINISHED with tri1 at:" `date` >> $log_file
fi

if [ $stage -le 10 ]; then
  log_file=exp/tri2b_out.log
  echo -e "\n aligning with tri1" `date` >> $log_file
  steps/align_si.sh --nj 10 --cmd "$train_cmd" \
                    data/train_10k data/lang_no_extra_phones exp/tri1 exp/tri1_ali_10k >> $log_file


  # train an LDA+MLLT system.  # num_iters = 35 default
  #original: numleaves=5000 totgauss=50000 (from github: numleaves=2500 totgauss=15000) TODO: binary search to find optimal
  #original: left-context=3 right-context=3 (same as github) TODO: binary search to find optimal
  
  echo -e "\n" >> $log_file
	echo "training triphone with LDA+MLLT" `date` >> $log_file
  #best configuration
	steps/train_lda_mllt.sh --cmd "$train_cmd" \
                          --splice-opts "--left-context=10 --right-context=10" 4370 75000 \
                          data/train_10k data/lang_no_extra_phones exp/tri1_ali_10k exp/tri2b >> $log_file
	
	

  ##uncomment the 2 lines below to make the graph for the model.
  # utils/mkgraph.sh data/lang_no_extra_phones_test_tgsmall \ 
  #                  exp/tri2b exp/tri2b/graph_no_extra_phones_tgsmall  >> $log_file
    
  echo "FINISHED with tri2b at:" `date` >> $log_file
fi

if [ $stage -le 11 ]; then
  log_file=exp/tri3b_out.log
 
  # Align a 10k utts subset using the tri2b model
  echo -e "\n Aligning with tri2b" `date` >> $log_file
  steps/align_si.sh  --nj 10 --cmd "$train_cmd" --use-graphs true --beam 30 --retry_beam 100 \
                     data/train_10k data/lang_no_extra_phones exp/tri2b exp/tri2b_ali_10k >> $log_file
  

  #typing the time when the training step started
  
	echo -e "Training with LDA + MLLT + SAT: " `date` >> $log_file  
  # Train tri3b, which is LDA+MLLT+SAT on 10k utts # num_iters = 35 default
  #original: numleaves=2500 totgauss=15000 (same as github) TODO: binary search to find optimal
  steps/train_sat.sh --cmd "$train_cmd" 10000 200000 \
                    data/train_10k data/lang_no_extra_phones exp/tri2b_ali_10k exp/tri3b >> $log_file
  
  # #uncomment the 2 lines below to make the graph for the model.
  # echo -e "\n Making graph with tri3b" `date` >> $log_file  
  # utils/mkgraph.sh data/lang_no_extra_phones_test_tgsmall \
  #                    exp/tri3b exp/tri3b/graph_no_extra_phones_tgsmall
  
  echo "FINISHED with tri3b at:" `date` >> $log_file
fi

if [ $stage -le 12 ]; then
  log_file=exp/tri4b_out.log
#   scale_options="--transition-scale=1.0 --acoustic-scale=0.6 --self-loop-scale=0.8"
  
  echo -e "\n aligning with tri3b on 100h train_clean" `date` >> $log_file
  # align the entire train_clean_100 subset using the tri3b model
  steps/align_fmllr.sh --nj 20 --cmd "$train_cmd" \
    					data/train_clean_100 data/lang_no_extra_phones \
    					exp/tri3b exp/tri3b_ali_clean_100 >> $log_file
  # echo "Finished with alignment at:" `date` >> exp/tri3b_out.log
  echo -e "\n Training LDA + MLLT + SAT on 100h "`date` >> exp/tri4b_out.log
  # train another LDA+MLLT+SAT system on the entire 100 hour subset  # num_iters = 35 default
  #original: numleaves=5000 totgauss=50000 (from github: numleaves=4200 totgauss=40000) TODO: binary search to find optimal
  steps/train_sat.sh  --cmd "$train_cmd" 10000 200000 \
                      data/train_clean_100 data/lang_no_extra_phones \
                      exp/tri3b_ali_clean_100 exp/tri4b >> $log_file
  
    # #uncomment the lines below to make the graph for the model.
    # echo -e "\n Making graph with tri3b" `date` >> $log_file  
    # utils/mkgraph.sh data/lang_no_extra_phones_test_tgsmall \
    #                  exp/tri4b exp/tri4b/graph_no_extra_phones_tgsmall >> $log_file
  
  echo "Finished at:" `date` >> exp/tri4b_out.log
fi

if [ $stage -le 13 ]; then
  log_file=exp/tri4b_out.log
  # Now we compute the pronunciation and silence probabilities from training data,
  # and re-create the lang directory.
  echo -e "\nRe-Creating the 'lang' directory" >> $log_file
  echo `date` >> $log_file
  steps/get_prons.sh --cmd "$train_cmd" \
                     data/train_clean_100 data/lang_no_extra_phones exp/tri4b >> $log_file
  echo `date` >> $log_file
  utils/dict_dir_add_pronprobs.sh --max-normalize true \
                                  data/local/dict_no_extra_phones \
                                  exp/tri4b/pron_counts_nowb.txt exp/tri4b/sil_counts_nowb.txt \
                                  exp/tri4b/pron_bigram_counts_nowb.txt data/local/no_extra_phones_prons >> $log_file
  echo `date` >> $log_file
  utils/prepare_lang.sh data/local/dict_no_extra_phones_new \
                        "<UNK>" data/local/lang_tmp_no_extra_phones data/lang_no_extra_phones_updated >> $log_file
  # echo `date` >> $log_file
  # local/format_lms.sh --src-dir data/lang_no_extra_phones_new data/local/lm >> $log_file
  # echo `date` >> $log_file
  # utils/build_const_arpa_lm.sh \
  #   data/local/lm/lm_tglarge.arpa.gz data/lang_no_extra_phones_new data/lang_no_extra_phones_new_test_tglarge >> $log_file
  
  # # utils/build_const_arpa_lm.sh \
  # #   data/local/lm/lm_fglarge.arpa.gz data/lang data/lang_test_fglarge


    # #uncomment the 2 lines below to make the graph for the model.
    # echo "Making graph " `date` >> exp/tri4b_out.log
    # utils/mkgraph.sh \
    #   data/lang_no_extra_phones_test_tgsmall exp/tri4b exp/tri4b/graph_no_extra_phones_tgsmall
    
  echo -e `date` "\nFINISHED with re-creating the lang directory: \nlook at lang_no_extra_phones_new for the updated"

  # If you want you can retrain the models until tri4b with the new Language Model 
  # lang_no_extra_phones_new
  # just change the name of the LM in the stages above.
  # DON'T FORGET to change the output directories so you can compare the models with the old and new LM.

fi

# Below are the next stages to build a DNN ASR model 
# from the original run.sh file from the Librispeech recipe

# if [ $stage -eq 14 ] ; then
  
#   # align train_clean_100 using the tri4b model
#   steps/align_fmllr.sh --nj 30 --cmd "$train_cmd" \
#     data/train_clean_100 data/lang-pretrained exp/tri4b exp/tri4b_ali_clean_100

# # This stage is for nnet2 training on 100 hours; we're commenting it out
# # as it's deprecated.
# #   # This nnet2 training script is deprecated.
# #   local/nnet2/run_5a_clean_100.sh
# fi

# if [ $stage -eq 15 ]; then
#   local/download_and_untar.sh $data $data_url train-clean-360

#   # now add the "clean-360" subset to the mix ...
#   local/data_prep.sh \
#     $data/LibriSpeech/train-clean-360 data/train_clean_360
#   steps/make_mfcc.sh --cmd "$train_cmd" --nj 40 data/train_clean_360 \
#                      exp/make_mfcc/train_clean_360 $mfccdir
#   steps/compute_cmvn_stats.sh \
#     data/train_clean_360 exp/make_mfcc/train_clean_360 $mfccdir

#   # ... and then combine the two sets into a 460 hour one
#   utils/combine_data.sh \
#     data/train_clean_460 data/train_clean_100 data/train_clean_360
# fi

# if [ $stage -eq 16 ]; then
#   # align the new, combined set, using the tri4b model
#   steps/align_fmllr.sh --nj 40 --cmd "$train_cmd" \
#                        data/train_clean_460 data/lang exp/tri4b exp/tri4b_ali_clean_460

#   # create a larger SAT model, trained on the 460 hours of data.
#   steps/train_sat.sh  --cmd "$train_cmd" 5000 100000 \
#                       data/train_clean_460 data/lang exp/tri4b_ali_clean_460 exp/tri5b

#   # decode using the tri5b model
#   (
#     utils/mkgraph.sh data/lang_test_tgsmall \
#                      exp/tri5b exp/tri5b/graph_tgsmall
#     for test in test_clean dev_clean; do ##test_other dev_other
#       steps/decode_fmllr.sh --nj 20 --cmd "$decode_cmd" --num-threads $NumThreads \
#                             exp/tri5b/graph_tgsmall data/$test \
#                             exp/tri5b/decode_tgsmall_$test
#       steps/lmrescore.sh --cmd "$decode_cmd" data/lang_test_{tgsmall,tgmed} \
#                          data/$test exp/tri5b/decode_{tgsmall,tgmed}_$test
#       steps/lmrescore_const_arpa.sh \
#         --cmd "$decode_cmd" data/lang_test_{tgsmall,tglarge} \
#         data/$test exp/tri5b/decode_{tgsmall,tglarge}_$test
#       steps/lmrescore_const_arpa.sh \
#         --cmd "$decode_cmd" data/lang_test_{tgsmall,fglarge} \
#         data/$test exp/tri5b/decode_{tgsmall,fglarge}_$test
#     done
#   )&
# fi


# # The following command trains an nnet3 model on the 460 hour setup.  This
# # is deprecated now.
# ## train a NN model on the 460 hour set
# #local/nnet2/run_6a_clean_460.sh

# if [ $stage -eq 17 ]; then
#   # prepare the remaining 500 hours of data
#   local/download_and_untar.sh $data $data_url train-other-500

#   # prepare the 500 hour subset.
#   local/data_prep.sh \
#     $data/LibriSpeech/train-other-500 data/train_other_500
#   steps/make_mfcc.sh --cmd "$train_cmd" --nj 40 data/train_other_500 \
#                      exp/make_mfcc/train_other_500 $mfccdir
#   steps/compute_cmvn_stats.sh \
#     data/train_other_500 exp/make_mfcc/train_other_500 $mfccdir

#   # combine all the data
#   utils/combine_data.sh \
#     data/train_960 data/train_clean_460 data/train_other_500
# fi

# if [ $stage -eq 18 ]; then
#   steps/align_fmllr.sh --nj 40 --cmd "$train_cmd" \
#                        data/train_960 data/lang exp/tri5b exp/tri5b_ali_960

#   # train a SAT model on the 960 hour mixed data.  Use the train_quick.sh script
#   # as it is faster.
#   steps/train_quick.sh --cmd "$train_cmd" \
#                        7000 150000 data/train_960 data/lang exp/tri5b_ali_960 exp/tri6b

#   # decode using the tri6b model
#   (
#     utils/mkgraph.sh data/lang_test_tgsmall \
#                      exp/tri6b exp/tri6b/graph_tgsmall
#     for test in test_clean dev_clean; do ##test_other dev_other
#       steps/decode_fmllr.sh --nj 20 --cmd "$decode_cmd" --num-threads $NumThreads \
#                             exp/tri6b/graph_tgsmall data/$test exp/tri6b/decode_tgsmall_$test
#       steps/lmrescore.sh --cmd "$decode_cmd" data/lang_test_{tgsmall,tgmed} \
#                          data/$test exp/tri6b/decode_{tgsmall,tgmed}_$test
#       steps/lmrescore_const_arpa.sh \
#         --cmd "$decode_cmd" data/lang_test_{tgsmall,tglarge} \
#         data/$test exp/tri6b/decode_{tgsmall,tglarge}_$test
#       steps/lmrescore_const_arpa.sh \
#         --cmd "$decode_cmd" data/lang_test_{tgsmall,fglarge} \
#         data/$test exp/tri6b/decode_{tgsmall,fglarge}_$test
#     done
#   )&
# fi


# if [ $stage -eq 19 ]; then
#   # this does some data-cleaning. The cleaned data should be useful when we add
#   # the neural net and chain systems.  (although actually it was pretty clean already.)
#   local/run_cleanup_segmentation.sh
# fi

# # steps/cleanup/debug_lexicon.sh --remove-stress true  --nj 200 --cmd "$train_cmd" data/train_clean_100 \
# #    data/lang exp/tri6b data/local/dict/lexicon.txt exp/debug_lexicon_100h

# # #Perform rescoring of tri6b be means of faster-rnnlm
# # #Attention: with default settings requires 4 GB of memory per rescoring job, so commenting this out by default
# # wait && local/run_rnnlm.sh \
# #     --rnnlm-ver "faster-rnnlm" \
# #     --rnnlm-options "-hidden 150 -direct 1000 -direct-order 5" \
# #     --rnnlm-tag "h150-me5-1000" $data data/local/lm

# # #Perform rescoring of tri6b be means of faster-rnnlm using Noise contrastive estimation
# # #Note, that could be extremely slow without CUDA
# # #We use smaller direct layer size so that it could be stored in GPU memory (~2Gb)
# # #Suprisingly, bottleneck here is validation rather then learning
# # #Therefore you can use smaller validation dataset to speed up training
# # wait && local/run_rnnlm.sh \
# #     --rnnlm-ver "faster-rnnlm" \
# #     --rnnlm-options "-hidden 150 -direct 400 -direct-order 3 --nce 20" \
# #     --rnnlm-tag "h150-me3-400-nce20" $data data/local/lm


# if [ $stage -eq 20 ]; then
#   # train and test nnet3 tdnn models on the entire data with data-cleaning.
#   local/chain/run_tdnn.sh # set "--stage 11" if you have already run local/nnet3/run_tdnn.sh
# fi

# # The nnet3 TDNN recipe:
# # local/nnet3/run_tdnn.sh # set "--stage 11" if you have already run local/chain/run_tdnn.sh

# # # train models on cleaned-up data
# # # we've found that this isn't helpful-- see the comments in local/run_data_cleaning.sh
# # local/run_data_cleaning.shdamp-edu@smule.com

# # # The following is the curdamp-edu@smule.comi-splice".
# # local/online/run_nnet2_ms.damp-edu@smule.com

# # # The following is the discriminative-training continuation of the above.
# # local/online/run_nnet2_ms_disc.sh

# # ## The following is an older version of the online-nnet2 recipe, without "multi-splice".  It's faster
# # ## to train but slightly worse.
# # # local/online/run_nnet2.sh

# # Wait for decodings in the background
# wait
