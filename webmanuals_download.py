#!python3

import requests


manualId = 5563 # OMA

# Already URL encoded (%2C is comma)
base_url = 'https://babcock.webmanuals.aero'
ajax_base_url = base_url + '/tibet/template'
login_url = ajax_base_url + '/json%2CLoginUser.json'
manual_metadata_url = ajax_base_url + '/json%2Creader%2CPages.json'
page_url = ajax_base_url + '/Index.vm'


session = requests.Session()
session.headers.update({
    "Accept": "application/json, text/plain, */*",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept-Language": "en-GB,en;q=0.5"
    })

# Log in
response = session.get(base_url)
print(response)
print(response.cookies)

login_payload = {
    "acceptedTou": "true",
    "action": "LoginUser",
    "password": "gladd",
    "siteId": "1140",
    "username": "gladd"}
response = session.post(login_url, data=login_payload)
login_data = response.json()
print(response)
print("Site {} - isLoggedeIn: {}".format(login_data["siteId"], login_data["isLoggedIn"]))

# Get MetaData for manual
params={
    "manualId": str(manualId),
    "revision": "undefined"
    }
response = session.post(manual_metadata_url, params=params)
print(response)
manual_metadata = response.json()
manual_revision = manual_metadata["revisionName"]
for chapter in manual_metadata["chapters"]:
    print("Chapter {}".format(chapter["name"]))
    pages = chapter["pages"]
    for page in pages:
        # Both i and id are numeric values NOT strings
        print("{} {}".format(page["i"], page["id"]))

# Get page snipet
params ={
    "pageId": 285082,
    "layoutMode": "normal"
    }
response = session.get(page_url, params=params)
print(response)
print(response.text)

# TODO: save to file





