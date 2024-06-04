import pandas as pd

def merge_data():
    
    # Paths to the CSV files
    csv_file_1 = 'sources/qa.csv' # Answer
    csv_file_2 = 'sources/cncf_stackoverflow_qas.csv' # answer

    # Read the CSV files
    df1 = pd.read_csv(csv_file_1)
    df2 = pd.read_csv(csv_file_2)

    # Select and rename the columns of interest from the first file
    column1_file1 = 'Question'
    column2_file1 = 'Answer'
    df1_selected = df1[['Question', 'Answer', 'Project']]

    # Select and rename the columns of interest from the second file

    df2_selected = df2[['question', 'answer', 'tag']].rename(columns={
        'question': 'Question',
        'answer': 'Answer',
        'tag': 'Project'
    })

    # Concatenate the selected and renamed columns
    merged_df = pd.concat([df1_selected, df2_selected])

    # Save the merged DataFrame to a new CSV file
    merged_df.to_csv('merged_qas.csv', index=False)

    print("Columns merged and saved successfully!")

if __name__ == "__main__": 
    merge_data()