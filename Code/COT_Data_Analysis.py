import pandas as pd

def process_cot_data(df):
    """
    Cleans and processes the COT data, including calculating normalized positions and scores.
    
    Parameters:
    - df (pd.DataFrame): Raw COT data.
    
    Returns:
    - pd.DataFrame: Cleaned and processed COT data with additional calculations.
    """
    
    # Step 1: Select Relevant Columns
    relevant_columns = [
        'Report_Date_as_YYYY_MM_DD',
        'YYYY Report Week WW',
        'Open_Interest_All',
        'NonComm_Positions_Long_All',
        'NonComm_Positions_Short_All',
        'Change_in_Open_Interest_All',
        'Change_in_NonComm_Long_All',
        'Change_in_NonComm_Short_All'
    ]
    df = df[relevant_columns].copy()
    
    # Step 2: Clean and Parse 'Report_Date_as_YYYY_MM_DD' to datetime
    df['Report_Date'] = pd.to_datetime(df['Report_Date_as_YYYY_MM_DD'], format='%m/%d/%Y %I:%M:%S %p', errors='coerce')
    
    # Drop rows with invalid dates
    if df['Report_Date'].isna().any():
        print("Warning: Some dates could not be parsed. Rows with invalid dates will be dropped.")
        print(df[df['Report_Date'].isna()][['Report_Date_as_YYYY_MM_DD']])
        df = df.dropna(subset=['Report_Date'])
    
    # Step 3: Extract 'Year' and 'Week_Number' from 'YYYY Report Week WW'
    # Assuming 'YYYY Report Week WW' is in the format '2022 Report Week 37'
    df['Year'] = df['YYYY Report Week WW'].str.extract(r'(\d{4})').astype(int)
    df['Week_Number'] = df['YYYY Report Week WW'].str.extract(r'Week (\d{1,2})').astype(int)
    
    # Step 4: Adjust 'Week_Number' to merge week 53 into week 52
    df['Week_Number'] = df['Week_Number'].replace({53: 52})
    
    # Step 5: Sort the DataFrame first by 'Year' descending, then by 'Week_Number' descending
    df = df.sort_values(['Year', 'Week_Number'], ascending=[False, False]).reset_index(drop=True)
    
    # Step 6: Handle duplicates by grouping and aggregating (taking the mean)
    df = df.groupby(['Year', 'Week_Number'], as_index=False).agg({
        'Report_Date': 'first',
        'Open_Interest_All': 'mean',
        'NonComm_Positions_Long_All': 'mean',
        'NonComm_Positions_Short_All': 'mean',
        'Change_in_Open_Interest_All': 'mean',
        'Change_in_NonComm_Long_All': 'mean',
        'Change_in_NonComm_Short_All': 'mean'
    })
    
    # Step 7: Sort again to ensure order from newest to oldest after grouping
    df = df.sort_values(['Year', 'Week_Number'], ascending=[False, False]).reset_index(drop=True)
    
    # Step 8: Rename Columns for Clarity
    df = df.rename(columns={
        'Report_Date_as_YYYY_MM_DD': 'Report_Date_Raw',
        'Report_Date': 'Report_Date',
        'YYYY Report Week WW': 'Report_Week_Raw'
    })
    
    # Step 9: Rearrange Columns
    df = df[[
        'Report_Date',
        'Year',
        'Week_Number',
        'Open_Interest_All',
        'NonComm_Positions_Long_All',
        'NonComm_Positions_Short_All',
        'Change_in_Open_Interest_All',
        'Change_in_NonComm_Long_All',
        'Change_in_NonComm_Short_All'
    ]]
    
    # Step 10: Data Validation and Cleaning
    # Remove rows with zero or negative Open Interest
    df = df[df['Open_Interest_All'] > 0]
    
    # Fill missing values in positions with zero
    df['NonComm_Positions_Long_All'] = df['NonComm_Positions_Long_All'].fillna(0)
    df['NonComm_Positions_Short_All'] = df['NonComm_Positions_Short_All'].fillna(0)
    
    # Step 11: Calculate Normalized Total Non-Commercial Positions
    df['Normalized_NonComm_Positions'] = (df['NonComm_Positions_Long_All'] + df['NonComm_Positions_Short_All']) / df['Open_Interest_All']
    
    # Step 12: Calculate Total Long Position Ratio
    df['Long_Position_Ratio'] = df['NonComm_Positions_Long_All'] / df['Open_Interest_All']
    
    # Step 13: Calculate Total Short Position Ratio
    df['Short_Position_Ratio'] = df['NonComm_Positions_Short_All'] / df['Open_Interest_All']
    
    # Step 14: Calculate Bullish/Bearish Score
    # If Long > Short, assign -1 (bearish)
    # If Short > Long, assign 1 (bullish)
    # If Long == Short, assign 0 (neutral)
    df['Bullish_Bearish_Score'] = df.apply(
        lambda row: -1 if row['NonComm_Positions_Long_All'] > row['NonComm_Positions_Short_All'] else (1 if row['NonComm_Positions_Short_All'] > row['NonComm_Positions_Long_All'] else 0),
        axis=1
    )
    
    # Step 15: Calculate Delta Inventory Score
    # If ΔLong < ΔShort, assign 1 (bullish)
    # If ΔLong > ΔShort, assign -1 (bearish)
    # If ΔLong == ΔShort, assign 0 (neutral)
    df['Delta_Score'] = df.apply(
        lambda row: 1 if row['Change_in_NonComm_Long_All'] < row['Change_in_NonComm_Short_All'] else (-1 if row['Change_in_NonComm_Long_All'] > row['Change_in_NonComm_Short_All'] else 0),
        axis=1
    )
    
    # Step 16: Rearrange Columns to Place Calculated Columns Adjacent to Relevant Data
    df = df[[
        'Report_Date',
        'Year',
        'Week_Number',
        'Open_Interest_All',
        'NonComm_Positions_Long_All',
        'NonComm_Positions_Short_All',
        'Normalized_NonComm_Positions',
        'Long_Position_Ratio',
        'Short_Position_Ratio',
        'Bullish_Bearish_Score',
        'Change_in_Open_Interest_All',
        'Change_in_NonComm_Long_All',
        'Change_in_NonComm_Short_All',
        'Delta_Score'
    ]]
    
    return df


