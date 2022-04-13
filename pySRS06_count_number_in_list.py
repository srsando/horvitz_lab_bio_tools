# 2021-10-05 - This script originated as "count_gene_in_list"
# On 2021-10-07 I split off this version to count the number of times certain expression values appeared.

import os
import glob
import pandas as pd


path = "E:\\python\\python workspace"
extension = 'xlsx'

# Make a list of all the excel documents in the path:
os.chdir(path)
xls_list = glob.glob('*.{}'.format(extension))

# Create dataFrames for lists of hits and summary stats:

# Look at everything in the list and process anything that ends with "hits.xlsx":
print(len(xls_list))
for i in range(0, len(xls_list)):
    fn_decomposition = xls_list[i].split('_')  # Makes a list out of all parts of the filename separated by "_"
    print(fn_decomposition[2])
    if fn_decomposition[2] == "hits.xlsx":  # Checks if the last part of the filename is hits.xlsx

        # Make dataFrame and import excel list of hits to it:
        anomalies = pd.read_excel(xls_list[i], sheet_name="individual hits", usecols="D")

        # Count the number of times each log2FC value appears for each gene in the "hits" dataframe:
        logFC_value = anomalies["egl-9"].value_counts()
        logFC_value_df = pd.DataFrame(logFC_value)  # Turn the results into a new dataframe
        logFC_value_df.rename(columns={'log2FC value': 'appearances as anomaly'}, inplace=True)

        # For each file, save the results of the analysis:
        fn_decomposition = xls_list[i].split('_')
        fn_final = fn_decomposition[0] + '_' + fn_decomposition[1] + '_' + 'anomalies_logFC_value.xlsx'
        logFC_value_df.to_excel(fn_final)
