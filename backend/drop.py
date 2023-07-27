import pandas as pd

file_path = r'C:\Users\jayed\Documents\jayed\data\ECommerce.csv'
output_file_path = r'E:\gits\recom\ecom.csv'

df = pd.read_csv(file_path)

# Drop rows after user_id 100
df_modified = df[df['user_id'] <= 1000]

df_modified.to_csv(output_file_path, index=False)
