# The code for my Undergraduate Thesis

This a repository containing the files as well as instructions to reproduce the results from my undergraduate thesis "[Processing of music signals for the automatic lyrics-to-audio alignment through training of acoustic models using the Kaldi toolkit](https://drive.google.com/file/d/16PppY9zV_qT3lcRtUNAxycq1r3aaYSqk/view?usp=sharing)".

**Pro Tip**: the files have comments in them explaining how the code works. Refer to them if you have any errors while trying to execute any of the files. 

For any question, note or report of a problem about the repo please contact me at: [jpapadopoulos99@gmail.com](jpapadopoulos99@gmail.com).

## Requirements

In order to be able to start training the models you will need:
- **A working Kaldi build**. You can find instruction on how to download and install Kaldi [here](https://kaldi-asr.org/doc/install.html)
- **The Librispeech dataset**. The ![run.sh](egs/my_librispeech/s5/run.sh) (check below) will download the files (dev-clean, dev-other, test-clean, test-other, train-clean-100) from [here](https://www.openslr.org/12/)
- **The 7h subset of DAMPB dataset**. You can find it in this [google drive folder](https://drive.google.com/drive/folders/1--AX8PACKG1zzusrQnMszdvCD82uQ09r?usp=sharing). It contains 833 wav files with durations ~30sec of 146 songs. Size = 733MB
- **The NUS48 evaluation dataset**. You can download it from [here](https://drive.google.com/drive/folders/12pP9uUl0HTVANU3IPLnumTJiRjPtVUMx).
(Citation: 
Zhiyan Duan, Haotian Fang, Bo Li, Khe Chai Sim and Ye Wang. “The NUS Sung and Spoken Lyrics Corpus: A Quantitative Comparison of Singing and Speech“. Asia-Pacific Signal and Information Processing Association Annual Submit and Conference 2013 (APSIPA ASC 2013))
- **The code for evaluation**. The python script `eval.py` from [this repository](https://github.com/georgid/AlignmentEvaluation) is needed to be installed to produce the results based on the 4 metrics (*Average absolute error/deviation*, *Median absolute error/deviation*, *Percentage of correct segments*, *Percentage of correct estimates according to a tolerance window*). Note that the evaluation scripts depend on [mir_eval](https://github.com/craffel/mir_eval) repository.  

## Before You start training models
You'll need to go to the folder where you installed Kaldi. Go into the `egs/` folder and paste all the files from the `egs/` folder of this repository. This folder contains all the neccessary files so that you can train models with you installed Kaldi version. Execute the unix commands below with the correct paths:
```
cp -r path/to/Kaldi-Timestamps-THESIS/egs/ path/to/kaldi/egs/
cd path/to/kaldi/egs/my_librispeech
ln -s ../wsj/s5/steps .
ln -s ../wsj/s5/utils .
ln -s ../../src .
```

## Training the Librispeech Model
In order to train a triphone LDA+MLLT+SAT model you need to:
1. Input the folder where you want to download the librispeech audio files
    - You input the full path of your folder as a value in the variable "PATH_TO_YOUR_DATA_FOLDER" in the /egs/my_librispeech/run.sh file.
2. Run from the command line the ```/egs/my_librispeech/run.sh``` Bash file step by step with the command:
    ```
    egs/my_librispeech/run.sh <stage_number>
    ```
Execute the script step-by-step. Replace <stage_number> with *1, then 2, then 3, in order to prepare your training data* and then give the numbers from *6 to 12 one by one* to run the steps of the file so you can train a triphone model with LDA+MLLT+SAT transforms called ***tri4b***. 
It's better to run the steps one by one for debugging purposes and understanding better how it works.


Each step outputs a log file named '<model_name>_out.txt' in the ```exp/``` folder

## Training the Librispeech Model on Singing Voice Data (a.k.a Finalising the Hybrid Model)
In order to train a triphone LDA+MLLT+SAT model on singing voice data based on the speech-trained previous model you need to:
1. Have a trained speech model based on librispeech data (Previous Section)
2. Make sure that the *librispeech directory* in the start of the ```egs/DAMPB_150songs/run.sh``` file corresponds to the directory were you have your final librispeech model ***tri4b***.
3. Execute the stages 1 through 5 one by one in ```/egs/DAMPB_150songs/run.sh``` using the following command in the command line:
    ```
    egs/DAMPB_150songs/run.sh <stage_number>
    ```

All of the *hybrid model*'s files will be created in a folder named ```/egs/DAMPB_150songs/exp/tri5b_sing```.
## Training the Sing Model
In order to train a triphone LDA+MLLT+SAT model from only singing voice data you need to:
1. If you haven't trained the hybrid model. Run the Stages 1 and 2 of the ```/egs/DAMPB_150songs/run.sh``` file to create the mfcc and cmvn files, as well as populate the lexicon direcoty. If you already have trained the hybrid model you don't need to.
2. Run the Stages 6 through 9 one by one from the ```/egs/DAMPB_150songs/run.sh``` file. You can execute a stage by using the same command in the command line as above:
```
egs/DAMPB_150songs/run.sh <stage_number>
```
All of the *Sing Only Model*'s files will be created in a folder named ```/egs/DAMPB_150songs/exp/tri3_singOnly```.


## Producing the Word level Timestamps from the three Models on NUS48 dataset
In order to obtain the Timestamps from the three models you need to:
1. From the ```/egs/NUS48/run.sh``` run the stages 1 through 4 on by one to prepare the NUS48 data for Kaldi.
2. Run the **stage 5** from the same file, to create the word level timestamps for the *librispeech (tri4b)* model. The file containing the timestamps is ```/egs/NUS48/exp/tri4b_align/ctm_align```. 
3. Run the **stage 6** from the same file, to create the word level timestamps for the *hybrid speech+sing (tri5b_sing)* model. The file containing the timestamps is ```/egs/NUS48/exp/tri5b_sing_align/ctm_align```.
4. Run the **stage 7** from the same file, to create the word level timestamps for the *sing only (tri3_singOnly)* model. The file containing the timestamps is ```/egs/NUS48/exp/tri5b_sing_align/ctm_align```.

In order to proceed to the next step you'll need to copy all three ```ctm_align``` files containing the timestamps from the 3 different models to a common folder, ***with a proper suffix at the end to indicate the model that produced them***. In the end you should have three files like those in the folder `local-files/KaldiWordCTM_all48_utts`.

## Evaluating the models at the word boundaries
In order to evaluate the models at the word boundaries, three metrics are used:
1. **Average absolute error/deviation**: The absolute error measures the time displacement between the actual timestamp and its estimate at the beginning and the end of each lyrical unit. The error is then averaged over all individual errors. An error in absolute terms has the drawback that the perception of an error with the same duration can be different depending on the tempo of the song
2. **Percentage of correct segments**:  The perceptual dependence on tempo is mitigated by measuring the percentage of the total length of the segments, labeled correctly to the total duration of the song.
3. **Percentage of correct estimates according to a tolerance window**: A metric that takes into consideration that the onset displacements from ground truth below a certain threshold could be tolerated by human listeners. We use 0.3 seconds as the tolerance window.
~ *Reference*: [MIREX 2020](https://www.music-ir.org/mirex/wiki/2020:Lyrics_Transcription)

You'll need to run the `eval.py` script to obtain all three of the above metrics. You can install the repository including the `eval.py` from the [AlignmentEvaluation](https://github.com/georgid/AlignmentEvaluation) GitHub. Note that evaluation scripts depend on [mir_eval](https://github.com/craffel/mir_eval/), but the `mir_eval` dependency is included with the *AlignmentEvaluation*.

The syntax to run the `eval.py` is:

`python eval.py <file path of the reference word boundaries> <file path of the detected word boundaries> <tolerance (s)> <Output directory>`

About the parameters:
- The **reference word boundaries files** for each song of the NUS48 dataset are in the directory `/local-files/RefWordTrans_AllUtts/`.
- To create the **detected word boundaries files** for all three models you have to run the `local-files/scripts/post_process_ctm_words.py`, which will create a folder (you can setup the name) to save all the detected word boundaries for the three models in different folders.
- **tolerance** is the tolerance window in seconds that the detected word will still be considered correct relative with the reference. It's used for the **Percentage of correct estimates according to a tolerance window** metric.
- **Output direcoty** is the output path where the `.csv` file with the results will be created.

The way the `eval.py` is written you have to run it seperately for each model. 
So in the end you should have three folders, one for every model, with a `.csv` file in each folder. 
Something like in the folder `local-files/EVAL_RESULTS/`
Remember to name the output directory for each model differently so you don't erase your previous results

## Parsing the results
In order to parse the results from the `eval.py`, you'll need to run the script `local-files/scripts/parse_results.py`.
This script requires the path to the directory where the different folder for each model are. For the current folder tree should be correctly looking inside the `EVAL_RESULTS` folder. 
It creates a `.csv` file with all the useful statistcs (mean, standard deviation, min value, max value) for every metric and for each of the three models.

End you're done ! !
Godspeed !
