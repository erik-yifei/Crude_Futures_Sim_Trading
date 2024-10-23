# Crude_Futures_Sim_Trading

Welcome to the Crude Oil Simulation Trading Project! This project leverages historical crude oil data to simulate trading strategies based on price movements, inventory levels, and Commitment of Traders (COT) reports. By integrating multiple data sources and applying a scoring system, this simulation aims to provide insights into potential trading opportunities and market sentiment.

# 📈 Project Overview
The Crude Oil Simulation Trading Project is designed to analyze and simulate trading strategies in the crude oil market. By processing and merging data from various sources, the project assigns scores to each trading week, enabling the identification of bullish or bearish market conditions. This comprehensive analysis facilitates informed decision-making for simulated trading scenarios.

# 🛠️ Features
Data Integration: Combines Price, Inventory, and COT data based on Year and Week_Number.
Scoring System: Assigns scores to each week based on price thresholds, inventory changes, and trader sentiment.
Total Score Calculation: Aggregates individual scores to provide an overall market sentiment indicator.
Data Filtering: Extracts specific rows based on total score values for targeted analysis.
Visualization: (Optional) Visualizes price movements and scores over time.
Automated Processing: Streamlines data cleaning, processing, and merging through modular Python scripts.

# 📚 Data Sources
Price Data (Price.csv)
Description: Contains weekly closing prices and related metrics for crude oil.
Key Columns: Year, Week_Number, Close, Open, High, Low, Bid, Ask, Exchange Date, Price Score, various weekly return columns.

Inventory Data (Inventory.csv)
Description: Represents weekly inventory levels excluding Strategic Petroleum Reserve (SPR) stocks.
Key Columns: Year, Week_Number, Absolute Storage Score, Delta Inventory Score.

Commitment of Traders (COT) Data (COT.csv)
Description: Provides weekly COT reports indicating trader positions.
Key Columns: Year, Week_Number, Bullish_Bearish_Score, Delta_Score.

# 🧰 Technologies Used
Programming Language: Python 3.x
Libraries:
pandas: Data manipulation and analysis.
numpy: Numerical operations.
matplotlib: Data visualization.
Environment: Scripts are organized into modular Python files for clarity and reusability.

# 📑 Functionality Breakdown
1. Price Data Processing (price.py)
Function: process_price_data(df)

Cleans and parses the Exchange Date.
Aggregates data by Year and Week_Number.
Assigns a Score based on closing price thresholds:
Score = 1 if Close ≤ 68
Score = 0.5 if 68 < Close < 70
Score = 0 if Close ≥ 70
Calculates future weekly returns for various time horizons.
Function: extract_rows_by_score(merged_df, score, tolerance=1e-5)
Filters and extracts rows from the merged DataFrame based on a specified Total_Score.

2. Inventory Data Processing (inventory.py)
Function: process_inventory_data(df)

Cleans and parses dates.
Aggregates inventory data by Year and Week_Number.
Calculates scores based on inventory levels and changes.
Function: inventory_redacted(df)
Extracts specific columns (Week_Number, Absolute Storage Score, Delta Inventory Score) for streamlined analysis.

3. COT Data Processing (cot.py)
Function: process_cot_data(df)

Cleans and parses dates.
Aggregates COT data by Year and Week_Number.
Calculates scores based on trader positions and changes.

4. Data Merging and Scoring (main.py)
Function: merge_dataframes(price_df, inventory_df, cot_df)

Merges the processed Price, Inventory, and COT DataFrames based on Year and Week_Number.
Inserts score columns adjacent to the Price Score.
Calculates a Total_Score by summing individual scores.
Function: extract_rows_by_score(merged_df, score, tolerance=1e-5)
Extracts rows with a specific Total_Score for targeted analysis.

# 📂 Data Integrity and Cleaning
Handling Duplicates: The merging functions ensure that duplicate Year and Week_Number entries are aggregated by taking the mean, maintaining data consistency.
Error Handling: Functions include checks for missing columns and data inconsistencies, raising informative errors to guide debugging.
Data Validation: After processing, the data is validated to ensure accurate score assignments and merging.

# 🤝 Contributing
Contributions are welcome! If you'd like to enhance the project, feel free to open issues or submit pull requests. Whether it's adding new features, improving data processing, or enhancing documentation, your input is valuable.

# 📜 License
This project is licensed under the MIT License.
