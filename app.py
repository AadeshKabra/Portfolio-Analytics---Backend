from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from dotenv import load_dotenv
import os
import requests
from starlette.responses import JSONResponse
from urllib3 import request


def generate_token():
    url = "https://developer.hdfcsec.com/oapi/v1/login"
    params = {
        "api_key": HDFC_OPENAPI_KEY
    }
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36"
    }

    response = requests.get(url, headers=headers, params=params)
    return response.json()


def generate_otp(client_id, password, token_id):
    url = "https://developer.hdfcsec.com/oapi/v1/login/validate"
    params = {
        "api_key": HDFC_OPENAPI_KEY,
        "token_id": token_id
    }
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
        "Content-Type": "application/json"
    }
    data = {
        "username": client_id,
        "password": password
    }

    response = requests.post(url, headers=headers, params=params, json=data)
    return response.json()


def validate_OTP(otp, token_id):
    # print("TokenID: ", token_id)
    url = "https://developer.hdfcsec.com/oapi/v1/twofa/validate"
    params = {
        "api_key": HDFC_OPENAPI_KEY,
        "token_id": token_id
    }
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
        "Content-Type": "application/json"
    }
    data = {
        "answer": otp
    }

    response = requests.post(url, headers=headers, params=params, json=data)
    # print(response.status_code)
    return response.json()


def get_authorisation(token_id, request_token):
    url = "https://developer.hdfcsec.com/oapi/v1/authorise"
    params = {
        "api_key": HDFC_OPENAPI_KEY,
        "token_id": token_id,
        "consent": True,
        "request_token": request_token
    }
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                      "AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/123.0.0.0 Safari/537.36",
        "Content-Type": "application/json"
    }

    response = requests.get(url, headers=headers, params=params)
    return response.json()


def get_access_token(request_token):
    print("Secret: ", HDFC_OPENAPI_SECRET)
    url = "https://developer.hdfcsec.com/oapi/v1/access-token"
    params = {
        "api_key": HDFC_OPENAPI_KEY,  # Replace with your actual API key
        "request_token": request_token  # Replace with your actual request token
    }
    headers = {
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36"
    }
    data = {
        "apiSecret": HDFC_OPENAPI_SECRET  # Replace with your actual API secret
    }

    response = requests.post(url, params=params, headers=headers, json=data)

    # response = requests.post(url, headers=headers, params=params, json=data)
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

@app.get("/")
async def root():
    return {"Hello": "World"}


@app.post("/otp")
async def otp(payload: dict):
    print(payload)
    data = payload["params"]
    client_id = data["clientid"]
    password = data["password"]

    token_id = generate_token()["tokenId"]
    print(token_id)
    # TOKEN_ID = token_id
    otp = generate_otp(client_id, password, token_id)
    print(otp)

    # return JSONResponse({"response": "return"})
    # request_token = validateOTP(otp)

    if "error" in otp:
        return JSONResponse({"error": "Invalid Credentials. Please try again"})
    else:
        return JSONResponse({"tokenID": token_id})


@app.post("/login")
async def login(payload: dict):
    print("Login payload: ", payload)
    otp = payload["otp"]
    token_id = payload["tokenId"]

    request_token_json = validate_OTP(otp, token_id)
    print(request_token_json)
    request_token = request_token_json["requestToken"]
    print("Request Token: ", request_token)
    print("Request token generated")

    authorisation_json = get_authorisation(token_id, request_token)
    print(authorisation_json)
    request_token_new = authorisation_json["requestToken"]
    print("New Request Token: ", request_token_new)
    print("Authorisation Done")

    access_token_json = get_access_token(request_token_new)
    print(access_token_json)
    # access_token = access_token_json["accessToken"]

    return JSONResponse({"Data": "received"})


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
