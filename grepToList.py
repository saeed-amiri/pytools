import sys
import pandas as pd

def split_title(grepLine):
    title = grepLine.strip()
    # remove the name of dir of zotero
    title = title.split(splitPart)[1]
    title = title.split('/')[1]
    # remove rest
    title = title.split('.pdf')[0]
    return title

fileName = sys.argv[1]
splitPart = sys.argv[2].__add__('/')

# for fileName in fileNames:
keyWord = fileName.strip().split('G')[0]
outName = keyWord.__add__('Titles')
titlesList = []
year = []
with open (fileName, 'r') as f:
    lines = f.readlines()
for line in lines:
    titlesList.append(split_title(line))
titles = list(set(titlesList))
for item in titles: 
    try:
        pubYear = int(item.split(' - ')[1].strip())
    except: 
        pubYear = 1111
    year.append(pubYear)
df = pd.DataFrame(titles, columns=[f"titles for '{keyWord}', # {len(titles)}" ])
df['Year'] = year
df = df.sort_values(by=[df.columns[1],df.columns[0]],na_position='last',ignore_index=True)
df = df.set_index('Year')
df.to_csv(outName, sep='\t')
print(fileName, len(titles))