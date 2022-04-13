# 11-12-2021: I wanted a way to quickly tell whether which items are shared in common
# between a set of 3 lists. This program accepts as its input two-to-three single strings
# containing a list of genes separated by spaces and it outputs which of those items are common between them.
# It also can read in lists saved in excel files

import re
import pandas as pd
from itertools import zip_longest
from matplotlib_venn import venn3, venn3_circles
from matplotlib import pyplot as plt

operation_id = 'srs09.3'
list_1_name = 'intestine'
list_2_name = 'muscle'
list_3_name = 'neurons'
save_spreadsheet = True  # Toggles whether to save results as an excel file
venn = True  # Toggles whether to make a venn diagram out of results

# Read in lists:

# Chose source of list:
list_input = 'excel_file'  # Either 'excel_file', paste into console ('paste'),
# or coded into the script itself ('coded')

if list_input == 'excel_file':
    path = 'E:\\python\\python workspace\\saved_lists'
    column_name = 'gene'
    list_1_fn_path = path + '\\' + 'hits_srs09.2_intestine_aggregated.xlsx'
    list_2_fn_path = path + '\\' + 'hits_srs09.2_muscle_aggregated.xlsx'
    list_3_fn_path = path + '\\' + 'hits_srs09.2_neurons_aggregated.xlsx'

    list_1_df = pd.read_excel(list_1_fn_path, usecols=['%s' % column_name])
    list_1_df_drop = list_1_df.dropna()  # Drop any "nan" values which cause errors later
    list_1 = list_1_df_drop['%s' % column_name].tolist()

    list_2_df = pd.read_excel(list_2_fn_path, usecols=['%s' % column_name])
    list_2_df_drop = list_2_df.dropna()
    list_2 = list_2_df_drop['%s' % column_name].tolist()
    list_3_df = pd.read_excel(list_3_fn_path, usecols=['%s' % column_name])
    list_3_df_drop = list_3_df.dropna()
    list_3 = list_3_df_drop['%s' % column_name].tolist()

else:
    if list_input == 'pasted':
        list_1_string = input('Enter first list (please do not paste gene lists enclosed in quotation marks. '
                              'Items must be separated by commas and/or spaces):')
        list_2_string = input('Enter second list:')
        list_3_string = input('Enter third list (or just press enter to compare the first two lists):')

    # I used this for troubleshooting:
    else:
        list_1_string = '1 3 5 7'
        list_2_string = '1, 2, 3, 4, 5, 6, 7, 8, 9'
        list_3_string = '1, 5, 15, 42'

        # If 'pasted' or 'coded', get rid of all the commas:
        list_1_string_no_comma = list_1_string.replace(',', '')
        list_2_string_no_comma = list_2_string.replace(',', '')
        list_3_string_no_comma = list_3_string.replace(',', '')

    # Then use spaces to split the input genes into separate items in a list and delete any commas:
    list_1 = re.findall(r'\s|,|[^,\s]+', list_1_string_no_comma)
    list_2 = re.findall(r'\s|,|[^,\s]+', list_2_string_no_comma)
    list_3 = re.findall(r'\s|,|[^,\s]+', list_3_string_no_comma)

# Detect whether there is a list 3 input:
if len(list_3) > 1:
    threeLists = True
else:
    threeLists = False

# Now find the intersections and differences of these lists:

# First, find intersections:

if threeLists:
    intersection_1_2_unique = list(set(list_1).intersection(set(list_2))-set(list_3))
    # Note that "intersection_1_2_unique" list excludes genes from set 3

    intersection_2_3_unique = list(set(list_2).intersection(set(list_3))-set(list_1))
    intersection_1_3_unique = list(set(list_1).intersection(set(list_3))-set(list_2))

    intersection_1_2 = list(set(list_1).intersection(set(list_2)))  # This list doesn't remove genes from list 2
    intersection_all = list(set(intersection_1_2).intersection(set(list_3)))
else:
    intersection_1_2 = list(set(list_1).intersection(set(list_2)))

# Calculate unique entries based on whether you are using three list mode:

if not threeLists:
    unique_list1 = set(list_1) - set(list_2)
    unique_list2 = set(list_2) - set(list_1)
else:
    unique_list1 = set(list_1)-set(list_2)-set(list_3)
    unique_list2 = set(list_2)-set(list_1)-set(list_3)
    unique_list3 = set(list_3)-set(list_1)-set(list_2)

# Report the results:
reportResults = True
if reportResults is True:

    if not threeLists:
        output = "The following genes are common to both lists: " + str(' '.join(intersection_1_2))
        print(output)
        print('\n')
    else:
        output = "The following genes are common to all lists: " + str(' '.join(intersection_all))
        print(output)
        print('\n')

    output = "The following genes were unique to %s: " % list_1_name + str(' '.join(unique_list1))
    print(output)
    print('\n')

    output = "The following genes were unique to %s: " % list_2_name + str(' '.join(unique_list2))
    print(output)
    print('\n')

    if threeLists:
        output = "The following genes were unique to %s: " % list_3_name + str(' '.join(unique_list3))
        print(output)
        print('\n')

# Combine results into a dictionary, turn it into a dataframe, and save the results to an excel file:

if threeLists:
    data = {'Common to all': intersection_all, 'Unique to %s' % list_1_name: unique_list1,
            'Unique to %s' % list_2_name: unique_list2, 'Unique to %s' % list_3_name: unique_list3,
            'Shared uniquely by %s and %s' % (list_1_name, list_2_name): intersection_1_2_unique,
            'Shared uniquely by %s and %s' % (list_1_name, list_3_name): intersection_1_3_unique,
            'Shared uniquely by %s and %s' % (list_2_name, list_3_name): intersection_2_3_unique}
else:
    data = {'Common to all': intersection_all, 'Unique to %s' % list_1_name: unique_list1,
            'Unique to %s' % list_2_name: unique_list2,
            'Common to %s and %s' % (list_1_name, list_2_name): intersection_1_2}

zl = list(zip_longest(*data.values()))
save_df = pd.DataFrame(zl, columns=data.keys())

if save_spreadsheet:
    save_name = operation_id + '_intersection_of_significant_hits.xlsx'
    save_df.to_excel('E:\\python\\python workspace\\' + save_name, index=False)

if venn:
    if threeLists:
        venn3(subsets=(len(unique_list1), len(unique_list2), len(intersection_1_2_unique), len(unique_list3),
                       len(intersection_1_3_unique), len(intersection_2_3_unique), len(intersection_all)),
              set_labels=('%s' % list_1_name, '%s' % list_2_name, '%s' % list_3_name), alpha=0.5)
        plt.show()
