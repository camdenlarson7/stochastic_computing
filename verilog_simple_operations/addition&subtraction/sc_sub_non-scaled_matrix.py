# visual_matrix.py
# Visual table for f(i,j) = (i/100 + (1 - j/100)) / 2

import pandas as pd

STEP = 5
INCLUDE_100 = False  # set True to go 0..100; False for 0..95

vals = list(range(0, 101 if INCLUDE_100 else 100, STEP))
idx_labels = [f"{i/100:.2f}" for i in vals]  # row labels (i/100)
col_labels = [f"{j/100:.2f}" for j in vals]  # column labels (j/100)

data = []
for i in vals:
    ai = i / 100
    row = []
    for j in vals:
        aj = j / 100
        val = (ai + (1 - aj)) / 2
        row.append(round(val, 3))
    data.append(row)

df = pd.DataFrame(data, index=idx_labels, columns=col_labels)

# Pretty print
pd.set_option("display.max_rows", None)
pd.set_option("display.max_columns", None)
pd.set_option("display.width", 180)
pd.set_option("display.colheader_justify", "center")

print("\nMatrix: f(i,j) = (i/100 + (1 - j/100)) / 2")
print("Rows = i/100, Columns = j/100\n")
print(df)

# Optional: save to CSV for Excel
df.to_csv("matrix_table.csv", index_label="i\\j")
print("\nSaved to matrix_table.csv")
