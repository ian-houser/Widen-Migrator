#Will pull down .json files for every asset in an asset group (or other query) and save them to be processed by the widen_downloader script
#Version 0.21 2022/09/21 | working

import json
import requests
import os
from pathlib import Path
import sys

##Widen Parameters (adjustable)
query = "ag:{vcbs_cm_design_internal}" #Set query from Widen to use to target files- can use advanced searches including AND and OR. More info on advanced search queries: https://community.widen.com/collective/s/article/How-do-I-search-for-assets
expands = "asset_properties,file_properties,thumbnails,metadata,metadata_info,security" #The kinds of extra info to return with results in JSON form. https://widenv2.docs.apiary.io/#reference/expands
limit = 100 #The number of results to return with each scroll. Accepts numbers 1-100.

#Set working directory as location of the script (run via CMD, not opening script directly)
wd = Path(os.path.realpath(os.path.dirname(__file__)))

#Set auth token. Loads from creds.key file next to script. Contents should be only "xxx/xxxxx..."
if os.path.exists(wd / "creds.key") == False:
    print("No credential file found! Make a 'creds.key' file next to the script with only your Widen API token inside | 'xxx/xxxxx...'")
    sys.exit()
auth = open(wd / "creds.key").read().splitlines()[0]

#set JSON directory as a "JSON" folder one level deeper than the script file.
jsonPath = wd / "JSON"

#Check if our file path exists and create them if necessary
if os.path.exists(jsonPath) == False:
    os.mkdir((jsonPath))

##Don't change. Combination of above parameters used to call the API.
apiURL = "https://api.widencollective.com/v2/assets/search?limit=" + str(limit) + "&expand=" + expands + "&query=" + query + "&scroll=true"
scrollApiURL = "https://api.widencollective.com/v2/assets/search/scroll?" + "&expand=" + expands + "&query=" + query + "&scroll=true&scroll_id="

#GET from Widen using a query based on asset group metadata
#Scroll through results of 100 each and save each result as a .json file in a /JSON folder
headers = {'Authorization': 'Bearer ' + auth}
response = requests.get(apiURL, headers=headers).json()
totalFiles = response['total_count']
print(str(totalFiles), "total .json files will be processed.")
scrollID = response['scroll_id']

filesizeCount = 0
count = 0
def dumpJSON(items):
    global count
    global filesizeCount
    for item in items:
        count += 1
        filesizeCount += item['file_properties']['size_in_kbytes']
        filename = item['filename']
        print("Processing #", str(count), "/", str(totalFiles), "|", str(filename))
        jsonFileName = filename + ".json" #extract just the file name from current JSON file for pathlib
        with open(jsonPath / jsonFileName, 'w') as dumpfile:
            json.dump(item, dumpfile, indent = 4 )

def scrollSearch():
    scrollResponse = requests.get(scrollApiURL + scrollID, headers=headers).json()
    scrollItems = scrollResponse['items']
    dumpJSON(scrollItems)

dumpJSON(response['items']) #Dump first batch of .json files before the scroll search begins

while count < totalFiles: #Keep calling the API to get more results until we've processed the total number of results
    scrollSearch()
else:
    print(str(count), ".json files have been processed out of", str(totalFiles), "| Combined total file size (actual download files, not JSON): " + str(filesizeCount) + " kbytes")