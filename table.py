import os, re, sys
import pandas as pd

"""
reading a data file containing LJ parameters for waters from different literatures and converting it to a latex table
"""
def read_param(filename):
    df = pd.read_csv(filename, sep='\t')
    return  df

class TABLE:
    def __init__(self, df) -> None:
        self.df = df
        self.numRows, self.numCols = self.df.shape
        # with open ("PARAM.water", 'w')
        # self.df.to_csv('PARAM.water', sep='\t')
        # print(df.to_string(),self.numRows, self.numCols,file=sys.stderr)

    
    def table(self):
        self.tab_header()
        self.tab_columns()
        self.math_parameter()
        self.do_cites()
        self.tab_rows()
        self.tab_ending()

    def tab_header(self):
        tex = f'\\begin{{center}}\n'
        tex += f'\\begin{{table}}\n'
        colsize = ['{']
        tex += '\t\\begin{tabular}'
        for i in range(1,self.numCols): colsize.append('p{1.8cm}')
        colsize.append('p{2.8cm}}')
        tex +=f"{' '.join([col for col in colsize])}\n" 
        tex +=f"\\hline\n"
        tex +=f"\\addlinespace"
        print(tex)
    
    def tab_columns(self):
        columns = []
        for i, item in enumerate(self.df.columns):
            if i < self.numCols-1:
                columns.append(f"{item}\t&")
            else:columns.append(f"{item}\t\\\\")
        tex = '\t'.join([col for col in columns])
        tex +=f"\n\t\\hline\n"
        print(f"\t{tex}\n")

    def tab_rows(self):
        for i in range(self.numRows): self.make_row(self.df.loc[i])
    
    def tab_ending(self):
        tex = '\t\\end{tabular}\n'
        tex += f'\\end{{table}}\n'
        tex += f'\\end{{center}}\n'
        print(tex)
    
    def make_row(self, row):
        tex_row = []
        for item in row[:-1]:
            if item: tex_row.append(item.__add__('\t&'))
        tex_row.append(row[-1].__add__('\\\\'))
        tex = ' '.join([item for item in tex_row])
        print(tex)#,file=sys.stderr)

    def math_parameter(self):
        params = [item for item in self.df.parameter]
        params = [self.name_underline(item) for item in params]
        params = [self.name_doller(item) for item in params]
        self.df.parameter = params

    def name_underline(self, item):
        if '_' in item :
            item = re.sub(r'(_)', r'\1{', item)
            item = item.__add__('}')
        else: pass
        return item

    def name_doller(self, item):
        if 'refrence' not in item :
            item = f"${item}$"
        else: pass
        return item

    def do_cites(self):
        cite_index = self.df.loc[self.df.parameter=='refrence'].index[0]
        for i, column in enumerate(self.df.columns):
            item = self.df.iloc[cite_index][column]
            if 'refrence' not in item:
                item = f"\cite{{{item}}}"
                self.df.at[cite_index,column]=item


sys.stdout = open('table.tex','w')

df = read_param('PARAM.water')
table = TABLE(df)
table.table()
sys.stdout = sys.stderr
