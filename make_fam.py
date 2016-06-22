import random
import pandas as pd
from collections import defaultdict

sex = dict(M=1, F=2)
regions = ['Africa', 'Black_Sea', 'Asia_Pacific', 'New_World']

def safe_dict_sample(pop, k):
    if len(pop) <= k:
        return(pop)
    else:
        return(random.sample(pop,k))

def random_df_group_subsample(df, groups, size):
    grouped = df.groupby(groups)
    lol = [safe_dict_sample(grouped.groups[x], size) for x in grouped.groups]
    subsampled = df.ix[sorted([i for sublist in lol for i in sublist])]
    return subsampled

def make_popID(row):
    if row['Region']=='Lab':
        return row['Population_Name']
    if row['Region'] in regions:
        pop = row['Population_Name']
        state = row['State/Province']
        country = row['Country']
        retstr = pop
        if pd.notnull(state) and state!=pop:
            retstr=retstr+"_"+state
        if pd.notnull(country) and country!=pop:
            retstr=retstr+"_"+country
        return retstr
    else:
        return row['Population_Name']
    
def make_fam(df, outfn):
    fam_rows = []
    tmpdf = df.copy(deep=True)
    tmpdf['Sex'] = tmpdf['Sex'].fillna(0).replace(to_replace=sex).astype(int)
    tmpdf[['Maternal_ID', 'Paternal_ID']] = tmpdf[['Maternal_ID', 'Paternal_ID']].fillna(0).astype(int)
    tmpdf['Phenotype'] = tmpdf['Phenotype'].fillna(-9).astype(int)
    for i, row in tmpdf.iterrows():
        tmp_str = '\t'.join([str(x) for x in [make_popID(row), row['Sample'], 
                            row['Paternal_ID'], row['Maternal_ID'], 
                            row['Sex'], row['Phenotype']]])+'\n'
        fam_rows.append(tmp_str.encode('ascii', 'ignore'))
    outfh = open(outfn, 'wb')
    [outfh.write(x) for x in fam_rows]
    outfh.close()
    

    
if __name__ == '__main__':
    df = pd.read_excel('https://yale.box.com/shared/static/bkhiisj4ztjwaetrhx3f9wgua8oq3t53.xlsx',sheetname='ALL')
    #get rid of failed samples, mendel tests, samples for others
    nofailed = ~df['Notes'].str.contains('FAILED', na=False)
    nomendel = ~df['Population_Name'].str.contains('Mendel', na=False)
    #noothers = ~df['Region'].str.contains('For_Others', na=False)
    #sdf = random_df_group_subsample(df[nofailed & nomendel & noothers], 'Population_Name', 12)
    sdf = random_df_group_subsample(df[nofailed & nomendel], 'Population_Name', 120)
    make_fam(sdf, 'all_inds.fam')
    sdf.to_csv('all_inds_popinfo.tsv',sep='\t',columns=['Population_Name','Sample','Region'],index=False)
    
    