# Used to return processed inventory data 
def cot_redacted(df):
    selected_columns = ['Year', 'Week_Number', 'Bullish_Bearish_Score', 'Delta_Score']
    redacted_df = df[selected_columns].copy()
    return redacted_df


# Plotting - Need to be refined
import matplotlib.pyplot as plt

def plot_cot_scores(df):
    """
    Plots Bullish/Bearish Scores and Delta Scores over Weeks.
    
    Parameters:
    - df (pd.DataFrame): Processed COT data with scores.
    
    Returns:
    - None
    """
    
    # Sort the DataFrame by Year and Week_Number in ascending order for plotting over time
    df_sorted = df.sort_values(['Year', 'Week_Number'], ascending=[True, True])
    
    # Create a continuous week number for plotting
    # Assuming data spans multiple years, we can create a cumulative week number
    df_sorted = df_sorted.reset_index(drop=True)
    df_sorted['Cumulative_Week'] = (df_sorted['Year'] - df_sorted['Year'].min()) * 52 + df_sorted['Week_Number']
    
    plt.figure(figsize=(15, 6))
    
    # Plot Bullish/Bearish Score
    plt.subplot(2, 1, 1)
    plt.plot(df_sorted['Cumulative_Week'], df_sorted['Bullish_Bearish_Score'], label='Bullish/Bearish Score', color='blue')
    plt.axhline(0, color='black', linewidth=0.5)
    plt.title('Bullish/Bearish Score Over Time')
    plt.xlabel('Cumulative Week Number')
    plt.ylabel('Score')
    plt.legend()
    plt.grid(True)
    
    # Plot Delta Score
    plt.subplot(2, 1, 2)
    plt.plot(df_sorted['Cumulative_Week'], df_sorted['Delta_Score'], label='Delta Score', color='red')
    plt.axhline(0, color='black', linewidth=0.5)
    plt.title('Delta Score Over Time')
    plt.xlabel('Cumulative Week Number')
    plt.ylabel('Score')
    plt.legend()
    plt.grid(True)
    
    plt.tight_layout()
    plt.show()

# Usage Example:
# Assuming 'processed_cot' is your processed COT DataFrame
# plot_cot_scores(processed_cot)

# Load the COT data
cot_data = pd.read_csv('C:Data\COT.csv')

# Process the COT data
processed_cot = process_cot_data(cot_data)
processed_cot_clean = cot_redacted(processed_cot)
# Display the first few rows of the processed DataFrame
print(processed_cot.head())

# Optionally, save the processed data to a new CSV file
processed_cot_clean.to_csv('processed_cot_clean.csv', index=False)
print("Processed COT data has been saved to 'cot_processed.csv'.")



