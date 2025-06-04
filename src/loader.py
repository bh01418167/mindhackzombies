import os
import xml.etree.ElementTree as ET

import camelot
import pandas as pd
import tabula


def file_extension(filename):
    return os.path.splitext(filename)[1].lower()


def read_pdf(file_path):
    # Try extracting all tables and concatenating
    try:
        dfs = tabula.read_pdf(file_path, pages='all', multiple_tables=True)
        return pd.concat(dfs, ignore_index=True)
    except Exception as e:
        print(e)
        tables = camelot.read_pdf(file_path, pages='all')
        dfs = [table.df for table in tables]
        return pd.concat(dfs, ignore_index=True)


def read_xlsx(file_path):
    return pd.read_excel(file_path)


def read_csv(file_path):
    return pd.read_csv(file_path)


def read_xml(file_path):
    tree = ET.parse(file_path)
    root = tree.getroot()
    # Assuming a "row" structure. Adjust as needed.
    rows = []
    columns = []
    for item in root:
        row = {}
        for child in item:
            row[child.tag] = child.text
            columns.append(child.tag)
        rows.append(row)
    return pd.DataFrame(rows, columns=columns)


def read_json(file_path):
    return pd.read_json(file_path)


def read_html(file_path):
    dfs = pd.read_html(file_path)
    return pd.concat(dfs, ignore_index=True)


def convert_to_standardized_csv(file_path, output_csv):
    ext = file_extension(file_path)
    if ext == '.pdf':
        df = read_pdf(file_path)
    elif ext in ['.xls', '.xlsx']:
        df = read_xlsx(file_path)
    elif ext == '.csv':
        df = read_csv(file_path)
    elif ext == '.xml':
        df = read_xml(file_path)
    elif ext == '.json':
        df = read_json(file_path)
    elif ext == '.html' or ext == '.htm':
        df = read_html(file_path)
    else:
        raise ValueError("Unsupported file format: {}".format(ext))
        # Clean columns names, strip whitespace, etc.
    df.columns = [str(col).strip() for col in df.columns]
    df.to_csv(output_csv, index=False)
    print(df)


convert_to_standardized_csv("../data/balance_sheet_csv.csv", "./output/csv_converted.csv")
convert_to_standardized_csv("../data/balance_sheet_xlsx.xlsx", "./output/xlsx_converted.csv")
convert_to_standardized_csv("../data/balance_sheet_xml.xml", "./output/xml_converted.csv")
convert_to_standardized_csv("../data/balance_sheet_html.html", "./output/html_converted.csv")
convert_to_standardized_csv("../data/balance_sheet_json.json", "./output/json_converted.csv")
convert_to_standardized_csv("../data/balance_sheet_pdf.pdf", "./output/pdf_converted.csv")