import pandas as pd

# Load Excel file
file_path = r'C:\Users\DELL\Documents\chibuike\past questions.xlsx'
excel_file = pd.ExcelFile(file_path)

# Print all sheet names
print("Sheet names:", excel_file.sheet_names)

# Iterate over each sheet and print its columns
for sheet_name in excel_file.sheet_names:
    df = pd.read_excel(file_path, sheet_name=sheet_name)
    print(f"\nColumns in sheet '{sheet_name}':", df.columns)
