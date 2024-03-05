import pandas as pd
from urllib.request import urlretrieve
import zipfile
import os

def load_names_from_web(category="both", hide_pre_1937=True):
    '''
    Downloads, unzips and loads the data into the returned dataframe
    category options: "national", "state" or "both"
    hide_pre_1937: "many people born before 1937 never applied for a Social Security card... [or] may not show the place of birth"
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
    
    
