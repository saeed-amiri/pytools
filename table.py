import os, re
import pandas as pd

"""
reading a data file containing LJ parameters for waters from different literatures and converting it to a latex table
"""
def read_param(filename):
    df = pd.read_csv(filename, sep='\t')
    return  df

def table(df, x, y):
    numRows, numCols = df.shape


df = read_param('df')
print(df)