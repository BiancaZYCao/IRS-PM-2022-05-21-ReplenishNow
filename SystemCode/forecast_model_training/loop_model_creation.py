import pandas as pd
import subprocess

totalID = len(pd.read_csv('sales_order.csv').itemID.unique())
for i in range(totalID):
    print(i)
    subprocess.run(['python3', 'create_model.py', '-i', str(i)])
    subprocess.run('clear')