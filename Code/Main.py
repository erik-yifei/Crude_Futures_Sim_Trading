import pandas as pd
import numpy as np
from COT_Data_Analysis import process_cot_data, cot_redacted
from Inventory_Data_Analysis import process_inventory_data, inventory_redacted, plot_inventory_graphs
from Price_Data_Analysis import process_price_data

def merge_dataframes(price_df, inventory_df, cot_df):
    """
    Merges Price, Inventory, and COT DataFrames on Year and Week_Number.
    Inserts the score columns to the right of the Price Score column.
    Calculates a Total_Score by summing individual scores.
    
    Parameters:
    - price_df (pd.DataFrame): Processed Price DataFrame.
    - inventory_df (pd.DataFrame): Processed Inventory DataFrame.
    - cot_df (pd.DataFrame): Processed COT DataFrame.
    
    Returns:
    - pd.DataFrame: Merged DataFrame with score columns and Total_Score.
    """
    
    # Step 1: Ensure Unique Year and Week_Number in Inventory DataFrame
    if inventory_df.duplicated(subset=['Year', 'Week_Number']).any():
        inventory_df = inventory_df.groupby(['Year', 'Week_Number'], as_index=False).mean()
        print("Duplicates found in Inventory DataFrame. Aggregated by mean.")
    
    # Step 2: Ensure Unique Year and Week_Number in COT DataFrame
    if cot_df.duplicated(subset=['Year', 'Week_Number']).any():
        cot_df = cot_df.groupby(['Year', 'Week_Number'], as_index=False).mean()
        print("Duplicates found in COT DataFrame. Aggregated by mean.")
    
    # Step 3: Merge Inventory and COT with Price DataFrame
    merged_df = price_df.merge(inventory_df, on=['Year', 'Week_Number'], how='left')
    merged_df = merged_df.merge(cot_df, on=['Year', 'Week_Number'], how='left')
    
    # Step 4: Insert Score Columns After 'Price Score'
    score_columns = ['Price Score', 'Bullish_Bearish_Score', 'Delta_Score', 'Absolute Storage Score', 'Delta Inventory Score']
    
    # Check if 'Price Score' exists
    if 'Price Score' not in merged_df.columns:
        raise ValueError("'Price Score' column not found in Price DataFrame.")
    
    # Find the index of 'Price Score'
    price_score_idx = merged_df.columns.get_loc('Price Score')
    
    # Rearrange columns to insert score columns after 'Price Score'
    cols = list(merged_df.columns)
    # Remove score columns if they are already present elsewhere
    cols = [col for col in cols if col not in score_columns]
    
    # Insert score columns after 'Price Score'
    for i, score_col in enumerate(score_columns):
        cols.insert(price_score_idx + 1 + i, score_col)
    
    merged_df = merged_df[cols]
    
    # Step 5: Calculate Total_Score by Summing Individual Scores
    # Define the score columns to sum
    score_columns_to_sum = score_columns  # Excluding 'Price Score' as per user's instruction
    
    # Check if all score columns exist
    missing_score_cols = [col for col in score_columns_to_sum if col not in merged_df.columns]
    if missing_score_cols:
        raise ValueError(f"The following score columns are missing in the merged DataFrame: {missing_score_cols}")
    
    # Fill NaN values in score columns with 0
    merged_df[score_columns_to_sum] = merged_df[score_columns_to_sum].fillna(0)
    
    # Calculate Total_Score
    merged_df['Total_Score'] = merged_df[score_columns_to_sum].sum(axis=1)
    
    return merged_df


def extract_rows_by_score(merged_df, score, tolerance=1e-5):
    """
    Extracts all rows from the merged DataFrame that have a 'Total_Score' equal to the given score.

    Parameters:
    - merged_df (pd.DataFrame): The merged DataFrame containing 'Total_Score' column.
    - score (float): The score value to filter rows by.
    - tolerance (float, optional): The allowable difference between 'Total_Score' and score for matching.
                                   Default is 1e-5 for exact matching.

    Returns:
    - pd.DataFrame: A DataFrame containing only the rows with 'Total_Score' equal to the given score within the specified tolerance.
    
    Raises:
    - ValueError: If the 'Total_Score' column is not found in the DataFrame.
    """
    
    # Step 1: Validate Input DataFrame
    if 'Total_Score' not in merged_df.columns:
        raise ValueError("The 'Total_Score' column is not present in the provided DataFrame.")
    
    # Step 2: Filter Rows Based on 'Total_Score'
    # Using tolerance to account for floating-point precision issues
    filtered_df = merged_df[np.abs(merged_df['Total_Score'] - score) <= tolerance].copy()
    
    # Optional: Reset Index of the Filtered DataFrame
    filtered_df.reset_index(drop=True, inplace=True)
    
    return filtered_df

price = pd.read_csv('C:Data\Price.csv')
inventory = pd.read_csv('C:Data\Inventory.csv')
cot_data = pd.read_csv('C:Data\COT.csv')

processed_price = process_price_data(price)
processed_inventory = inventory_redacted(process_inventory_data(inventory))
processed_cot = cot_redacted(process_cot_data(cot_data))

merged = merge_dataframes(processed_price, processed_inventory, processed_cot)

# Save the processed DataFrame to a new CSV file
merged.to_csv('merged.csv', index=False)
print("Merged data has been saved to 'merged.csv'.")

merged_score_check = extract_rows_by_score(merged, 4)
merged_score_check.to_csv('merged_score_check.csv', index=False)
print("Merged data has been saved to 'merged_score_check.csv'.")