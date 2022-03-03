import re
import os

import pandas as pd
import requests
import numpy as np
from bs4 import BeautifulSoup
from datetime import datetime
from pytz import timezone


now_date = datetime.now(timezone("EST")).date().strftime("%Y-%m-%d")

link = "https://madmoney.thestreet.com/screener/index.cfm?showview=stocks&showrows=500"
r = requests.post(link,
                  data=f"airdate={now_date}",
                  headers={"Content-Type": "application/x-www-form-urlencoded",
                           "User-Agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.3 Safari/605.1.15"})
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

df = pd.read_html(r.text)[0]

df["Symbol"] = df.Company.apply(lambda x: re.findall(r"[\w]+", x)[-1])
df["Price"] = df.Price.apply(lambda x: float(x.strip("$")))
df = df.drop(columns=["Segment", "Call", "Portfolio"])
df["Recommendation"] = rec
df["Company"] = df.apply(lambda x: x.Company.replace(f"({x.Symbol})", ""), axis=1)
df["InverseCramer"] = df["Recommendation"].apply(lambda x: ["Buy", "Sell"][x == "Buy"])
date = df["Date"][0].replace("/","-")

df.to_csv(f"daily/{date}.csv")

all_recs = pd.DataFrame()
for file in os.listdir("daily"):
    all_recs = pd.concat(
        [
        all_recs,
         pd.read_csv(f"daily/{file}", index_col=0)
         ]
    )
all_recs= all_recs.sort_values(by=["Date","Symbol"]).reset_index(drop=True)
all_recs.to_csv("AllRecommendations.csv")

