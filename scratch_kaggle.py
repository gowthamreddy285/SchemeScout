import kagglehub
import pandas as pd
import os

try:
    path = kagglehub.dataset_download('jainamgada45/indian-government-schemes')
    print('Path:', path)
    files = os.listdir(path)
    print('Files:', files)
    
    csv_files = [f for f in files if f.endswith('.csv')]
    if csv_files:
        df = pd.read_csv(os.path.join(path, csv_files[0]))
        print('Shape:', df.shape)
        print('Columns:', df.columns.tolist())
        print(df.head(2).to_markdown())
except Exception as e:
    print("Error:", e)
