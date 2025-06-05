import pandas as pd
from prophet import Prophet

class Detect:
    def __init__(self, value_columns, train_files):
        """
        :param value_columns: List of columns to model and detect anomalies on.
        :param train_files: List of 5 training file paths.
        """
        self.value_columns = value_columns
        self.train_files = train_files
        self.models = {}

    def load_and_prepare_data(self, files):
        dfs = []
        for file in files:
            df = pd.read_csv(file)
            df.columns = [col.strip() for col in df.columns]
            df['Hour'] = pd.to_datetime(df['Hour'])
            dfs.append(df)
        return pd.concat(dfs).sort_values('Hour').reset_index(drop=True)

    def train_models(self):
        train_df = self.load_and_prepare_data(self.train_files)
        for col in self.value_columns:
            df = train_df[['Hour', col]].rename(columns={'Hour': 'ds', col: 'y'})
            model = Prophet()
            model.fit(df)
            self.models[col] = model

    def detect_anomalies(self, test_file):
        test_df = pd.read_csv(test_file)
        test_df.columns = [col.strip() for col in test_df.columns]
        test_df['Hour'] = pd.to_datetime(test_df['Hour'])

        result_df = test_df.copy()

        for col in self.value_columns:
            test_data = test_df[['Hour', col]].rename(columns={'Hour': 'ds', col: 'y'})
            forecast = self.models[col].predict(test_data[['ds']])

            result_df[f'{col}_is_anomaly'] = (
                (test_data['y'] < forecast['yhat_lower']) |
                (test_data['y'] > forecast['yhat_upper'])
            )

        # Add a flag if any column is anomalous
        anomaly_flags = [f'{col}_is_anomaly' for col in self.value_columns]
        result_df['any_anomaly'] = result_df[anomaly_flags].any(axis=1)

        # Return only rows with anomalies
        return result_df[result_df['any_anomaly']]
