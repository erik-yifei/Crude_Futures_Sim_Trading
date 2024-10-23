# Backtesting.py

import pandas as pd
import numpy as np
import os

# Suppress SettingWithCopyWarning for cleaner output
pd.options.mode.chained_assignment = None  # default='warn'

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
    if 'Total_Score' not in merged_df.columns:
        raise ValueError("The 'Total_Score' column is not present in the provided DataFrame.")
    
    # Filter rows based on score within tolerance
    filtered_df = merged_df[np.abs(merged_df['Total_Score'] - score) <= tolerance].copy()
    
    # Reset index for cleanliness
    filtered_df.reset_index(drop=True, inplace=True)
    
    return filtered_df

def compute_sharpe_ratio(returns, investment_period_weeks, annual_risk_free_rate=0.03):
    """
    Computes the annualized Sharpe Ratio for a series of investment returns over a specific period.
    
    Parameters:
    - returns (pd.Series): Series of investment returns in percentage points (e.g., -8.39 for -8.39%).
    - investment_period_weeks (int): The holding period in weeks for the returns.
    - annual_risk_free_rate (float): The annual risk-free rate (default is 3%).
    
    Returns:
    - float: The annualized Sharpe Ratio.
    """
    # Convert returns from percentage points to decimals
    returns_decimal = returns / 100.0
    
    # Calculate the risk-free rate for the investment period
    # Using the compound interest formula to adjust the annual risk-free rate to the investment period
    risk_free_rate_period = (1 + annual_risk_free_rate) ** (investment_period_weeks / 52) - 1
    
    # Compute excess returns
    excess_returns = returns_decimal - risk_free_rate_period
    
    # Calculate mean and standard deviation of excess returns
    mean_excess = excess_returns.mean()
    std_excess = excess_returns.std()
    
    if std_excess == 0:
        return np.nan  # Avoid division by zero
    
    # Annualize the Sharpe Ratio
    # The scaling factor sqrt(52 / investment_period_weeks) adjusts the Sharpe Ratio to an annual basis
    sharpe_ratio = (mean_excess / std_excess) * np.sqrt(52 / investment_period_weeks)
    
    return sharpe_ratio

