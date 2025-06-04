class TradeTracer:
    def __init__(self):
        pass

    @staticmethod
    def trace_cell_metric(index, column, agg_df, df_all, group_cols):
        """
        description: Trace based on cell (row + column)
        :param index:
        :param column:
        :param agg_df:
        :param df_all:
        :param group_cols:
        :return:
        """
        if index < 0 or index >= len(agg_df):
            print("Invalid row index.")
            return None
        if column not in agg_df.columns:
            print("Invalid column name.")
            return None

        row = agg_df.iloc[index]
        filters = {col: row[col] for col in group_cols}
        filtered = df_all.copy()
        for col, val in filters.items():
            filtered = filtered[filtered[col] == val]

        print(f"Cell value for '{column}' at row {index}: {row[column]}")
        print(f"Found {len(filtered)} contributing trade rows for this cell.")
        return filtered