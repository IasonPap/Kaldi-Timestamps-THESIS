import os, sys
import pandas as pd
from pandas.core.indexes.numeric import IntegerIndex

models = ["speech", "speech+sing", "sing_only"]
total_df = pd.DataFrame(columns=['Average absolute error',
								"Median absolute error",
								"Percentage of correct segments",
								"Percentage of correct onsets with tolerance"])

for model in models:
	
	# REPLACE the following line with the path to the file of your results.
	results_csv_dir = os.path.join("EVAL_RESULTS","eval_results_"+model)

	for csv_file in os.listdir(results_csv_dir):
		# replace "Results_new" with the suffix for you results
		if "Results_new" in csv_file: 
			results_csv_path = csv_file
	
	results_csv_path = os.path.join(results_csv_dir,results_csv_path)

	if os.path.isfile(results_csv_path):
		results_df = pd.read_csv(results_csv_path)
	else: # for safety
		print("There is no file named " + results_csv_path)
		sys.exit(0)

	for utt in ["ADIZ-01","SAMF-01"]: # dropping these two utterances because my 
		index_to_drop = results_df.index[results_df['Track'] == utt]
		# print(index_to_drop.tolist()[0])
		results_df = results_df.drop(index_to_drop)
		# print(results_df)
	
	# print(results_df.mean().to_numpy())
	mean, std, minv, *perc25_50_75, maxv = results_df.describe().iloc[1:].to_numpy()
	

	# writes the mean, standard deviation, min value and max value of the results of each model to a csv
	total_df.loc[f"{model}_mean"] = mean
	total_df.loc[f"{model}_std"] = std
	total_df.loc[f"{model}_min-value"] = minv
	total_df.loc[f"{model}_max-value"] = maxv

	total_df.to_csv(os.path.join("EVAL_RESULTS","Statistics_All_models_All_metrics.csv"))

	print("\n"+r"######## " + model.upper() + r" ########" " Number of utterances: " + str(results_df.shape[0]))
	print(f"The Mean of the metrics is:" )
	print(results_df.mean())
	print(f"\nThe Standard deviation is:")
	print(results_df.std())