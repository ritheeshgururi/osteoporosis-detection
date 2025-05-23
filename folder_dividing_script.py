import pandas as pd
import os
import shutil

df_osteopenia_pve = pd.read_csv('R:\Downloads\df_copy (1).csv')

source_folder = 'R:\Images'

destination_folder = 'R:\Pictures\My personal Onedrive Folder\OneDrive\Documents\Research Project\Osteoporosis Negative Images'
os.makedirs(destination_folder, exist_ok=True)

for index, row in df_osteopenia_pve.iterrows():
    # Get the file name
    file_name = row['filestem']

    source_file = os.path.join(source_folder, file_name)

    destination_file = os.path.join(destination_folder, file_name)

    if os.path.exists(source_file):
        shutil.copy(source_file, destination_file)
    else:
        print("Source file does not exist:", source_file)