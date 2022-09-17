#Will pull down .json files for every asset in an asset group (or other query) and save them to be processed later
import json
import requests
import shutil
import os
import glob

#Set working directory as location of the script (run via CMD, not opening script directly)
wd = os.path.dirname(__file__)

#Set auth token. Loads from creds.key file next to script. Contents should be only "xxx/xxxxx..."
auth = open(wd + "\\creds.key").read().splitlines()[0]

#set JSON directory as a "JSON" folder one level deeper than the script file.
jsonPath = wd + "\\JSON\\"

##Widen Parameters (adjustable)
query = "ag:(pplus_key_art)" #Set query from Widen to use to target files.
expands = "metadata, asset_properties, file_properties, metadata_info" #The kinds of extra info to return with results in JSON form.
limit = 100 #The number of results to return with each scroll. Accepts numbers 1-100.

##Don't change. Combination of above parameters used to call the API.
apiURL = "https://api.widencollective.com/v2/assets/search?limit=" + str(limit) + "&expand=" + expands + "&query=" + query + "&scroll=true"
scrollApiURL = "https://api.widencollective.com/v2/assets/search/scroll?limit"+ str(limit) + "&expand=" + expands + "&query=" + query + "&scroll=true&scroll_id="

#GET from Widen using a query based on asset group metadata
#Scroll through results of 100 each and save each result as a .json file in a /JSON folder
headers = {'Authorization': 'Bearer ' + auth}
response = requests.get(apiURL, headers=headers).json()
totalFiles = response['total_count']
print(str(totalFiles) + " total .json files will be processed.")
scrollID = response['scroll_id']

count = 0
def dumpJSON(items):
    global count
    for item in items:
        count += 1
        filename = item['filename']
        print("Processing #" + str(count) + "/" + str(totalFiles) + " | " + str(filename))
        with open(wd + '\\JSON\\' + filename + '.json', 'w') as dumpfile:
            json.dump(item, dumpfile, indent = 4 )

def scrollSearch():
    global count
    scrollResponse = requests.get(scrollApiURL + scrollID, headers=headers).json()
    scrollItems = scrollResponse['items']
    dumpJSON(scrollItems)

dumpJSON(response['items']) #Dump first batch of .json files before the scroll search begins

while count < totalFiles: #Keep calling the API to get more results until we've processed the total number of results
    scrollSearch()
else:
    print(str(count) + " .json files have been processed out of " + str(totalFiles))
