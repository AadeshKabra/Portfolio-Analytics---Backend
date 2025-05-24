from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from dotenv import load_dotenv
import os
import requests
from starlette.responses import JSONResponse, RedirectResponse
from kiteconnect import KiteConnect
from urllib3 import request


def get_holdings():

    url = "https://api.kite.trade/portfolio/holdings"
    headers = {
        "X-Kite-Version": "3",
        "Authorization": f"token {api_key}:{access_token}"
    }

    response = requests.get(url, headers=headers)
    print(response.status_code)
    return response.json()


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
HDFC_OPENAPI_KEY = os.getenv("HDFC_OPENAPI_KEY")
HDFC_OPENAPI_SECRET = os.getenv("HDFC_OPENAPI_SECRET")
FRONTEND_URL = os.getenv("FRONTEND_URL")

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

    # print(data["access_token"])
    # return JSONResponse({"accessToken": access_token})
    redirect_url = f"{FRONTEND_URL}/success?access_token={access_token}"
    return RedirectResponse(url=redirect_url)


@app.get("/holdings")
async def holdings():
    holdings = get_holdings()
    print(holdings)
    return JSONResponse({"holdings": holdings})


# @app.get("/stock_news")
# async def stock_news(stock: str):
#     print(stock)
#
#     news = get_stock_news(stock)
#     pass


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
