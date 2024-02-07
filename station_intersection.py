import pandas as pd

# Paths to the CSV files
file1_path = r'C:\Users\ASUS\Documents\ANEproject\radio_stations_obtained_data.csv'
file2_path = r'C:\Users\ASUS\Documents\ANEproject\radio_stations_real_data.csv'

# Specific column for intersection
intersection_column = 'Frequency (MHz)'

# Read CSV files into pandas DataFrames
df1 = pd.read_csv(file1_path)
df2 = pd.read_csv(file2_path)

# Perform intersection on the specified column
intersection = pd.merge(df1, df2, on=intersection_column)

# Print the result or save it to a new CSV file
print(intersection)

# Save the result to a new CSV file
intersection.to_csv('intersection_result.csv', index=False)
