# When copying lists of genes off tables and such from the internet, etc, it can be a pain to clean them up into a list
# This program, a practice exercise for me, cleans that sort of thing up.
# Copy all the gene-containing text and save it as a file, then run this on it.

# This script will search for genes by looking for "a-#' or "A__#.#" structures that are indicative
# of C. elegans genes and cosmids. Then, it outputs a list of all genes it found.

import os
import pandas as pd

# Open the text file
path = 'E:\\python\\python workspace'
input_filename = 'gene_list.txt'  # The file you're reading from
output_filename = 'mec_genes.xlsx'  # Name of the output

filenname_w_path = os.path.join(path, input_filename)

with open(filenname_w_path, 'r') as f:
    text = f.read()

# Remove all the extra spaces/formatting:
    string = text.split()

# Now turn into a list and select elements that contain a '-' or '.'
    text_list = list(string)
    output_list = []
    hyphen = '-'
    period = '.'
    for item in text_list:
        if hyphen in item or period in item:
            output_list.append(item)

print(output_list)

# Now save the list as an excel file:

output_df = pd.Series(output_list)

output_fn_w_path = os.path.join(path, output_filename)

output_df.to_excel(output_fn_w_path, 'xlsxwriter', index=False)
