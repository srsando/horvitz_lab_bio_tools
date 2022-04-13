# 10-13-2021: Used to convert a spreadsheet with rows (genes) and columns (UMIs)
# into a spreadsheet with rows (genes) and columns (UMIs in a given cluster)
# it uses the "tissue_Convert_UMI_Label.tsv" (e.g., "Intestine_Convert_UMI_Label.tsv") files
# given to us by the core facility.

# I'll use the "intestine" tissue as an example in the notes here:

# Using the intestine as an example, it will use
# "Intestine_Convert_UMI_Label.tsv" as a guide to open a set of columns in
# "Intestine_normalized_Gene_Count_per_Cell.tsv" that correspond to the only the UMIs that belong in a given cluster.

# This script would have been much more Pythonic if I'd have used pandas to simply filter the spreadsheets
# instead of looking line-by-line with a loop.

import pandas as pd
import os.path

# Parameters:
path = "E:/python/python workspace"  # Where to find the file
tissue = "Muscle"  # The tissue you're looking at (e.g., "Intestine")
#  The genotypes designations as given in "Intestine_Convert_UMI_Label.tsv"
genotype_labels = ['wtproj', 'egl9proj', 'egl9hif1proj']  # Used as part of a loop to make UMI lists for each genotype

# Open the list of UMI cluster assignments:

fn_UMI_labels = tissue + "_Convert_UMI_Label.tsv"  # Generate the expected filename of the UMI label spreadsheet
path_UMI_labels = os.path.join(path, fn_UMI_labels)  # Make path based on current folder and file name

# Open the "the "_Convert_UMI_label.tsv" file that has all the UMIs and their cluster designations:
UMI_cluster_labels = pd.read_csv(path_UMI_labels, sep='\t')

# Determine how many clusters you're working with:
cluster_ID_column = UMI_cluster_labels["cluster"]  # Grab the 'cluster' column
number_clusters = cluster_ID_column.max() + 1  # The number of clusters is equal to the highest cluster id + 1

# We'll need this info during the loop:
# Generate name of file that contains the normalized gene count per cell info:
fn_normalized_gene_count = tissue + '_normalized_Gene_Count_per_Cell.tsv'
# Make path based on current folder and file name:
path_normalized_gene_count = os.path.join(path, fn_normalized_gene_count)

# Go through each cluster and make a list of all UMIs that belong in that cluster
# according to "Intestine_Convert_UMI_Label.tsv".

# Use that list as the "usecols=" argument in "pd.read_csv" to open only those columns.
# Then, at the end, save each cluster to a new csv file:
for genotypes in range(0, (len(genotype_labels))):
    for cluster in range(0, number_clusters):  # Look at each cluster
        # First, filter the UMI_cluster_labels to make a dataFrame that shows only UMIs in our desired cluster:
        # Show only the current cluster:
        UMIs_filtered_by_cluster = UMI_cluster_labels[(UMI_cluster_labels['cluster'] == cluster)
                                                      & (UMI_cluster_labels['sample'] == genotype_labels[genotypes])]

        # Turn that set of UMIs into a list to be used as column titles:
        UMI_list = UMIs_filtered_by_cluster['cell'].values.tolist()
        gene_header = ['gene']  # We want the first thing in our list of column titles to be "gene"
        UMI_list_w_gene_list = gene_header + UMI_list  # The column headers for the dataFrame

        # Now open the big document of all UMIs, but only the columns that match the UMIs in our cluster:
        normalized_gene_count = pd.read_csv(path_normalized_gene_count, sep='\t', usecols=UMI_list_w_gene_list)

        # Write it:
        genotype_save_id = ['_wt', '_egl9', '_egl9_hif1']
        fn_final = (tissue + genotype_save_id[genotypes] + '_cluster' + str(cluster) +
                    '_normalized_Gene_Count_per_Cell.xlsx')

        save_path = os.path.join(path, fn_final)

        print('saving...')
        writer = pd.ExcelWriter(save_path, engine='xlsxwriter')
        writer.book.use_zip64()  # This line is necessary to write very large files as for the neuronal data
        normalized_gene_count.to_excel(writer, sheet_name='sheet1', index=False)
        writer.save()
        print('done')
