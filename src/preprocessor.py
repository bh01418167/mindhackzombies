import pandas as pd


class PreProcessor:
    def __init__(self):
        pass

    @staticmethod
    def normalize(df):
        """
        description: Normalize column names
        :param df:
        :return:
        """
        col_map = {
            'Amt': 'Amount', 'Value': 'Amount', 'TradeAmount': 'Amount',
            'TS': 'Timestamp', 'Time': 'Timestamp', 'TradeTime': 'Timestamp',
            'Org': 'Entity', 'Company': 'Entity', 'Client': 'Entity',
            'Item': 'Product', 'Asset': 'Product', 'Component': 'Product',
            'Risk_Score': 'RiskScore', 'Score': 'RiskScore', 'Risk': 'RiskScore'
        }
        return df.rename(columns={col: col_map.get(col, col) for col in df.columns})

    @staticmethod
    def preprocess(df):
        """
        description: Preprocess and derive metrics
        :param df:
        :return:
        """
        if 'Timestamp' in df.columns:
            df['Timestamp'] = pd.to_datetime(df['Timestamp'], errors='coerce')
            df = df.dropna(subset=['Timestamp'])
            df['Hour'] = df['Timestamp'].dt.floor('H')
        else:
            # If missing, use a default placeholder hour (e.g., first file's index or file-specific constant)
            df['Hour'] = pd.Timestamp('2025-01-01 00:00:00')

        # Amount
        if 'Amount' in df.columns:
            df['Amount'] = pd.to_numeric(df['Amount'], errors='coerce').fillna(0)
        else:
            df['Amount'] = 0

        # RiskScore
        if 'RiskScore' in df.columns:
            df['RiskScore'] = pd.to_numeric(df['RiskScore'], errors='coerce').fillna(0)
        else:
            df['RiskScore'] = 0

        # Latency
        if 'Latency(ms)' in df.columns:
            df['Latency(ms)'] = pd.to_numeric(df['Latency(ms)'], errors='coerce').fillna(1)
        else:
            df['Latency(ms)'] = 1

        # QoSWeight from QoS
        qos_map = {'High': 1.0, 'Medium': 0.5, 'Low': 0.2}
        if 'QoS' in df.columns:
            df['QoSWeight'] = df['QoS'].map(qos_map).fillna(0.1)
        else:
            df['QoSWeight'] = 0.1

        # DerivedWeight
        df['DerivedWeight'] = (
                df['Amount'] * df['QoSWeight'] * (1 + df['RiskScore']) / df['Latency(ms)']
        )
        return df