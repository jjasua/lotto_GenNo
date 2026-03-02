import pandas as pd
import json
import os

file_name = "로또 회차별 당첨번호_20260222112313.xlsx"
df = pd.read_excel(file_name, skiprows=1)
print(df.columns)
print(df.head(2))
