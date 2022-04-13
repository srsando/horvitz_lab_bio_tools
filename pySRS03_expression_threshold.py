
# Sorts through a folder of spreadsheets of differential gene expression results.
# For each spreadsheet (i.e., tissue), it picks the genes that meet user-defined fold-change and adjusted p-values and
# aves them in a new spreadsheet of hits.

# This script is far from ideal; it would be much have been much easier to use pandas to filter each
# Spreadsheet based on the properties desired

import xlwt
import xlrd
import os
import glob

# User-defined variables:
path = "E:\\python\\python workspace"  # The path of the folder to operate on
operation_id = 'srs11.3_'  # This defines the unique identifier for files produced in a given execution of this script:

# Set threshold for up-regulation:
FC_threshold = float(0.3785)  # For the data we are working with this will be log2
print('log2(FC) threshold set to %s' % FC_threshold)

# Set significance cut-off for adjusted p-values:
p_value_type = 'non-adjusted'  # p-value can be "adjusted" or "non-adjusted"
significance_threshold = 0.01
print('using %s p-values, with significance threshold of %s ' % (p_value_type, significance_threshold))

# Calculate the threshold for negative expression changes:
FC_threshold_neg = float(FC_threshold * -1)

# Make a list of all the excel documents in the path:
extension = 'xls'
os.chdir(path)
xls_list = glob.glob('*.{}'.format(extension))
print(xls_list)

# This can go through the list:
for i in range(0, len(xls_list)):
    print(xls_list[i])
    fn_decomposition = xls_list[i].split('_')  # Makes a list out of all parts of the filename separated by "_"

# Check if the last piece of the filename is "collected"
    if fn_decomposition[5] == "collected.xls":

        # Open and name Excel file and sheet:
        workbook_collected = xlrd.open_workbook(xls_list[i])  # Open the workbook
        sheet_collected = workbook_collected.sheet_by_index(0)  # Open the sheet

# Create the new spreadsheet to copy hits into:
        workbook_hits = xlwt.Workbook()
        sheet_hits = workbook_hits.add_sheet("hits")

# Make titles bold
        header_font = xlwt.Font()
        header_font.name = 'Arial'
        header_font.bold = True

        header_style = xlwt.XFStyle()
        header_style.font = header_font

# Name the titles in the sheet we're writing to (probably could do this with a list more succinctly)
        sheet_hits.write(0, 0, 'gene', header_style)
        sheet_hits.write(0, 1, 'egl-9 - avg_log2FC', header_style)
        sheet_hits.write(0, 2, 'p_val', header_style)
        sheet_hits.write(0, 3, 'p_val_adj', header_style)
        sheet_hits.write(0, 4, 'egl-9 hif-1 - avg_log2FC', header_style)
        sheet_hits.write(0, 5, 'p_val', header_style)
        sheet_hits.write(0, 6, 'p_val_adj', header_style)

# Now search the source file for genes that hit the expression threshold:
        hit_index = 1  # The hit index indexes the spreadsheet of hits
        for r in range(1, sheet_collected.nrows):  # Look at each row except the title row

            egl9_log2fc = sheet_collected.cell_value(r, 1)
            is_string_egl9 = isinstance(egl9_log2fc, str)

            egl9_hif1_log2fc = sheet_collected.cell_value(r, 4)
            is_string_egl9_hif1 = isinstance(egl9_hif1_log2fc, str)

# Select adjusted or non-adjusted p-value:
            if p_value_type == 'adjusted':
                p_value_use_egl9 = sheet_collected.cell_value(r, 3)
                p_value_use_egl9_hif1 = sheet_collected.cell_value(r, 6)

            if p_value_type == 'non-adjusted':
                p_value_use_egl9 = sheet_collected.cell_value(r, 2)
                p_value_use_egl9_hif1 = sheet_collected.cell_value(r, 5)
            else:
                print('enter valid p-value type')

            if p_value_use_egl9 <= significance_threshold and p_value_use_egl9_hif1 <= significance_threshold:
                significant = True
            else:
                significant = False

            if is_string_egl9 or is_string_egl9_hif1:
                print("one of these columns contains a string")
            elif egl9_log2fc >= FC_threshold and egl9_hif1_log2fc <= FC_threshold_neg and significant == True:

                # Set up a loop to copy desired row column-by-column into the new excel sheet
                for c in range(sheet_collected.ncols):
                    # "c" tracks column and i tracks row
                    sheet_hits.write(hit_index, c, sheet_collected.cell_value(r, c))
                # Each new hit is written to the next line of the output document:
                hit_index = hit_index + 1

            elif egl9_log2fc <= FC_threshold_neg and egl9_hif1_log2fc >= FC_threshold and significant == True:
                # Set up a loop to copy desired row column-by-column into the new excel sheet
                for c in range(sheet_collected.ncols):
                    # "c" tracks column and "i" tracks row
                    sheet_hits.write(hit_index, c, sheet_collected.cell_value(r, c))
                hit_index = hit_index + 1  # Each new hit is written to the next line of the output document
        collected_save = "hits_" + operation_id + xls_list[i]
        workbook_hits.save(collected_save)
