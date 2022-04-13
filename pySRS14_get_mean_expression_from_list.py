# This program looks through the normalize_gene_count spreadsheets.
# For each gene in a user-defined list, it calculates the mean and sd of expression.

import pandas as pd
import SRS_python_utilities

# Define the unique identifier for files produced in a given execution of this script:
operation_id = 'srs06.3'

# Make the list of genes to look for:

candidate_list_fn = 'list2_mec_genes.xlsx'
list_fn_decomposition = candidate_list_fn.split('_')

candidate_list_path = 'E:\\python\\python workspace\\saved_lists'  # Path of gene list
candidate_list_path_fn = candidate_list_path + '\\' + candidate_list_fn
list_df = pd.read_excel(candidate_list_path_fn, usecols=['gene'])
candidate_list = list_df['gene'].tolist()

# Search the path for files with 'xlsx' endings:
path = 'E:\\python\\python workspace'
xls_list = SRS_python_utilities.list_path_files_by_ext(path, 'xlsx')

# Now open each file, search it for hits, calculate mean/sd, and save:
for file in xls_list:
    fn = file
    fn_decomposition = fn.split('_')
    if fn_decomposition[5] == 'Count':

        # Open the file:
        fn_path = path + '\\' + fn
        cluster_spreadsheet_gene_list = pd.read_excel(fn_path, usecols=['gene'])
        cluster_gene_list = cluster_spreadsheet_gene_list['gene'].tolist()

        cluster_spreadsheet_gene_list.set_index('gene', inplace=True)

        # Find which of the candidate genes are in the sequencing data.
        candidates_present = []  # This is where the genes present in both lists will be places

        for candidate in candidate_list:
            if candidate in cluster_gene_list:
                candidates_present.append(candidate)

        # Now we know which genes to search the spreadsheet for, which we do:

        # Open the whole file this time:
        cluster_normalized_gene_count = pd.read_excel(fn_path)
        cluster_normalized_gene_count.set_index('gene', inplace=True)

        # Pull out the rows that have the genes and calculate mean/sd/fraction expressing:
        row_means = cluster_normalized_gene_count.loc[candidates_present].mean(axis=1)
        row_sd = cluster_normalized_gene_count.loc[candidates_present].std(axis=1)

        num_entries = cluster_normalized_gene_count.loc[candidates_present].count(axis=1)
        zero_count = cluster_normalized_gene_count.loc[candidates_present].isin([0]).sum(axis=1)
        fraction_zeroes = zero_count.div(num_entries)
        percent_expressing = 100 * (1 - fraction_zeroes)

        # Merge and save:
        result = pd.concat([row_means, row_sd, percent_expressing, num_entries], axis=1)
        result = result.rename(columns={0: 'mean', 1: 'sd', 2: 'percent expressing', 3: 'sample size'})

        save_list = [operation_id, fn_decomposition[0], fn_decomposition[1],
                     fn_decomposition[2], 'searchedFor', list_fn_decomposition[1],
                     list_fn_decomposition[2]]
        save_name = '_'.join(save_list)

        result.to_excel(path + '\\' + save_name)
