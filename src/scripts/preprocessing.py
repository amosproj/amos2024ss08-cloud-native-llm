"""
This script merges data from two CSV files containing question-answer pairs into a single CSV file.

Functions:
- merge_data():
  Reads two CSV files ('sources/qa.csv' and 'sources/cncf_stackoverflow_qas.csv'), selects and renames
  specific columns of interest from each file, concatenates them, and saves the merged data to 'sources/merged_qas.csv'.
  Prints a success message upon completion.

Example usage:
Run the script to merge question-answer pairs from 'sources/qa.csv' and 'sources/cncf_stackoverflow_qas.csv'
and save the merged data to 'sources/merged_qas.csv'.
"""

import pandas as pd

def merge_data() -> None:
    """
    Merge data from two CSV files and save the merged DataFrame to a new CSV file.

    Reads 'sources/qa.csv' and 'sources/cncf_stackoverflow_qas.csv',
    selects relevant columns, renames them if necessary, concatenates them,
    and saves the merged data to 'sources/merged_qas.csv'.

    Args:
        None

    Returns:
        None
    """
    
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
    # Drop additional columns
    df2 = df2.drop(['question_id', 'score'], axis=1)
    # Concatenate the selected and renamed columns
    merged_df = pd.concat([df1_selected, df2_selected])

    # Save the merged DataFrame to a new CSV file
    merged_df.to_csv('sources/merged_qas.csv', index=False)

    print("Columns merged and saved successfully!")

if __name__ == "__main__": 
    merge_data()