import pandas as pd
from urllib.request import urlretrieve
import zipfile
import os
from sklearn.model_selection import train_test_split

def births_per_year():
    return pd.read_csv('birthsbyyear/birthsbyyear.csv').set_index('year')

def births_in_year(year, gender='total'):
    # don't use this in a loop, takes too long
    births_per_year = pd.read_csv('birthsbyyear/birthsbyyear.csv').set_index('year')
    return births_per_year.at[year, gender]

def load_names_from_web(category="both", hide_pre_1937=True, use_existing_files=False):
    '''
    Downloads, unzips and loads the data into the returned dataframe
    category options: "national", "state" or "both"
    hide_pre_1937: "many people born before 1937 never applied for a Social Security card... [or] may not show the place of birth"
    use_existing_files: Don't bother to redownload and reunzip
    '''

    # these are the URLs
    national_url = "https://www.ssa.gov/OACT/babynames/names.zip"
    state_url = "https://www.ssa.gov/OACT/babynames/state/namesbystate.zip"
    
    # unzip filename variables
    national_file = national_url.split('/')[-1]
    state_file = state_url.split('/')[-1]
    national_unzip_path = "national_unzip_path"
    state_unzip_path = "state_unzip_path"
    
    # multiple dataframes will be created then concatenated. Store the list of dataframes:
    list_of_dfs = []
    order_of_columns = ['state', 'year', 'name', 'M/F', 'count']
    
    # get the national data
    if (category=="national") or (category=="both"):
        if not use_existing_files:
            urlretrieve(national_url, national_file)
            with zipfile.ZipFile(national_file, 'r') as zip_ref:
                zip_ref.extractall(national_unzip_path)
        for file in os.listdir(national_unzip_path):
            temp_df = pd.read_csv(national_unzip_path + '/' + file, names=['name', 'M/F', 'count'])
            temp_df['year'] = int(file.split('yob')[1].split('.txt')[0])
            temp_df['state'] = 'US'
            temp_df = temp_df[order_of_columns]
            list_of_dfs.append(temp_df)        
    
    
    # get the state data
    if (category=="state") or (category=="both"):
        if not use_existing_files:
            urlretrieve(state_url, state_file)
            with zipfile.ZipFile(state_file, 'r') as zip_ref:
                zip_ref.extractall(state_unzip_path)
        for file in os.listdir(state_unzip_path):
            # print(state_unzip_path + '/' + file)
            if file[-3:] != 'pdf':    # or contains ReadMe...
                temp_df = pd.read_csv(state_unzip_path + '/' + file, names=['state', 'M/F', 'year', 'name','count'])
                temp_df = temp_df[order_of_columns]
                list_of_dfs.append(temp_df)
    
    # now concatenate all of the individual DFs
    df = pd.concat(list_of_dfs, ignore_index=True)
    
    # see note above about this parameter
    if (hide_pre_1937):
        df = df[df['year']>=1937]

        
    # delete files? Or just git ignore?
        
    return df
    
    
def holdout_split(df, holdout_size=0.2, modern_year=2013):
    '''
    split into a set of names for training/testing, and a holdout or validation set. try to do it in a stratified manner so each set has some of the most popular names of all time and recently.
    '''

    # create labels for stratification

    # assume we have US in the data (could be wrong)
    df1 = df[df['state'] == 'US']

    df2 = df1[df1['year'] >= modern_year].copy()

    def label_by_pop(mydf):
        mydf['name-M/F'] = mydf['name'] + '-' + mydf['M/F']
        counts = mydf.groupby('name-M/F')['count'].sum()
        counts = counts.reset_index()
        counts['M/F'] = counts['name-M/F'].str[-1]
        counts['name'] = counts['name-M/F'].str[:-2]
        counts = counts.sort_values(by='count', ascending=False)
        def label_by_gender(mydf2, g):
            mydf2 = mydf2[mydf2['M/F'] == g].reset_index(drop=True)
            mydf2['label'] = str(g + '10000')
            mydf2.loc[0:9, 'label'] = str(g + '10')
            mydf2.loc[10:99, 'label'] = str(g + '100')
            mydf2.loc[100:999, 'label'] = str(g + '1000')
            return mydf2
        counts = pd.concat([label_by_gender(counts, 'M'),
                            label_by_gender(counts, 'F')],
                            ignore_index=True)
        return counts[['name', 'M/F', 'label']]
    
    names1 = label_by_pop(df1)
    names2 = label_by_pop(df2)
    names = pd.merge(names1, names2, on=['name', 'M/F'], suffixes=['1','2'])
    names['label'] = names.apply(lambda row: row['label1'] if len(row['label1']) < len(row['label2']) else row['label2'], axis=1)
    labels = names['label']

    train_names, holdout_names = train_test_split(names, test_size=holdout_size, random_state=0, stratify=labels)
    train_names['set'] = 'train'
    holdout_names['set'] = 'holdout'
    names = pd.concat([train_names, holdout_names])
    df2 = pd.merge(df, names, how='left', on=['name', 'M/F'])
    X_train = df2[df2['set'] == 'train'].reset_index(drop=True).drop(columns=['label', 'set', 'label1', 'label2'])
    X_holdout = df2[df2['set'] == 'holdout'].reset_index(drop=True).drop(columns=['label', 'set', 'label1', 'label2'])

    return X_train, X_holdout

def year_split(df, holdout_size=10):
    '''
    split into train/holdout sets where the holdout set is all known data and the train set is all known data prior to the latest known year minus the holdout_size number of years. all available names are included in each set, it only splits by years. essentially training based on data known up to a certain point and then trying to predict data past that point.
    '''

    most_recent_year = df['year'].max()
    cutoff_year = most_recent_year - holdout_size

    X_train = df[df['year'] <= cutoff_year]
    X_holdout = df

    return X_train, X_holdout