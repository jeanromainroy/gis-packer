# importing the requests library
import requests

username = 'jeanromainroy'
password = 'qi417721'

URL = 'https://scihub.copernicus.eu/dhus/search?start=0&rows=10&q=footprint:"Intersects(41.9000,12.5000)"'

# URL = 'https://services.sentinel-hub.com/api/v1/catalog/search'
# headers = {"Authorization" : f"Bearer {token}"}
# PARAMS = {
#     "bbox":[11.86248779296875,41.48697733905992,13.135528564453127,42.309815415686664],
#     "datetime":"2020-10-24T00:00:00.000Z/2020-11-03T23:59:59.999Z",
#     "collections":[
#         "sentinel-2-l2a"
#     ],
#     "limit":50,
#     "query":{
#         "eo:cloud_cover":{
#             "lte":100
#         }
#     }
# }

# sending get request and saving the response as response object
r = requests.get(url=URL)

# extracting data in json format
data = r.json()

print(data)
