# # from google import genai
# #
# #
# # client = genai.Client(api_key="AIzaSyD7yNhzXeVZOVdMU2_oSIsWLaLuDRNFn54")
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


# import pyotp
# from SmartApi import SmartConnect
# from logzero import logger
#
# api_key = "pnkeIRyP"
# username = "S783069"
# password = "2468"
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


HDFC_api = ""
HDFC_api_secret = ""


import requests

url = "https://developer.hdfcsec.com/oapi/v1/login"
params = {
    "api_key": HDFC_api
}
headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36"
}

response = requests.get(url, headers=headers, params=params)

print("Status Code:", response.status_code)
print("Response Text:", response.text)
print(response.json()["tokenId"])
tokenId = response.json()["tokenId"]
# print(tokenId)


url = "https://developer.hdfcsec.com/oapi/v1/login/validate"
params = {
    "api_key": HDFC_api,
    "token_id": tokenId
}
headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    "Content-Type": "application/json"
}
data = {
    "username": "***",
    "password": "***"
}

response = requests.post(url, headers=headers, params=params, json=data)

print("Status Code:", response.status_code)
print("Response:", response.json())