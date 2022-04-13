# 1-26-2022: A simple utility that converts tab-separated txt files into csvs. Made it to convert the outputs of geneontology.org GO term enrichment program into tables.

import os
import glob
import pandas as pd

path = "E:\\python\\python workspace"

# Make a list of all the .txt documents in the path:
extension = 'txt'
os.chdir(path)
txt_list = glob.glob('*.{}'.format(extension))
print(txt_list)

# Name columns to prevent parser error that occurs during input:
# (see https://stackoverflow.com/questions/18039057/python-pandas-error-tokenizing-data)
col_names=["col1", "col2", "col3", "col4", "col5", "col6", "col7", "col8"]

for i in range(0,len(txt_list)):
    myfile = path + '\\' + txt_list[i]
    print(myfile)
    df = pd.read_csv(myfile,sep='\t', names=col_names)

    fn_and_path = myfile.replace('.txt', '.csv')
    df.to_csv(fn_and_path)
