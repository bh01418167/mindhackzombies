import logging
import warnings

from src.aggregation_model import AggregationModel
from src.preprocessor import PreProcessor
import pandas as pd
import glob
import os


class Aggregator:
    input_dir = "./generated_trade_files"
    output_agg_file_location = "./6g_liquidity_aggregation.csv"
    complete_file_location = "./full_trades_with_impact.csv"

    def __init__(self):
        logging.info("input dir:::", self.input_dir)
        logging.info("output_agg_file_location:::", self.output_agg_file_location)
        logging.info("complete_file_location:::", self.complete_file_location)
        self.aggregation_model = AggregationModel()
        self.preprocessor = PreProcessor()
        self.group_cols = ['Hour', 'Entity', 'Region', 'Product']

    def produce_aggregation_file(self):

        dfs = self.__load_data()
        dfs = [self.preprocessor.normalize(df) for df in dfs]
        df_all = pd.concat([self.preprocessor.preprocess(df) for df in dfs], ignore_index=True)
        logging.info("Aggregating with derived metrics and model impact...")

        print("Aggregating with derived metrics and model impact...")
        shap_df = self.aggregation_model.calculate_shap_impact(df_all)
        shap_impact_map = shap_df.groupby('TradeID')['SHAP_Impact'].mean()
        df_all['SHAP_Impact'] = df_all['TradeID'].map(shap_impact_map).fillna(0)
        agg = df_all.groupby(self.group_cols).agg(
            TotalAmount=('Amount', 'sum'),
            AvgDerivedWeight=('DerivedWeight', 'mean'),
            AvgSHAPImpact=('SHAP_Impact', 'mean'),
            TradeCount=('TradeID', 'count')
        ).reset_index()

        logging.info("Performing leave-one-out sensitivity analysis...")
        print("Performing leave-one-out sensitivity analysis...")
        df_all['LOOImpact'] = self.aggregation_model.leave_one_out_sensitivity(
            df_all, self.group_cols, 'DerivedWeight')

        print("Saving final enriched report...")
        agg.to_csv(self.output_agg_file_location, index=False)
        df_all.to_csv(self.complete_file_location, index=False)

    @classmethod
    def __load_data(cls):
        files = glob.glob(os.path.join(cls.input_dir, '*.csv'))
        dfs = []
        for f in files:
            df = pd.read_csv(f)
            df['SourceFile'] = os.path.basename(f)
            dfs.append(df)
        logging.info("Loaded data...")
        logging.info(dfs)
        return dfs


if __name__ == "__main__":
    warnings.filterwarnings("ignore")
    aggregator = Aggregator()
    aggregator.produce_aggregation_file()