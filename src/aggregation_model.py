import pandas as pd
import shap
from sklearn.ensemble import GradientBoostingRegressor


class AggregationModel:
    def __init__(self):
        pass

    @staticmethod
    def model_with_shap(df, features, target):
        """
        description: Train model and compute SHAP values
        :param df:
        :param features:
        :param target:
        :return:
        """
        model = GradientBoostingRegressor()
        df = df.dropna(subset=features + [target])
        model.fit(df[features], df[target])
        explainer = shap.Explainer(model, df[features])
        shap_values = explainer(df[features])
        return shap_values, df

    def calculate_shap_impact(self, df_all):
        features = ['Amount', 'RiskScore', 'QoSWeight', 'Latency(ms)', 'DerivedWeight']
        target = 'Amount'

        print("Training model and calculating SHAP values...")
        shap_values, df_model = self.model_with_shap(df_all.copy(), features, target)
        shap_df = pd.DataFrame(shap_values.values, columns=features)
        shap_df['TradeID'] = df_model['TradeID'].values
        shap_df['SHAP_Impact'] = shap_df[features].abs().sum(axis=1)
        shap_df.to_csv("./shap_trade_impact.csv", index=False)
        return shap_df

    @staticmethod
    def leave_one_out_sensitivity(df, group_cols, metric):
        """
        description: Sensitivity Analysis
        :param df:
        :param group_cols:
        :param metric:
        :return:
        """
        sensitivity_series = pd.Series(index=df.index, dtype=float)
        grouped = df.groupby(group_cols)

        for _, group in grouped:
            baseline = group[metric].sum()
            for idx in group.index:
                temp_group = group.drop(index=idx)
                new_score = temp_group[metric].sum()
                impact = baseline - new_score
                sensitivity_series.at[idx] = impact

        return sensitivity_series