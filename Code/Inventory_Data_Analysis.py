import pandas as pd
import matplotlib.pyplot as plt

def process_inventory_data(df):
    # Step 1: Clean 'Date' column
    df['Date'] = df['Date'].astype(str).str.strip().str.replace('"', '')
    
    # Step 2: Parse 'Date' to datetime format
    df['Date'] = pd.to_datetime(df['Date'], format='%b %d, %Y', errors='coerce')
    
    # Step 3: Check for parsing errors
    if df['Date'].isna().any():
        print("Warning: Some dates could not be parsed. Rows with invalid dates will be dropped.")
        print(df[df['Date'].isna()]['Date'])
        df = df.dropna(subset=['Date'])
    
    # Step 4: Extract 'Year' and 'Week_Number'
    df['Year'] = df['Date'].dt.year
    df['Week_Number'] = df['Date'].dt.isocalendar().week
    
    # Step 5: Adjust 'Week_Number' to merge week 53 into week 52
    df['Week_Number'] = df['Week_Number'].replace({53: 52})
    
    # Step 6: Sort the DataFrame first by 'Year' descending, then by 'Week_Number' descending
    df = df.sort_values(['Year', 'Week_Number'], ascending=[False, False]).reset_index(drop=True)

    # Step 7: Select relevant columns and rename for easier reference
    df = df[['Date', 'Year', 'Week_Number', 
             'Weekly U.S. Ending Stocks excluding SPR of Crude Oil  (Thousand Barrels)']]
    df = df.rename(columns={
        'Weekly U.S. Ending Stocks excluding SPR of Crude Oil  (Thousand Barrels)': 
        'Ending Stocks Excluding SPR (Thousand Barrels)'
    })
    
    
    # Step 8: Handle duplicates by grouping and aggregating (taking the mean)
    df = df.groupby(['Year', 'Week_Number'], as_index=False).agg({
        'Date': 'first',
        'Ending Stocks Excluding SPR (Thousand Barrels)': 'mean'
    })
    
    # Step 9: Calculate 5 and 10-Year Averages (excluding 2020)
    current_year = df['Year'].max()
    df_for_avg = df[(df['Year'] != current_year) & (df['Year'] != 2020)]
    
    # Define the years to include in the averages
    years_available = df_for_avg['Year'].unique()
    years_available.sort()
    years_5yr = years_available[-5:]
    years_10yr = years_available[-10:]
    
    # Calculate 5-Year Average, Max, and Min Inventory Level for each Week_Number
    avg_5yr = df_for_avg[df_for_avg['Year'].isin(years_5yr)].groupby('Week_Number')['Ending Stocks Excluding SPR (Thousand Barrels)'].agg(['mean', 'max', 'min']).reset_index()
    avg_5yr = avg_5yr.rename(columns={
        'mean': '5yr Average Inventory',
        'max': '5yr Max Inventory',
        'min': '5yr Min Inventory'
    })
    
    # Calculate 10-Year Average, Max, and Min Inventory Level for each Week_Number
    avg_10yr = df_for_avg[df_for_avg['Year'].isin(years_10yr)].groupby('Week_Number')['Ending Stocks Excluding SPR (Thousand Barrels)'].agg(['mean', 'max', 'min']).reset_index()
    avg_10yr = avg_10yr.rename(columns={
        'mean': '10yr Average Inventory',
        'max': '10yr Max Inventory',
        'min': '10yr Min Inventory'
    })
    
    # Merge the averages back into the main DataFrame
    df = df.merge(avg_5yr, on='Week_Number', how='left')
    df = df.merge(avg_10yr, on='Week_Number', how='left')
    
    # Step 10: Calculate "Absolute Storage Score"
    # If current inventory is lower than either the 5yr or 10yr average, score = 1; else, score = -1
    df['Absolute Storage Score'] = df.apply(
        lambda row: 1 if (row['Ending Stocks Excluding SPR (Thousand Barrels)'] < row['5yr Average Inventory']) or
                             (row['Ending Stocks Excluding SPR (Thousand Barrels)'] < row['10yr Average Inventory'])
                  else -1, axis=1)
    
    # Step 11: Calculate Delta Inventory (Week-over-Week Change)
    # Since the data is sorted from newest to oldest, delta = current - previous
    df['Delta Inventory'] = df['Ending Stocks Excluding SPR (Thousand Barrels)'].diff(periods=1)
    df['Delta Inventory'] = df['Delta Inventory'].fillna(0)  # Fill NaN for the first entry
    
    # Step 12: Calculate 5 and 10-Year Average Delta Inventory for each Week_Number (excluding 2020)
    # Calculate delta inventory for previous years
    df_for_avg['Delta Inventory'] = df_for_avg.groupby('Year')['Ending Stocks Excluding SPR (Thousand Barrels)'].diff(periods=1)
    df_for_avg['Delta Inventory'] = df_for_avg['Delta Inventory'].fillna(0)
    
    df = df.sort_values(['Year', 'Week_Number'], ascending=[False, False]).reset_index(drop=True)

    # 5-Year Average Delta Inventory
    avg_delta_5yr = df_for_avg[df_for_avg['Year'].isin(years_5yr)].groupby('Week_Number')['Delta Inventory'].mean().reset_index()
    avg_delta_5yr = avg_delta_5yr.rename(columns={'Delta Inventory': '5yr Average Delta Inventory'})
    
    # 10-Year Average Delta Inventory
    avg_delta_10yr = df_for_avg[df_for_avg['Year'].isin(years_10yr)].groupby('Week_Number')['Delta Inventory'].mean().reset_index()
    avg_delta_10yr = avg_delta_10yr.rename(columns={'Delta Inventory': '10yr Average Delta Inventory'})
    
    # Merge the average deltas back into the main DataFrame
    df = df.merge(avg_delta_5yr, on='Week_Number', how='left')
    df = df.merge(avg_delta_10yr, on='Week_Number', how='left')
    
    # Step 13: Calculate "Delta Inventory Score"
    # If current delta is drawing faster than seasonality (more negative than average), score = 1; else, score = -1
    def delta_inventory_score(row):
        current_delta = row['Delta Inventory']
        avg_delta_5yr = row['5yr Average Delta Inventory']
        avg_delta_10yr = row['10yr Average Delta Inventory']
        
        # Drawing faster means current_delta is more negative than average deltas
        if (current_delta < avg_delta_5yr) or (current_delta < avg_delta_10yr):
            return 1
        else:
            return -1
    
    df['Delta Inventory Score'] = df.apply(delta_inventory_score, axis=1)
    
    # Step 14: Organize columns
    df = df[['Date', 'Year', 'Week_Number', 
             'Ending Stocks Excluding SPR (Thousand Barrels)', 
             '5yr Average Inventory', '5yr Max Inventory', '5yr Min Inventory',
             '10yr Average Inventory', '10yr Max Inventory', '10yr Min Inventory',
             'Absolute Storage Score',
             'Delta Inventory', '5yr Average Delta Inventory', '10yr Average Delta Inventory', 
             'Delta Inventory Score']]
    
    df = df.sort_values(['Year', 'Week_Number'], ascending=[False, False]).reset_index(drop=True)

    return df

