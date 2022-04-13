# This script can be used to bold any text in an Excel file that matches a user-defined list

import SRS_spreadsheet_tools
import pandas as pd

# The file you want to format:
path = 'E:\python\python workspace\\srs07.1_intersection_of_significant_hits.xlsx'

# The list you want to use to define formatting:
list_path = 'E:\python\python workspace\saved_lists\\list1_Cory_RNA_seq_hits.xlsx'

format_list_df = pd.read_excel(list_path)

print(format_list_df)

format_list = format_list_df['gene'].tolist()

SRS_spreadsheet_tools.xl_conditional_format_from_list(path, format_list)
