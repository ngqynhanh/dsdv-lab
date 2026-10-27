"""Optional: download the unchanged historical JHU CSSE source CSV for local use.

Usage (from the examples folder): python download_original_csv.py
Requires Internet. This script does not alter or synthesize source records.
"""
from pathlib import Path
from urllib.request import urlretrieve
import csv

URL = (
    "https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/"
    "csse_covid_19_data/csse_covid_19_time_series/"
    "time_series_covid19_confirmed_global.csv"
)
out = Path("time_series_covid19_confirmed_global.csv")
urlretrieve(URL, out)
with out.open(encoding="utf-8-sig", newline="") as file:
    reader = csv.reader(file)
    headers = next(reader)
    count = sum(1 for row in reader)
print(f"Saved: {out.resolve()}")
print(f"Total rows: {count}; target 4/5/20 exists: {'4/5/20' in headers}")
print("Metadata columns:", headers[:4])
