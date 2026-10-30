import pandas as pd
import os
from tools import Tool

class ExpenseAuditorTool(Tool):
    name = "expense_auditor"
    description = "Scans UPI transactions to find duplicate charges and spend surges. Pass the filename as input (e.g., 'upi_transactions_2024.csv')."

    def execute(self, filename: str = "upi_transactions_2024.csv") -> str:
        data_dir = os.environ.get("AGENTX_DATA_DIR", "data")
        filepath = os.path.join(data_dir, filename)
        
        if not os.path.exists(filepath):
            filepath = filename
            
        if not os.path.exists(filepath):
            return f"Error: Could not find dataset at {filepath}"

        try:
            df = pd.read_csv(filepath)
            sample_df = df.head(10000).copy()
            
            # Convert timestamp to just the date to find same-day duplicates
            sample_df['date'] = pd.to_datetime(sample_df['timestamp']).dt.date
            dupes = sample_df[sample_df.duplicated(subset=['amount (INR)', 'merchant_category', 'date'], keep=False)]
            
            dup_count = len(dupes)
            dup_example = dupes.iloc[0]['merchant_category'] if dup_count > 0 else "None"
            
            avg_amt = sample_df.groupby('merchant_category')['amount (INR)'].mean().to_dict()
            surges = 0
            surge_example = "None"
            
            for _, row in sample_df.iterrows():
                cat = row['merchant_category']
                amt = row['amount (INR)']
                if cat in avg_amt and amt > (avg_amt[cat] * 3) and amt > 1000:
                    surges += 1
                    if surge_example == "None":
                        surge_example = f"{cat} charge of ₹{amt} (Avg is ₹{avg_amt[cat]:.2f})"

            result = "--- Expense Audit Report ---\n"
            result += f"Total transactions scanned: {len(sample_df)}\n"
            result += f"Found {dup_count} potential duplicate transactions (Example: {dup_example}).\n"
            result += f"Found {surges} spend surges. (Example: {surge_example}).\n"
            result += "Recommendation: Cancel duplicates and adjust budget to save money."
            
            return result

        except Exception as e:
            return f"Error during audit: {str(e)}"