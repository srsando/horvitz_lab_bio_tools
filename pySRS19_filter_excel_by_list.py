# 1-27-2022: This program accepts as inputs a list of gene lists and outputs the sites of expression of each gene

# Made for looking at the outputs of the GO term enrichment analysis from geneontology.org.
# We found we often want to look at a given set of enriched genes for a given term to see
# if they are expressed in the same set of cells. The main summary output sheet of pySRS09 has all this information for
# a given dataset, but it's slow to search by hand, and while excel does support list-based filtering it doesn't
# let you automatically save the list after.

# In developing this script, I discovered that the geneontology.org GO term enrichment tool truncates C. elegans
# cosmid names (i.e., C32F10.9 becomes C32F10). See notes below for how that affects this program.

import SRS_python_utilities as srs
import pandas as pd
import numpy as np
import re

# User-defined variables:
cluster_summary = True  # Mark "True" if you want to summarize your summary by cluster as well.
path = 'E:\\python\\python workspace\\'
operation_id = 'srs10.3_'  # The operation_id links a given execution of the script to a lab notebook entry.

summary_file = 'E:\\python\\python workspace\\hits_srs09.2_intestine_aggregated.xlsx'  # The file to be filtered.

# Make a dataframe of summary results - this is what will be filtered by each sublist:
summary_df = pd.read_excel(summary_file)
summary_df_dropna = summary_df.dropna()  # Drop the NaNs because they cause an issue when filtering.

# Make a list of all .xlsx files in the path:
xlsx_list = srs.list_path_files_by_ext(path, 'xlsx')

for files in xlsx_list:
    # For each file, check if it's a list of scraped GO terms
    # with associated genes (i.e., fits "XXX_extracted" name format):
    fn_decomposition = files.split('_')
    if fn_decomposition[1] == 'extracted':
        print('\n')
        print('Opening 1 of the 3 ontology lists of lists of GO terms and associated genes...')

        # Then take that list of lists and use each list to make a different filtered summary:

        # Open the list of lists of genes by which to filter:

        df_list_of_lists = pd.read_excel(files, header=None)
        df_lol_drop = df_list_of_lists.dropna(how='all')
        df_lol_drop_noNa = df_list_of_lists.replace(np.nan, '', regex=True)

        # Generate a list of actual lists to work with:
        individual_lists = df_lol_drop_noNa.values.tolist()

        # Remove empty strings from lists:
        individual_lists_trimmed = []  # This is where we'll put each new list after removing empty strings
        for lists in individual_lists:
            newlist = [gene for gene in lists if len(gene) >= 1]
            individual_lists_trimmed.append(newlist)

        individual_lists_trimmed_2 = [item for item in individual_lists_trimmed if item != []]

        for lists in individual_lists_trimmed_2:
            # print('Opening list of GO term with associated genes')
            if lists == False:  # Don't look at the list if it's empty
                print('empty list ignored')
            else:

                # Now, filter the df:

                # Important: originally, I used the commented-out code below:
                    # filter = summary_df.gene.isin(lists)
                    # filtered_df = summary_df[filter]

                # However, geneontology.org's GO term analyzer strips the last # from C. elegans cosmid names:
                # i.e., C34G10.9 -> C34G10.

                # Because the above method looks for exact matches, this meant that none of those genes
                # were included in the summary sheets. To fix this, I'm using the following method:
                # https://stackoverflow.com/questions/55941100/how-to-filter-pandas-dataframe-rows-which-contains-any-string-from-a-list

                lists_drop_nan = [x for x in lists if x != 'nan']
                filtered_df = summary_df_dropna[
                    summary_df_dropna.stack().str.contains('|'.join(lists_drop_nan)).any(level=0)]

                # Important: the geneontology.org GO-term enrichment tool  unfortunately trims the end off cosmid notes
                # e.g., C32F10.8 is trimmed to C32F10.
                # Thus, if C32F10.1 and C32F10.2 were both differentially regulated,
                # they will both be pulled into the summary sheet if either appeared associated with
                # a given enriched GO term.
                #
                # We can't get around this without using a different GO-term enrichment program,
                # and right now we don't want to reinvent the wheel. We'll correct it manually after the fact.

                # For now, I'm going to add a tool that flags files with such events
                # by putting "CHECK" in their filenames.

                # I'll identify those files by comparing the number of terms in the list output
                # from the GO-term enrichment analyzer to the number of genes in the summary.
                # If multiple genes from a given cosmid were differentially regulated, this should result
                # in additional genes being pulled into the summary.
                # e.g. if ced-10 and C32F10.1 were enriched and associated with a "cell death" GO term,
                # but both C32F10.1 and C32F10.2 were in the master list,
                # the summary document would list 3 genes: ced-10, C32F10.1, and C32F10.2.
                # Thus, there would be an extra gene. Spreadsheets with more genes than expected will be marked when saved.

                # Count how many genes are in the list we're using to filter:
                no_genes_in_term = str(
                    len(lists) - 1)  # The "- 1" accounts for the fact that the list includes a GO term as well
                no_genes_in_summary = str(len(filtered_df.index))

                if int(no_genes_in_summary) - int(no_genes_in_term) != 0:
                    # If there's a discrepancy, note it in the save name:
                    print('discrepancy detected with term %s:' % lists[0])
                    print('%s genes expected, %s genes reported' % (no_genes_in_term, no_genes_in_summary))
                    save_name = 'GO_enriched_' + operation_id + fn_decomposition[3] + '_' + \
                                fn_decomposition[4] + '_' + fn_decomposition[5][:-5] + '_' + lists[0] + 'CHECK' + '.csv'
                else:  # Otherwise, save as normal:
                    save_name = 'GO_enriched_' + operation_id + fn_decomposition[3] + '_' + \
                                fn_decomposition[4] + '_' + fn_decomposition[5][:-5] + '_' + lists[0] + '.csv'

                save_name_and_path = path + '\\GO_enrichment_results\\' + save_name

# If no additional summaries are required, save it:
                if cluster_summary == False:
                    filtered_df.to_csv(save_name_and_path, header=True)
# If additional summaries, do them:
                else:
                    gene_list = filtered_df['gene'].tolist()  # The list of genes associated with this GO term
                    gene_expression_dict = {}  # This dictionary will hold the gene expression data of each cluster

                    for genes in gene_list:
                        # Grow a list of IDs of each tissue in which this gene is expressed here:
                        tissues_expressed_in = []

                        # Get the sites of expression for that gene from the df:
                        expression_sites_series = filtered_df.loc[filtered_df['gene'] == genes, 'clusters'].astype(str)
                        exp_sites_str = expression_sites_series.to_string()
                        exp_sites_str_split = re.split('[, ]', exp_sites_str)
                        del exp_sites_str_split[0]  # Remove the index from the series.
                        # Discard non-integers:
                        for items in exp_sites_str_split:
                            if items.isnumeric():
                                tissues_expressed_in.append(items)
# Add to the dictionaries:
                        for clusters in tissues_expressed_in:
                            if clusters in gene_expression_dict:
                                gene_expression_dict[clusters].append(genes)
                            else:
                                gene_expression_dict[clusters] = [genes]


print('Note: discrepancies between the number of genes associated with a given term and the number of genes appearing in the summary spreadsheet of that term are typically due to the presence of multiple genes derived from the same cosmid - see notes.')
