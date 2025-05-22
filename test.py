# # from google import genai
# #
# #

# #
# # response = client.models.generate_content(
# #     model="gemini-2.0-flash",
# #     contents="Can you tell me what is the latest news about Tata Steel Share? Also date the news"
# # )
# #
# # print(response.text)
#
#
# # import logging
# # from kiteconnect import KiteConnect
# #
# #
# # logging.basicConfig(level=logging.DEBUG)
# #
# # kite =
#
# from SmartApi import SmartConnect
# import pyotp
# from logzero import logger
# import json
# import requests
#
#
# # smart_api = SmartConnect(api_key=api_key)
# import http.client
# import mimetypes
#
# conn = http.client.HTTPSConnection(" apiconnect.angelone.in ")
# payload = ''
# headers = {
#   'Authorization': 'Bearer AUTHORIZATION_TOKEN',
#   'Content-Type': 'application/json',
#   'Accept': 'application/json',
#   'X-UserType': 'USER',
#   'X-SourceID': 'WEB',
#   'X-ClientLocalIP': 'CLIENT_LOCAL_IP',
#   'X-ClientPublicIP': 'CLIENT_PUBLIC_IP',
#   'X-MACAddress': 'MAC_ADDRESS',
#   'X-PrivateKey': api_key
# }
# conn.request("GET","/rest/secure/angelbroking/portfolio/v1/getHolding", payload, headers)
#
# res = conn.getresponse()
# data = res.read()
# print(data.decode("utf-8"))

#
# import pyotp
# from SmartApi import SmartConnect
# from logzero import logger
#

#
# totp = pyotp.TOTP(totp_secret).now()
#
# smart_api = SmartConnect(api_key)
#
# token = smart_api.generateToken(username)
# session_data = smart_api.generateSession(username, password, totp)
# refresh_token = session_data["data"]["refreshToken"]
#
# smart_api.getProfile(refresh_token)
#
# profile = smart_api.getProfile(refresh_token)
# holdings = smart_api.holding()
# print(profile)
# print(holdings)
# print("----------------")
# print("----------------")
#
# for i in holdings["data"]:
#     print(i)

# try:
#     if session_data["status"]:
#         auth_token = session_data["data"]["jwtToken"]
#         feed_token = smart_api.getfeedToken()
#     else:
#         logger.error("Login Failed")
#
# except Exception as e:
#     logger.error("An error occured")


# HDFC_api = ""
# HDFC_api_secret = ""
#
#
# import requests
#
# url = "https://developer.hdfcsec.com/oapi/v1/login"
# params = {
#     "api_key": HDFC_api
# }
# headers = {
#     "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36"
# }
#
# response = requests.get(url, headers=headers, params=params)
#
# print("Status Code:", response.status_code)
# print("Response Text:", response.text)
# print(response.json()["tokenId"])
# tokenId = response.json()["tokenId"]
# # print(tokenId)
#
#
# url = "https://developer.hdfcsec.com/oapi/v1/login/validate"
# params = {
#     "api_key": HDFC_api,
#     "token_id": tokenId
# }
# headers = {
#     "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
#     "Content-Type": "application/json"
# }
# data = {
#     "username": "***",
#     "password": "***"
# }
#
# response = requests.post(url, headers=headers, params=params, json=data)
#
# print("Status Code:", response.status_code)
# print("Response:", response.json())



from kiteconnect import KiteConnect
import logging
import requests

logging.basicConfig(level=logging.DEBUG)



kite = KiteConnect(api_key=api_key)

print(kite.login_url())
response = requests.get(kite.login_url())
print(response.content)
# print(response.json())
print(response.status_code)

# request_token = "wTZq9uHh6eZZ7zLlfMmS0VK0z2WLSfgh"
#
# data = kite.generate_session(request_token=request_token, api_secret=api_secret)
# access_token = data["access_token"]
#
# print(access_token)
# kite.set_access_token(access_token)




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