# Used to return processed inventory data 
def inventory_redacted(df):
    selected_columns = ['Year', 'Week_Number', 'Absolute Storage Score', 'Delta Inventory Score']
    redacted_df = df[selected_columns].copy()
    return redacted_df


def plot_inventory_graphs(df):
    # Define the years to plot
    years_to_plot = [df['Year'].max(), df['Year'].max()-1]  # 2024 and 2023
    
    # Define the average periods
    avg_periods = {
        '5-Year': {
            'avg': '5yr Average Inventory',
            'max': '5yr Max Inventory',
            'min': '5yr Min Inventory'
        },
        '10-Year': {
            'avg': '10yr Average Inventory',
            'max': '10yr Max Inventory',
            'min': '10yr Min Inventory'
        }
    }
    
    # Prepare data for 5-Year Average Graph
    plt.figure(figsize=(14, 7))
    
    # Plot 2024 and 2023 inventory levels
    for year in years_to_plot:
        subset = df[df['Year'] == year]
        plt.plot(subset['Week_Number'], subset['Ending Stocks Excluding SPR (Thousand Barrels)'], label=str(year))
    
    # Plot 5-Year Average
    plt.plot(df['Week_Number'], df['5yr Average Inventory'], label='5-Year Average', linestyle='--', color='blue')
    
    # Plot 5-Year Max and Min
    plt.fill_between(df['Week_Number'], df['5yr Min Inventory'], df['5yr Max Inventory'], color='blue', alpha=0.1, label='5-Year Range')
    
    # Configure the plot
    plt.xlabel('Week Number')
    plt.ylabel('Ending Stocks Excluding SPR (Thousand Barrels)')
    plt.title('Crude Oil Inventory Levels: 2024, 2023, and 5-Year Average')
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()
    
    # Prepare data for 10-Year Average Graph
    plt.figure(figsize=(14, 7))
    
    # Plot 2024 and 2023 inventory levels
    for year in years_to_plot:
        subset = df[df['Year'] == year]
        plt.plot(subset['Week_Number'], subset['Ending Stocks Excluding SPR (Thousand Barrels)'], label=str(year))
    
    # Plot 10-Year Average
    plt.plot(df['Week_Number'], df['10yr Average Inventory'], label='10-Year Average', linestyle='--', color='green')
    
    # Plot 10-Year Max and Min
    plt.fill_between(df['Week_Number'], df['10yr Min Inventory'], df['10yr Max Inventory'], color='green', alpha=0.1, label='10-Year Range')
    
    # Configure the plot
    plt.xlabel('Week Number')
    plt.ylabel('Ending Stocks Excluding SPR (Thousand Barrels)')
    plt.title('Crude Oil Inventory Levels: 2024, 2023, and 10-Year Average')
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()


# Load the data
inventory = pd.read_csv('C:Data\Inventory.csv')

# Process the inventory data
processed_inventory = process_inventory_data(inventory)
processed_inventory_clean = inventory_redacted(processed_inventory)

# plot_inventory_graphs(processed_inventory)

# Optionally, save the processed DataFrame to CSV
processed_inventory_clean.to_csv('processed_inventory_clean.csv', index=False)
print("Processed data has been saved to 'inventory_processed.csv'.")
