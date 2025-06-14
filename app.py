from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from dotenv import load_dotenv
import os
import requests
from starlette.responses import JSONResponse, RedirectResponse
from kiteconnect import KiteConnect
from urllib3 import request
from serpapi import GoogleSearch
from datetime import datetime
import pandas as pd


def get_holdings():
    url = "https://api.kite.trade/portfolio/holdings"
    headers = {
        "X-Kite-Version": "3",
        "Authorization": f"token {api_key}:{access_token}"
    }

    response = requests.get(url, headers=headers)
    # print(response.status_code)
    return response.json()


def get_stock_news(stock):
    params = {
        "engine": "google_news",
        "q": stock + " Stock",
        "api_key": GOOGLE_SERPAPI_KEY,
        "hl": "en",
        "gl": "in"
    }
    search = GoogleSearch(params)
    results =search.get_dict()

    date_format = "%m/%d/%Y, %I:%M %p, %z UTC"
    news = results["news_results"]
    news_filtered = [i for i in news if "date" in i]
    sorted_news = sorted(news_filtered, key=lambda x: datetime.strptime(x["date"], date_format), reverse=True)
    return sorted_news


def get_historical_data(stock, time_period="1m"):
    url = "https://stock.indianapi.in/historical_data"

    querystring = {"stock_name": stock, "period": time_period, "filter": "price"}
    headers = {"X-Api-Key": INDIAN_STOCK_API_KEY}

    response = requests.get(url, headers=headers, params=querystring)

    historical_data = response.json()["datasets"][0]["values"]
    # print(historical_data)
    # print(response.json())
    return historical_data


app = FastAPI()

origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
FRONTEND_URL = os.getenv("FRONTEND_URL")
GOOGLE_SERPAPI_KEY = os.getenv("GOOGLE_SERPAPI_KEY")
INDIAN_STOCK_API_KEY = os.getenv("INDIAN_STOCK_API_KEY")

api_key = os.getenv("ZERODHA_API_KEY")
api_secret = os.getenv("ZERODHA_API_SECRET")
kite = KiteConnect(api_key=api_key)
access_token = ""

@app.get("/")
async def root():
    return {"Hello": "World"}


@app.get("/login")
async def login():
    login_url = kite.login_url()
    return RedirectResponse(url=login_url)


@app.get("/kite/callback")
async def kite_callback(request: Request):
    global access_token

    request_token = request.query_params.get("request_token")
    print(request_token)
    data = kite.generate_session(request_token, api_secret=api_secret)
    kite.set_access_token(data["access_token"])
    access_token = data["access_token"]

    redirect_url = f"{FRONTEND_URL}/success?access_token={access_token}"
    return RedirectResponse(url=redirect_url)


@app.get("/holdings")
async def holdings():
    holdings = get_holdings()
    # print(holdings)
    return {"holdings": holdings}


@app.get("/stock_news")
async def stock_news(stock: str):
    print("Reached stock news")
    news = get_stock_news(stock)
    return JSONResponse({"News": news})


@app.get("/stock_history")
async def stock_history(stock: str):
    historical_data = get_historical_data(stock)
    return JSONResponse({"historicalData": historical_data})


@app.get("/sector_pie_chart")
async def sector_pie_chart():
    holdings = get_holdings()
    print(holdings)
    return JSONResponse({"Return": "Yes"})


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
