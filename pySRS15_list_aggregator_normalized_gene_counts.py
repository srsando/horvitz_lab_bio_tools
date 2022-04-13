# 12-16-2021: This program was modified from pySRS09, "list aggregator" .

# It finds spreadsheets that match certain filename criteria and then merges them to create a single large spreadsheet.
# Here, I've adapted it for looking at the output of py14 (get_mean_expression_from_from_list).
# It looks through those data and aggregates the mean, sd, and penetrance of gene expression


import os
import glob
import pandas as pd
import SRS_scRNAseq_tools

# Define the unique identifier for files produced in a given execution of this script:
operation_id = 'srs06.04'

# Set the threshold for calling something a "hit" - default is 10% cells expressing that gene:
percent_expression_threshold = 10

# Define the name and path of the cluster ID file that names the clusters based on their number:
id_path = "E:\\python\\python workspace\\cluster_id\\cluster ID.xlsx"
path = "E:\\python\\python workspace"

# Determine whether you want to simplify spreadsheet output when analyzing files derived from a single tissue type
# (i.e., print "neurons clusters 1, 2, 3" instead of "neurons cluster 1, neurons cluster 2, etc"
homogenous_tissue_input = True

# Make a list of all the excel documents in the path:
extension = 'xlsx'
os.chdir(path)
xls_list = glob.glob('*.{}'.format(extension))
if not bool(xls_list):  # Checks if list is empty (empty list = False)
    print("No files found with extension '%s' in '%s'" % (extension, path))
    quit()
for file in xls_list:
    print(file)

# Create dataFrame for lists of genes:

columnNames = ['gene', 'cell id', 'cluster', 'mean', 'sd', 'percent expressing', 'sample size']
collected_hits = pd.DataFrame(columns=columnNames)  # This dataframe collects all the genes in each cluster

target_index = 0  # For putting entries on the right lines in the final list of genes
summary_stats_target_index = 0  # For putting entries on the right lines in the final list of summary stats

# Look at everything in the list and process anything that starts with "hits":
for i in range(0, len(xls_list)):
    fn_decomposition = xls_list[i].split('_')  # Makes a list out of all parts of the filename separated by "_"

    if fn_decomposition[4] == "searchedFor":  # Checks for all pySRS14 outputs - i.e., all gene expression summary lists

        # Make dataFrame and import excel list of hits to it:
        hits = pd.read_excel(xls_list[i])

        # Fetch the ID of the cluster if you have one:

        # Generate the cluster name and number:
        current_tissue = fn_decomposition[1]
        current_cluster = fn_decomposition[1] + "_" + fn_decomposition[3]
        print(current_cluster)

        cell_ID = SRS_scRNAseq_tools.name_from_cluster_ID(current_cluster)

    # Look at each row and copy anything that has '% expressing" greater than 10%:
        for index, row in hits.iterrows():  # Step through each row
            if row['percent expressing'] >= percent_expression_threshold:  # Look at everything that passes threshold

                collected_hits.at[target_index, "gene"] = row["gene"]
                collected_hits.at[target_index, "cluster"] = current_cluster
                collected_hits.at[target_index, "cell id"] = cell_ID
                collected_hits.at[target_index, "mean"] = row["mean"]
                collected_hits.at[target_index, "sd"] = row["sd"]
                collected_hits.at[target_index, "percent expressing"] = row["percent expressing"]
                collected_hits.at[target_index, "sample size"] = row["sample size"]

                target_index = target_index + 1

# Count the number of times each gene appears in the "hits" dataframe:
gene_count = collected_hits["gene"].value_counts()

gene_count_df = pd.DataFrame(gene_count)  # Turn the results into a new dataframe
gene_count_df.rename(columns={'gene': 'number_clusters_expressing'}, inplace=True)

# Now, compile all hits across cell types and note which cell types they were hits in:
# Make a list of all hits across all clusters, duplicates removed:
columnNames = ['gene', 'cell id', 'clusters expressing']
hits_all_clusters_dup_removed = pd.DataFrame(columns=columnNames)
hits_all_clusters_dup_removed['gene'] = collected_hits['gene'].drop_duplicates()

entry_index = 0  # Like the "target_index" above, the entry index designates which line you write to.
cluster_list = []  # We'll put the clusters which each gene appears in in this list.
cell_id_list = []  # As with the cluster list, we'll put all the cell ids associated with a given gene here.

# Iterate through each row in the dataframe:

# First, for each row (i.e., each gene), check to see which clusters it was differentially regulated in
for index, row in hits_all_clusters_dup_removed.iterrows():
    for index_nested, row_nested in collected_hits.iterrows():  # Look through each row of the differential hits df
        if row_nested['gene'] == row['gene']:
            cluster_list.append(row_nested['cluster'])
            cell_id_list.append(SRS_scRNAseq_tools.name_from_cluster_ID(row_nested['cluster']))

    # If using data all from same tissue type, remove "tissue_cluster" from each of the entries in the cluster_list
    if homogenous_tissue_input:
        cluster_list_concise = []

        for x in cluster_list:
            if current_tissue.casefold() == 'intestine':
                next_num = x.replace('intestine_cluster', '')
            if current_tissue.casefold() == 'muscle':
                next_num = x.replace('muscle_cluster', '')
            if current_tissue.casefold() == 'neurons':
                next_num = x.replace('neurons_cluster', '')
            cluster_list_concise.append(next_num)

        # Convert the list of clusters to a string:
        cluster_list_string = current_tissue + " " + ", ".join(cluster_list_concise)
    else:
        # Include every tissue label if processing data from several tissues at once:
        cluster_list_string = ", ".join(cluster_list_concise)

    # Remove the duplicates from the cell_id_list and then convert to a string to put in excel:
    cell_id_list_no_dup = list(dict.fromkeys(cell_id_list))  # Remove duplicates

    # Remove any "NaNs" from the list, preventing an error that occurs when the "join" function encounters a float:
    cell_id_no_nan = [id_item for id_item in cell_id_list_no_dup if str(id_item) != 'nan']
    cell_id_list_string = ", ".join(cell_id_no_nan)  # Join all entries into a single string to print in excel.

    # Write the summary of which clusters and which cells the gene is differentially regulated in:
    hits_all_clusters_dup_removed.at[index, 'cell id'] = cell_id_list_string
    hits_all_clusters_dup_removed.at[index, 'clusters'] = cluster_list_string

    cluster_list = []
    cell_id_list = []
    entry_index = entry_index + 1  # The entry index makes sure you write each line to a new line of the df.

# Sort by name to eliminate any ambiguity as to what you're sorting by:
hits_all_clusters_dup_removed.sort_values('gene', inplace=True)

# Prepare file name:
fn_decomposition = xls_list[0].split('_')
fn_final = fn_decomposition[1] + '_' + operation_id + '_' + \
           fn_decomposition[2] + '_' + fn_decomposition[5] + '_' + 'genes_aggregated.xlsx'

# Save the file:
writer = pd.ExcelWriter(fn_final, engine='xlsxwriter')
hits_all_clusters_dup_removed.to_excel(writer, sheet_name='all hits - overview', index=False)
collected_hits.to_excel(writer, sheet_name='individual genes by tissue', index=False)
gene_count_df.to_excel(writer, sheet_name='summary gene cluster count')
writer.save()
