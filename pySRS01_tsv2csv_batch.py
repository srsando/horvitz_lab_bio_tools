# This program first finds all the tsv files in a folder and saves them as csv files.

import glob
import os
import pandas as pd

# path = input("Input file path: ")  # Request path of target folder
path = "my_path"  # Specify the path of the folder to operate on

# Make a list of all tsv files in the directory:
extension = 'tsv'
os.chdir(path)
tsv_list = glob.glob('*.{}'.format(extension))

# Go through the list:
for i in range(0, len(tsv_list)):
    # Get the tsv file name, remove the tsv, and put it back in the list
    tsv_file_name = tsv_list[i]

    # Open the tsv as a csv.
    csv_table = pd.read_table(tsv_file_name, sep='\t')

    # Now save that csv/dataframe as an xls file:
    name_stem = tsv_file_name.rsplit('.', 1)[0]  # Remove the file extension for we can save as xlx
    new_name_xls = name_stem + '.xls'
    csv_table.to_excel(new_name_xls)
