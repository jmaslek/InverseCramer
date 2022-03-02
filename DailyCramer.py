import re

import pandas as pd
import requests
import numpy as np
from bs4 import BeautifulSoup


cramer_link = "https://madmoney.thestreet.com/screener/index.cfm"
r = requests.get(cramer_link)
soup = BeautifulSoup(r.text, "html.parser")
table = soup.find_all("table")[0]
trs = table.find_all("tr")
recs = {
    "1": "Sell",
    "2": "Sell",
    "3": "Hold",
    "4": "Buy",
    "5": "Buy",
}

rec = []

for tr in trs[1:]:
    rec.append(recs[tr.find_all("td")[3].find("img")["src"][-5]])

df = pd.read_html("https://madmoney.thestreet.com/screener/index.cfm")[0]

df["Symbol"] = df.Company.apply(lambda x: re.findall(r"[\w]+", x)[-1])
df["Price"] = df.Price.apply(lambda x: float(x.strip("$")))
df = df.drop(columns=["Segment", "Call", "Portfolio"])
df["Recommendation"] = rec
df["Company"] = df.apply(lambda x: x.Company.replace(f"({x.Symbol})", ""), axis=1)
df["InverseCramer"] = df["Recommendation"].apply(lambda x: ["Buy", "Sell"][x == "Buy"])
date = df["Date"][0]

df.to_csv(f"daily/{date}.csv")


