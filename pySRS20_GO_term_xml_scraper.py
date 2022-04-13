# 1-26-2022: This script is used to scrape GO terms and their associated gene names from the geneontology.org
# GO term enrichment analyzer's xml data output. It processes xml files and then outputs excel files which list each
# GO term and the genes that belong to that term.

# Note that you should save the output of the GO term enrichment analysis according to the following format:
# "GO_enrich_**operation_id**_**tissue**_**ontology**":
# **operation_id** is the identifier for the lab notebook entry
# **tissue** is intestine/muscle/neurons
# **ontology** is biological process/molecular function/cellular component
# Example: GO_enrich_srs10.5_intestine_biological_process

import SRS_python_utilities
import re
import pandas as pd

# User-defined variables:
operation_id = 'srs10.2'  # Use this to link a given instance of script execution to a lab notebook entry.
path = "E:\\python\\python workspace"  # Where the files are stored

# Search the source folder for all xml files and make a list:
xml_list = SRS_python_utilities.list_path_files_by_ext(path, "xml")

# Load each file in turn and extract the relevant info:
for files in xml_list:

    # First, open the file:
    with open(files, 'r') as file:
        data = file.read()

    # Now break the contents up into a string based on where the new GO terms appear
    # In the xml document, GO terms are flanked by "<label>", i.e., "<label>GO_term_</label>".
    process_split = list(data.split("<label>"))
    GO_term_list = []
    list_of_gene_lists = []

    for items in process_split:

        # Grab the text (i.e., GO term) between '<label>' and '</label>':
        process_split_substring = re.search('<label>|(.*?)/|</label>', items)

        # Print the GO_term obtained above - using '[1]' because this variable is a "re.Match" object:
        GO_term = process_split_substring[1]
        # For some reason the re.search function is including the "<" after the GO term; strip it here:
        GO_term = GO_term[:-1]

        GO_term_list.append(GO_term)  # Add the latest term to a growing list of terms

# Break the chunk belonging to the current GO term up into bits for each gene (format is "<mapped_id>GENE</mapped_id>":
        split_enriched_genes = items.split("<mapped_id>")
        enriched_gene_list = []  # A list to add the scraped genes to.

        for genes in split_enriched_genes:
            # A stray string of text containing the word 'FISHER' is accidentaly captured - this removes it:
            if 'FISHER' in genes:
                pass
            else:
                # Grab the text (i.e., gene) between '<mapped_id>' and '</mapped_id>':
                enriched_split_substring = re.search('<mapped_id>|(.*?)/|</mapped_id>', genes)

                # Print the gene obtained above. using "[1]" because this variable is a "re.Match" object:
                enriched_gene = enriched_split_substring[1]
                enriched_gene = enriched_gene[:-1]  # Again, remove the "<".
                enriched_gene_list.append(enriched_gene)

        list_of_gene_lists.append(enriched_gene_list)  # Add the latest list to the list of lists for each GO term.

    # Turn the list of lists into a dataframe:
    df = pd.DataFrame(list_of_gene_lists)
    # Specify the save name:
    input_fn_decomposition = list(files.split('_'))

    # Don't try to save files with an incorrect number of sections in their names:
    if len(input_fn_decomposition) <= 5:
        print('Naming format of file with name "%s" incorrect - filename has too few terms! File not saved.' % files)
    # Generate save name:
    else:
        fn = 'GO_extracted_' + operation_id + '_' + input_fn_decomposition[3] \
             + '_' + input_fn_decomposition[4] + '_' + input_fn_decomposition[5][:-4] + '.xlsx'

        path_and_fn = path + '\\' + fn

        # Save it:
        df.to_excel(path_and_fn, index=False, columns=None, header=False)
        print('File save - %s' % fn)
