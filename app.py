from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from dotenv import load_dotenv
import os
import requests
from starlette.responses import JSONResponse, RedirectResponse
from kiteconnect import KiteConnect
from serpapi import GoogleSearch
from datetime import datetime
import yfinance as yf
from pinecone import Pinecone
from sentence_transformers import SentenceTransformer
from google import genai
import pandas as pd
from google.genai import types
from concurrent.futures import ThreadPoolExecutor
import itertools


def get_holdings():
    url = "https://api.kite.trade/portfolio/holdings"
    headers = {
        "X-Kite-Version": "3",
        "Authorization": f"token {api_key}:{access_token}"
    }

    response = requests.get(url, headers=headers)

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
    results = search.get_dict()

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

    return historical_data


def get_company_ticker(company_name):
    url = f"https://www.nseindia.com/api/search/autocomplete"
    params = {'q': company_name}
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }

    try:
        response = requests.get(url, params=params, headers=headers)
        data = response.json()
        return data.get('symbols', [])
    except:
        return []


def get_formatted_dataframe(df, type=None):
    df = df.reset_index()
    if type == "dividend":
        df["Dividend_Date"] = df["Date"].dt.date
        df = df.drop('Date', axis=1)
    else:
        df = df.replace({float('nan'): None})
        df.columns = [col.strftime('%Y-%m-%d') if isinstance(col, pd.Timestamp) else col for col in df.columns]

    return df


def prepare_docs(df, stock_ticker, type=None):
    rows = len(df)
    columns = df.columns
    text_data = []
    metadata = []
    if type == "dividend":
        for row in range(rows):
            if df.loc[row, 'Dividends'] is not None:
                text = f"On {df.loc[row, 'Dividend_Date']} the dividend given was {df.loc[row, 'Dividends']}"
                text_data.append(text)

                metadata_doc = {
                    "financial_item": "Dividend",
                    "date": str(df.loc[row, 'Dividend_Date']),
                    "value": float(df.loc[row, 'Dividends']),
                    "stock ticker": stock_ticker
                }
                metadata.append(metadata_doc)

    else:
        for row in range(rows):
            for col in range(1, len(columns)):
                if df.iloc[row, col] is not None:
                    text = f"As on {columns[col]}, the {df['index'].iloc[row]} for {stock_ticker} is {df.iloc[row, col]}"
                    text_data.append(text)

                    metadata_doc = {
                        "financial_item": df['index'].iloc[row],
                        "date": columns[col],
                        "value": float(df.iloc[row, col]),
                        "stock ticker": stock_ticker
                    }
                    metadata.append(metadata_doc)


    return text_data, metadata


def prepare_vectors(text_data, metadata, model, stock_ticker, description):
    vectors = []
    for (index, text) in enumerate(text_data):
        vectorized_text = model.encode(text).tolist()

        metadata_text = metadata[index]

        vectors.append({
            "id": f"{stock_ticker}_{description}_{index}",
            "values": vectorized_text,
            "metadata": metadata_text
        })

    return vectors


def process_chunk(df, stock_ticker, model, chunk_name, prepare_type=None):
    df = get_formatted_dataframe(df, type=prepare_type) if prepare_type else get_formatted_dataframe(df)
    text_data, metadata = prepare_docs(df, stock_ticker, prepare_type if prepare_type else chunk_name)
    vectors = prepare_vectors(text_data, metadata, model, stock_ticker, chunk_name)
    print(f"{chunk_name.replace('_', ' ').title()} done")
    return vectors


def add_vectors_to_pinecone(vectors, batch_size):
    for i in range(0, len(vectors), batch_size):
        batch = vectors[i: i + batch_size]
        index.upsert(vectors=batch, namespace=namespace)


def get_prompt(query, results, stock_ticker):
    prompt = f"""
        Please answer the following question about {stock_ticker} based on the context provided. Also try to mention the timeframe for which you have the data to 
        make the user understand the answer more efficiently.
        Question: {query}
        Context: {results}
    """

    return prompt


def chunked(iterable, batch_size):
    it = iter(iterable)
    while chunk := tuple(itertools.islice(it, batch_size)):
        yield chunk


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

# Zerodha Configuration
api_key = os.getenv("ZERODHA_API_KEY")
api_secret = os.getenv("ZERODHA_API_SECRET")
kite = KiteConnect(api_key=api_key)
access_token = ""

# Pinecone Configuration
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
pinecone = Pinecone(api_key=PINECONE_API_KEY)
index_name = os.getenv("PINECONE_INDEX_NAME")
index = pinecone.Index(host=os.getenv("PINECONE_INDEX_HOST"))
namespace = "test"

model = SentenceTransformer('all-mpnet-base-v2')
stock_ticker = None

