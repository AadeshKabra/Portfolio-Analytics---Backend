import pandas as pd
import yfinance as yf
import requests
from kiteconnect import KiteConnect
from dotenv import load_dotenv
import ast



holdings = [["AXISBANK", "NSE"], ["ETERNAL", "BSE"], ["IRFC", "NSE"], ["JIOFIN", "BSE"], ["LAURUSLABS", "NSE"],
            ["MARICO", "NSE"], ["TATAMOTORS", "NSE"], ["TATASTEEL", "BSE"], ["VEDL", "NSE"], ["YESBANK", "NSE"]]


df = pd.DataFrame(columns=['Date', 'Close', 'High', 'Low', 'Open', 'Volume', 'Ticker'])

for stock in holdings:
    ticker = ""
    if stock[1]=="BSE":
        ticker = stock[0] + ".BO"
    elif stock[1]=="NSE":
        ticker = stock[0] + ".NS"

    data = yf.download(ticker, period='30d', interval="1d")
    data = data.reset_index()
    data.columns = data.columns.get_level_values(0)
    data["Ticker"] = stock[0]
    # print(data.columns)
    # break
    df = pd.concat([df, data], ignore_index=True)

print(df)