def backtest_scores(merged_df, scores, investment_periods, backtest_years, output_folder='Backtesting_Data', annual_risk_free_rate=0.03):
    """
    Performs backtesting for each score and investment period, computes Sharpe Ratios, and saves results.
    
    Parameters:
    - merged_df (pd.DataFrame): The merged DataFrame containing all data.
    - scores (list of float): List of Total_Score values to backtest.
    - investment_periods (list of int): List of investment periods in weeks.
    - backtest_years (list of int): List of years to include in backtesting.
    - output_folder (str): Directory to save backtesting CSV files.
    - annual_risk_free_rate (float): The annual risk-free rate for Sharpe Ratio calculation.
    
    Returns:
    - pd.DataFrame: Summary table of Sharpe Ratios for each score and investment period.
    """
    # Ensure output directory exists
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
        print(f"Created directory '{output_folder}' for backtesting outputs.")
    
    # Initialize list to store summary data
    summary_data = []
    
    for score in scores:
        print(f"\nProcessing Total_Score = {score}...")
        
        # Extract rows by score
        score_df = extract_rows_by_score(merged_df, score)
        
        # Filter for specified years
        score_df = score_df[score_df['Year'].isin(backtest_years)]
        
        # Define output CSV path
        score_filename = f"score_{score}.csv"
        score_filepath = os.path.join(output_folder, score_filename)
        
        # Save filtered data to CSV
        score_df.to_csv(score_filepath, index=False)
        print(f"Saved data for Total_Score = {score} to '{score_filepath}'.")
        
        # Compute Sharpe Ratios for each investment period
        for period in investment_periods:
            return_col_long = f"{period}_Week_Long_Return"
            return_col_short = f"{period}_Week_Short_Return"
            
            # Check if the return columns exist
            if return_col_long not in score_df.columns:
                print(f"Warning: Column '{return_col_long}' not found in data for Total_Score = {score}. Skipping.")
                continue
            
            # Extract long returns, drop NaN values
            returns_long = score_df[return_col_long].dropna()
            
            if returns_long.empty:
                sharpe_long = np.nan
                print(f"No long returns available for Investment Period = {period} weeks for Total_Score = {score}.")
            else:
                sharpe_long = compute_sharpe_ratio(returns_long, period, annual_risk_free_rate)
                print(f"Sharpe Ratio for {period}-Week Long Investment: {sharpe_long:.2f}")
            
            # Append to summary data
            summary_data.append({
                'Total_Score': score,
                'Investment_Period_Weeks': period,
                'Return_Type': 'Long',
                'Sharpe_Ratio': sharpe_long
            })
            
            # Optionally, compute Sharpe Ratio for short returns
            if return_col_short in score_df.columns:
                returns_short = score_df[return_col_short].dropna()
                
                if returns_short.empty:
                    sharpe_short = np.nan
                    print(f"No short returns available for Investment Period = {period} weeks for Total_Score = {score}.")
                else:
                    sharpe_short = compute_sharpe_ratio(returns_short, period, annual_risk_free_rate)
                    print(f"Sharpe Ratio for {period}-Week Short Investment: {sharpe_short:.2f}")
                
                # Append to summary data
                summary_data.append({
                    'Total_Score': score,
                    'Investment_Period_Weeks': period,
                    'Return_Type': 'Short',
                    'Sharpe_Ratio': sharpe_short
                })
            else:
                print(f"Warning: Column '{return_col_short}' not found in data for Total_Score = {score}. Skipping short returns.")
    
    # Create summary DataFrame
    summary_df = pd.DataFrame(summary_data)
    
    # Pivot the table for better readability
    summary_pivot = summary_df.pivot_table(index=['Total_Score'], 
                                          columns=['Investment_Period_Weeks', 'Return_Type'], 
                                          values='Sharpe_Ratio')
    
    # Flatten MultiIndex columns
    summary_pivot.columns = [f"{period}_Week_{rtype}" for period, rtype in summary_pivot.columns]
    
    # Save summary table to CSV
    summary_csv_path = os.path.join(output_folder, "sharpe_ratio_summary.csv")
    summary_pivot.to_csv(summary_csv_path)
    print(f"\nSaved Sharpe Ratio summary to '{summary_csv_path}'.")
    
    return summary_pivot

def main():
    # Define file paths
    merged_file = 'merged.csv'  # Ensure this file exists in your project directory
    output_folder = 'Backtesting_Data'
    
    # Define backtesting parameters
    scores = [2, 2.5, 3, 3.5, 4, 4.5, 5, -2, -2.5, -3, -3.5, -4]
    investment_periods = [1, 2, 3, 4, 8, 12, 24]  # in weeks
    backtest_years = [2019, 2020, 2021, 2022, 2023, 2024]  # adjust as needed
    
    # Risk-free rate (e.g., 3% annual)
    annual_risk_free_rate = 0.03
    
    # Load merged data
    if not os.path.exists(merged_file):
        print(f"Error: '{merged_file}' not found in the current directory.")
        return
    
    try:
        merged_df = pd.read_csv(merged_file, parse_dates=['Exchange Date'])  # Adjust 'Exchange Date' as needed
        print(f"Loaded '{merged_file}' successfully.")
    except Exception as e:
        print(f"Error loading '{merged_file}': {e}")
        return
    
    # Optional: Verify essential columns exist
    essential_columns = ['Year', 'Week_Number', 'Close', 'Total_Score']
    missing_columns = [col for col in essential_columns if col not in merged_df.columns]
    if missing_columns:
        print(f"Error: Missing essential columns in '{merged_file}': {missing_columns}")
        return
    
    # Perform backtesting
    summary = backtest_scores(
        merged_df=merged_df,
        scores=scores,
        investment_periods=investment_periods,
        backtest_years=backtest_years,
        output_folder=output_folder,
        annual_risk_free_rate=annual_risk_free_rate
    )
    
    # Display the summary table
    print("\n=== Sharpe Ratio Summary ===")
    print(summary)

if __name__ == "__main__":
    main()
