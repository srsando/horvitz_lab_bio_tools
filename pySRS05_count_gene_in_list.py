# 2021-10-05 - This script counts the number of times a given gene name appears in a list
# This script is derived from pySRS04_expression_mirror_detector

import os
import glob
import pandas as pd

path = "E:\\python\\python workspace"

# Make a list of all the excel documents in the path:
extension = 'xlsx'
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
        anomalies = pd.read_excel(xls_list[i], sheet_name="individual hits", usecols="C")

# Count the number of times each gene appears in the "hits" dataframe:
        gene_count = anomalies["gene"].value_counts()

        # Turn the results into a new dataframe
        gene_count_df = pd.DataFrame(gene_count)
        gene_count_df.rename(columns={'gene': 'appearances as anomaly'}, inplace=True)

# For each file, save the results of the analysis:
        fn_decomposition = xls_list[i].split('_')
        fn_final = fn_decomposition[0] + '_' + fn_decomposition[1] + '_' + 'anomalies_gene_count.xlsx'
        gene_count_df.to_excel(fn_final)
