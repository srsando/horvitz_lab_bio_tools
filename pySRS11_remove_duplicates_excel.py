# 11/29/2021: This script a given excel file, take all the names out of a given column,
# and then deletes the duplicates and outputs a new list of the remaining entries.

import pandas as pd
import os

# Define file and location of column in file:
path = 'E:\\python\\python workspace'
file_name = 'significant hits w duplicates.xlsx'
file_and_path = os.path.join(path, file_name)

column_id = "A"

# Open the desired column of the file:
genes_with_duplicates_df = pd.read_excel(file_and_path, usecols="%s" % column_id)

# Delete the duplicates:
dup_free_list = genes_with_duplicates_df.drop_duplicates()

# Save as xlsx:
file_and_path = os.path.join(path, 'list.xlsx')

dup_free_list.to_excel(file_and_path)
