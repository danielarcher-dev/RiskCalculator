import pandas as pd

# Create a Pandas dataframe
df = pd.DataFrame({"Data": [10, 20, 30]})

# Create an Excel writer using xlsxwriter
writer = pd.ExcelWriter("output.xlsx", engine="xlsxwriter")
df.to_excel(writer, sheet_name="Sheet1")

# Get the workbook and worksheet objects
workbook = writer.book
worksheet = writer.sheets["Sheet1"]

# Insert an image
worksheet.insert_image("B2", "example.png")

# Save the file
writer.close()