# Gemini Configuration
gemini_client = genai.Client(api_key=GEMINI_API_KEY)

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
    # print(holdings["data"])
    return {"holdings": holdings}


@app.get("/stock_news")
async def stock_news(stock: str):
    # print("Reached stock news")
    news = get_stock_news(stock)
    return JSONResponse({"News": news})


@app.get("/stock_history")
async def stock_history(stock: str):
    historical_data = get_historical_data(stock)
    return JSONResponse({"historicalData": historical_data})


@app.get("/sector_pie_chart")
async def sector_pie_chart():
    holdings = get_holdings()
    # print(holdings)
    return JSONResponse({"Return": "Yes"})


@app.get("/stock-search")
async def stock_search(stock: str):
    # print("Reached stock search")
    company_ticker = get_company_ticker(stock)
    # print(company_ticker)

    company_names = []
    for option in company_ticker:
        company_names.append([option["symbol"], option["symbol_info"]])

    return JSONResponse({"companyNames": company_names})


@app.get("/stock-research")
async def stock_research(stockTicker: str):
    global pinecone_index

    stock = yf.Ticker(stockTicker+".BO")
    stock_info = stock.info

    stock_price_json = {}
    all_vectors = []

    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = []

        futures.append(executor.submit(process_chunk, stock.financials, stockTicker, model, "financials"))
        futures.append(executor.submit(process_chunk, stock.financials, stockTicker, model, "income_stmt"))
        futures.append(executor.submit(process_chunk, stock.financials, stockTicker, model, "balance_sheet"))

        for future in futures:
            vectors = future.result()
            all_vectors += vectors


    dividends_df = stock.dividends
    dividends_df = get_formatted_dataframe(dividends_df, type="dividend")
    text_data, metadata = prepare_docs(dividends_df, stockTicker, "dividend")
    vectors = prepare_vectors(text_data, metadata, model, stockTicker, "dividend")
    all_vectors += vectors
    # add_vectors_to_pinecone(vectors, batch_size=100)
    print("Dividends done")

    print(len(all_vectors))
    # print(all_vectors)
    # all_vectors = set(all_vectors)
    # print(len(all_vectors))

    # print(index.list_namespaces())
    namespaces = [i.name for i in index.list_namespaces()]
    if namespace in namespaces:
        index.delete(delete_all=True, namespace=namespace)
        print("Old namespace deleted")


    with ThreadPoolExecutor(max_workers=4) as executor:
        executor.submit(add_vectors_to_pinecone, all_vectors[:200], 200)
        executor.submit(add_vectors_to_pinecone, all_vectors[200:400], 200)
        executor.submit(add_vectors_to_pinecone, all_vectors[400:600], 200)
        executor.submit(add_vectors_to_pinecone, all_vectors[600:], 200)

    print("Upserting completed")

    return JSONResponse({"stockInfo": stock_info, "stockPrice": stock_price_json})


@app.get("/stock-chatbot-query")
async def stock_chatbot_query(query: str, stock: str):
    query_encoded = model.encode(query).tolist()
    results = index.query(vector=query_encoded, namespace=namespace, top_k=10, include_metadata=True)
    print(results)
    prompt = get_prompt(query, results, stock)

    response = gemini_client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
        config=types.GenerateContentConfig(
            temperature=0.5,
            system_instruction="You are a chatbot developed for answering questions about indian stocks along with their technicals and fundamental information. Your name is Neko."
        )
    )
    # print(response.text)
    return JSONResponse({"response": response.text})


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)


# financials_df = stock.financials
# financials_df = get_formatted_dataframe(financials_df)
# text_data, metadata = prepare_docs(financials_df, stockTicker)
# vectors = prepare_vectors(text_data, metadata, model, stockTicker, "financials")
# all_vectors += vectors
# # add_vectors_to_pinecone(vectors,  batch_size=100)
# print("Financials done")
#
# income_stmt_df = stock.income_stmt
# income_stmt_df = get_formatted_dataframe(income_stmt_df)
# text_data, metadata = prepare_docs(income_stmt_df, stockTicker)
# vectors = prepare_vectors(text_data, metadata, model, stockTicker, "income_stmt")
# all_vectors += vectors
# # add_vectors_to_pinecone(vectors, batch_size=100)
# print("Income Statement done")
#
# balance_sheet_df = stock.balance_sheet
# balance_sheet_df = get_formatted_dataframe(balance_sheet_df)
# text_data, metadata = prepare_docs(balance_sheet_df, stockTicker)
# vectors = prepare_vectors(text_data, metadata, model, stockTicker, "balance_sheet")
# all_vectors += vectors
# # add_vectors_to_pinecone(vectors, batch_size=100)
# print("Balance Sheet done")
#


