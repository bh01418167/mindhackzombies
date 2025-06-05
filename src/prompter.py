import warnings

import pandas as pd

from src.trade_tracer import TradeTracer


class Prompter:
    def __init__(self):
        aggregation_file_location = "./6g_liquidity_aggregation.csv"
        complete_file_location = "./full_trades_with_impact.csv"
        self.agg = pd.read_csv(aggregation_file_location)
        self.group_cols = ['Hour', 'Entity', 'Region', 'Product']
        self.complete_df = pd.read_csv(complete_file_location)
        self.trade_tracer = TradeTracer()

    def get_prompts(self):
        user_row = input("Enter row index to trace (or press Enter to skip): ")
        user_col = input("Enter column name to trace (e.g., AvgSHAPImpact): ")
        if user_row.strip() and user_col.strip():
            try:
                index = int(user_row)
                trace_df = self.trade_tracer.trace_cell_metric(
                    index, user_col.strip(), self.agg, self.complete_df, self.group_cols)
                if trace_df is not None:
                    print(trace_df.head())
            except ValueError:
                print("Invalid input.")

        print("Done. Aggregation with SHAP, sensitivity, and traceability complete.")


# Run
if __name__ == "__main__":
    warnings.filterwarnings("ignore")
    prompter = Prompter()
    prompter.get_prompts()