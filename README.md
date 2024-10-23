# Crude Futures Sim Trading

Welcome to the Crude Oil Simulation Trading Project! This project leverages historical crude oil data to simulate trading strategies based on price movements, inventory levels, and Commitment of Traders (COT) reports. By integrating multiple data sources and applying a scoring system, this simulation aims to provide insights into potential trading opportunities and market sentiment.

## 📈 Project Overview
The Crude Oil Simulation Trading Project is designed to implement a discretionary trading strategy based on quantitative analysis on the crude oil futures market. By processing and merging data from various sources, the project assigns scores to each trading week, enabling the identification of bullish or bearish market conditions. This comprehensive analysis facilitates informed decision-making for simulated trading scenarios.

## 🧠 Trading Strategy Used
### Objective:<br>
Trade WTI Crude Oil Futures directionally with a 1-month (30 days) timeframe.<br>

### Key Components:<br>
1. Cost Curve (Price Support):<br>
- Utilize price support levels from the cost curve to identify optimal entry and exit points, ensuring trades are placed at strategic price levels.<br>

2. Inventory Levels:<br>
- Monitor weekly inventory data to assess supply and demand dynamics, using changes in inventory to anticipate potential price movements.<br>

3. CTA Positioning:<br>
- Analyze Commitment of Traders (COT) data to approximate the positioning of Commodity Trading Advisors (CTAs) or non-commercial traders, gauging market sentiment and crowd behavior to inform trading decisions.<br>

4. Geo-Political Events:<br>
- Incorporate recent news and geopolitical developments to contextualize market conditions, enhancing the decision-making process by accounting for external factors that may influence crude oil prices.<br>

## 📊Visualizations
### Crude Cost Curve
- Price floor/breakeven prices for crude production at different oil producing regions of the world.<br>
- Analysis based on data released by the EIA and Goldman Top Projects 2023: Back to growth.<br>
![Crude Cost Curve](images/crude_cost_curve.jpg)

### Inventory Levels Trailing 5/10 Years
- Comprehensive Analysis: Evaluates weekly U.S. crude oil reserves data published by the Energy Information Administration (EIA).<br>
- Demand Indicators: Lower inventory levels signify inventory draws, reflecting increased demand.<br>
- Seasonality Insights: Utilizes 5-year and 10-year averages to identify seasonal patterns in inventory levels.<br>
- Trend Visualization: The sinusoidal patterns observed in seasonality highlight consistent inventory reductions during summer and winter months, corresponding to heightened travel and heating demands, respectively.<br>
![Inventory Levels Trailing 5 Years](images/inventory_5yr.png)
![Inventory Levels Trailing 10 Years](images/inventory_10yr.png)

## 🛠️ Features
- Data Integration: Combines Price, Inventory, and COT data based on Year and Week_Number.<br>
- Scoring System: Assigns scores to each week based on price thresholds, inventory changes, and trader sentiment.<br>
- Total Score Calculation: Aggregates individual scores to provide an overall market sentiment indicator.<br>
- Data Filtering: Extracts specific rows based on total score values for targeted analysis.<br>
- Visualization: (Optional) Visualizes price movements and scores over time.<br>
- Automated Processing: Streamlines data cleaning, processing, and merging through modular Python scripts.<br>

## 📚 Data Sources
### Price Data (Price.csv)<br>
- Description: Contains weekly closing prices and related metrics for crude oil.<br>
- Key Columns: Year, Week_Number, Close, Open, High, Low, Bid, Ask, Exchange Date, Price Score, various weekly return columns.<br>

### Inventory Data (Inventory.csv)<br>
- Description: Represents weekly inventory levels excluding Strategic Petroleum Reserve (SPR) stocks.<br>
- Key Columns: Year, Week_Number, Absolute Storage Score, Delta Inventory Score.<br>

### Commitment of Traders (COT) Data (COT.csv)<br>
- Description: Provides weekly COT reports indicating trader positions.<br>
- Key Columns: Year, Week_Number, Bullish_Bearish_Score, Delta_Score.<br>

## 🧰 Technologies Used
### Programming Language: Python<br>
### Libraries:<br>
- pandas: Data manipulation and analysis.<br>
- numpy: Numerical operations.<br>
- matplotlib: Data visualization.<br>
- Environment: Scripts are organized into modular Python files for clarity and reusability.<br>

## 📑 Functionality Breakdown
### Price Data Processing (price.py)<br>
Function: process_price_data(df)<br>
- Cleans and parses the Exchange Date.<br>
- Aggregates data by Year and Week_Number.<br>
- Assigns a Score based on closing price thresholds:<br>
- Score = 1 if Close ≤ 68<br>
- Score = 0.5 if 68 < Close < 70<br>
- Score = 0 if Close ≥ 70<br>
- Calculates future weekly returns for various time horizons.<br>

### Inventory Data Processing (inventory.py)<br>
Function: process_inventory_data(df)<br>
- Cleans and parses dates.<br>
- Aggregates inventory data by Year and Week_Number.<br>
- Calculates scores based on inventory levels and changes.<br>

### COT Data Processing (cot.py)<br>
Function: process_cot_data(df)<br>
- Cleans and parses dates.<br>
- Aggregates COT data by Year and Week_Number.<br>
- Calculates scores based on trader positions and changes.<br>

### Data Merging and Scoring (main.py)<br>
Function: merge_dataframes(price_df, inventory_df, cot_df)<br>
- Merges the processed Price, Inventory, and COT DataFrames based on Year and Week_Number.<br>
- Inserts score columns adjacent to the Price Score.<br>
- Calculates a Total_Score by summing individual scores.<br>

## 📂 Data Integrity and Cleaning
Handling Duplicates: The merging functions ensure that duplicate Year and Week_Number entries are aggregated by taking the mean, maintaining data consistency.<br>
Error Handling: Functions include checks for missing columns and data inconsistencies, raising informative errors to guide debugging.<br>
Data Validation: After processing, the data is validated to ensure accurate score assignments and merging.<br>

## 🤝 Contributing
Contributions are welcome! If you'd like to enhance the project, feel free to open issues or submit pull requests. Whether it's adding new features, improving data processing, or enhancing documentation, your input is valuable.

## 📜 License
This project is licensed under the MIT License.
