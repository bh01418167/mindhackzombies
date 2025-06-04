import pandas as pd
import numpy as np
import os
import random
import uuid
from datetime import datetime, timedelta

# Configuration
OUTPUT_DIR = "./generated_trade_files"
NUM_FILES = 14
ROWS_PER_FILE = 5000
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Master column functions
column_generators = {
    'TradeID': lambda: str(uuid.uuid4()),
    'Timestamp': lambda: (datetime(2025, 1, 1) + timedelta(minutes=random.randint(0, 43200))).strftime('%Y-%m-%d %H:%M:%S'),
    'Amount': lambda: round(random.uniform(1000, 100000), 2),
    'Entity': lambda: random.choice(['USA', 'IND', 'UK', 'GER', 'JPN']),
    'Product': lambda: random.choice(['6G-Core', '6G-Antenna', '6G-Node', '6G-Chip']),
    'Category': lambda: random.choice(['Hardware', 'Software', 'Service']),
    'Region': lambda: random.choice(['APAC', 'EMEA', 'NA']),
    'Channel': lambda: random.choice(['Direct', 'Reseller', 'Online']),
    'RiskScore': lambda: round(random.uniform(0, 1), 3),
    'Volume': lambda: random.randint(1, 100),
    'Latency(ms)': lambda: round(random.uniform(0.1, 5.0), 2),
    'QoS': lambda: random.choice(['High', 'Medium', 'Low']),
    'TradeStatus': lambda: random.choice(['Executed', 'Pending', 'Failed']),
    'CounterParty': lambda: random.choice(['VendorA', 'VendorB', 'VendorC']),
    'Currency': lambda: random.choice(['USD', 'EUR', 'INR', 'JPY']),
    'ExchangeRate': lambda: round(random.uniform(0.5, 1.5), 3),
    'TradeType': lambda: random.choice(['Spot', 'Forward', 'Option']),
    'SettlementDays': lambda: random.randint(1, 5),
    'BrokerFee': lambda: round(random.uniform(10, 1000), 2)
}

# Column name variations
alias_map = {
    'Amount': ['Amt', 'TradeAmount', 'Value'],
    'Timestamp': ['TS', 'TradeTime'],
    'Entity': ['Org', 'Company', 'Client'],
    'Product': ['Item', 'Asset', 'Component'],
    'RiskScore': ['Score', 'Risk', 'Risk_Score']
}

# Generate one file
def generate_file(index):
    cols = list(column_generators.keys())
    selected_cols = random.sample(cols, random.randint(18, len(cols)))

    # Randomly rename some columns
    renamed = {}
    for col in selected_cols:
        if col in alias_map and random.random() > 0.5:
            renamed[random.choice(alias_map[col])] = column_generators[col]
        else:
            renamed[col] = column_generators[col]

    data = {k: [func() for _ in range(ROWS_PER_FILE)] for k, func in renamed.items()}
    df = pd.DataFrame(data)

    # Occasionally drop Timestamp column to simulate missing
    if 'Timestamp' in df.columns and random.random() < 0.2:
        df.drop(columns=['Timestamp'], inplace=True)

    file_path = os.path.join(OUTPUT_DIR, f"trade_file_{index}.csv")
    df.to_csv(file_path, index=False)
    print(f"Generated {file_path} with {len(df.columns)} columns")

# Generate all files
for i in range(1, NUM_FILES + 1):
    generate_file(i)