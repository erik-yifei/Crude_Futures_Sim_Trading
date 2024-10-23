import pandas as pd

price = pd.read_csv('C:Data\Price.csv')

def process_price_data(df):
    # Step 1: Clean 'Exchange Date' column
    df['Exchange Date'] = df['Exchange Date'].astype(str).str.strip()
    df['Exchange Date'] = df['Exchange Date'].str.split().str[0]
    
    # Step 2: Parse 'Exchange Date' without specifying the format
    df['Exchange Date'] = pd.to_datetime(df['Exchange Date'], errors='coerce')
    
    # Step 3: Check for any parsing errors
    if df['Exchange Date'].isna().any():
        print("Warning: Some dates could not be parsed. Rows with invalid dates will be dropped.")
        print(df[df['Exchange Date'].isna()]['Exchange Date'])
        df = df.dropna(subset=['Exchange Date'])
    
    # Step 4: Extract 'Year' and 'Week_Number'
    df['Year'] = df['Exchange Date'].dt.year
    df['Week_Number'] = df['Exchange Date'].dt.isocalendar().week

    # Step 5: Adjust 'Week_Number' to merge week 53 into week 52
    df['Week_Number'] = df['Week_Number'].replace({53: 52})

    # Step 6: Group by 'Year' and 'Week_Number' and aggregate
    # For numeric columns, we'll take the mean
    numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
    # Exclude 'Year' and 'Week_Number' from aggregation to prevent averaging them
    numeric_cols.remove('Year')
    numeric_cols.remove('Week_Number')

    df = df.groupby(['Year', 'Week_Number'], as_index=False)[numeric_cols].mean()

    # Step 7: Reconstruct 'Exchange Date' as the first day of the week
    df['Exchange Date'] = pd.to_datetime(
        df['Year'].astype(str) + '-W' + df['Week_Number'].astype(str) + '-1',
        format='%Y-W%W-%w'
    )

    # Step 8: Order the DataFrame from newest to oldest
    df = df.sort_values('Exchange Date', ascending=False).reset_index(drop=True)

    # Alternatively, using numpy's select for better performance on large datasets
    import numpy as np
    conditions = [
        df['Close'] <= 68,
        (df['Close'] > 68) & (df['Close'] < 70)
    ]
    choices = [1, 0.5]
    df['Price Score'] = np.select(conditions, choices, default=0)

    # Step 9: Calculate future weekly profits using shift method
    weeks = [1, 2, 3, 4, 8, 12, 24]
    for week in weeks:
        future_close = df['Close'].shift(week)
        # Calculate long futures returns
        df[f'{week}_Week_Long_Return'] = ((future_close - df['Close']) / df['Close']) * 100
        # Calculate short futures returns
        df[f'{week}_Week_Short_Return'] = df['Close'].pct_change(periods=week) * 100

    return df


# Process the price data
processed_price = process_price_data(price)

# Display the processed DataFrame
print(processed_price.head())

# Optionally, visualize the DataFrame using tabulate
from tabulate import tabulate
print(tabulate(processed_price.head(), headers='keys', tablefmt='psql'))

# Save the processed DataFrame to a new CSV file
processed_price.to_csv('processed_price.csv', index=False)

print("Processed data has been saved to 'processed_price.csv'.")
