import pandas as pd
import json
import os

file_name = "로또 회차별 당첨번호_20260222112313.xlsx"

# The first row of the excel after skiprows=1 seems to be: 
# 1, 1212, 5, 8, 25, 31, 41, 44, 45, '1등', '12 명', '2,654,089,032 원'
# Which indicates columns are [Index, DrawNo, n1, n2, n3, n4, n5, n6, bonus, Rank, Winners, Prize]

try:
    df = pd.read_excel(file_name, skiprows=1)
    
    # Check if there are column names or if they just became the first row data,
    # because pandas might use first row as columns.
    data = []
    
    # add the "columns" as a row if they are numbers
    if df.columns[0] == 1 or str(df.columns[0]) == '1':
        row_dict = {
            "draw": int(df.columns[1]),
            "numbers": [int(df.columns[2]), int(df.columns[3]), int(df.columns[4]), int(df.columns[5]), int(df.columns[6]), int(df.columns[7])],
            "bonus": int(df.columns[8])
        }
        data.append(row_dict)

    for index, row in df.iterrows():
        try:
            row_dict = {
                "draw": int(row.iloc[1]),
                "numbers": [int(row.iloc[2]), int(row.iloc[3]), int(row.iloc[4]), int(row.iloc[5]), int(row.iloc[6]), int(row.iloc[7])],
                "bonus": int(row.iloc[8])
            }
            data.append(row_dict)
        except Exception as e:
            continue
            
    # sort by draw number desc
    data = sorted(data, key=lambda x: x["draw"], reverse=True)
    
    output_path = os.path.join("lotto-app", "src", "assets", "lotto_data.json")
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print("Successfully generated lotto_data.json with", len(data), "draws.")
except Exception as e:
    print("Error generating json:", e)
