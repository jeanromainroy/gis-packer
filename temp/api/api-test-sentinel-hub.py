# importing the requests library
import requests
from oauthlib.oauth2 import BackendApplicationClient
from requests_oauthlib import OAuth2Session

# Your client credentials
client_id = '1422634d-ff4d-4e93-bf83-c19497a57f00'
client_secret = 'fW^+n~JOFP;9~Ph_]YLr9B.up@^QIL#KE0B{L7p9'

# Create a session
client = BackendApplicationClient(client_id=client_id)
oauth = OAuth2Session(client=client)

# Get token for the session
token = oauth.fetch_token(token_url='https://services.sentinel-hub.com/oauth/token',
                          client_id=client_id, client_secret=client_secret)

# All requests using this session will have an access token automatically added
resp = oauth.get("https://services.sentinel-hub.com/oauth/tokeninfo")
print(resp.content)


URL = 'https://services.sentinel-hub.com/api/v1/catalog/search'
headers = {"Authorization" : f"Bearer {token}"}
PARAMS = {
    "bbox":[11.86248779296875,41.48697733905992,13.135528564453127,42.309815415686664],
    "datetime":"2020-10-24T00:00:00.000Z/2020-11-03T23:59:59.999Z",
    "collections":[
        "sentinel-2-l2a"
    ],
    "limit":50,
    "query":{
        "eo:cloud_cover":{
            "lte":100
        }
    }
}

# sending get request and saving the response as response object
r = oauth.post(url=URL, json=PARAMS)

# extracting data in json format
data = r.json()

print(data)
