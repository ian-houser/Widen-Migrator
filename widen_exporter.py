#Will pull down .json files for every asset in an asset group (or other query) and save them to be processed by the widen_downloader script
#Version 0.3 2022/10/14 | Working | Added "Attached documents" functionality
#Next need to organize JSON files into sub-folders based on "Field Set" aka categories

import json
import requests
import os
from pathlib import Path
import sys

##Widen Parameters (adjustable)
query = "ag:{vcbs_cm_video_internal}" #Set query from Widen to use to target files- can use advanced searches including AND and OR. More info on advanced search queries: https://community.widen.com/collective/s/article/How-do-I-search-for-assets
expands = "asset_properties,file_properties,thumbnails,metadata,metadata_info,security" #The kinds of extra info to return with results in JSON form. https://widenv2.docs.apiary.io/#reference/expands
limit = 100 #The number of results to return with each scroll. Accepts numbers 1-100.

#Whether or not to check for attached documents on each asset and download the JSON
checkAttached = False

#Whether or not to organize JSON in to sub-folders based on their categories (field_set)
subOrganize =  True

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

#The first API request to ping API endpoint
response = requests.get(apiURL, headers=headers).json()
totalFiles = response['total_count']
print(str(totalFiles), "total .json files will be processed.")
scrollID = response['scroll_id']
filesizeCount = 0
dump_count = 0

#Function to write the JSON files of each item in the API call.
def dumpJSON(items):
    global dump_count
    global filesizeCount
    for item in items:
        dump_count += 1
        filesizeCount += item['file_properties']['size_in_kbytes']
        filename = item['filename']
        jsonFileName = filename + ".json" #extract just the file name from current JSON file for pathlib
        if subOrganize:
            dumpJsonPath = wd / item['metadata_info']['field_set'] / "JSON"
            if os.path.exists(dumpJsonPath) == False:
                os.makedirs((dumpJsonPath))
        else:
            dumpJsonPath = jsonPath
        print("Processing #", str(dump_count), "/", str(totalFiles), "|", str(filename))
        with open(dumpJsonPath / jsonFileName, 'w') as dump:
            json.dump(item, dump, indent = 4 )

#Function to check for attached documents using V1 of the API and send then to be dumped
def searchAttached(response):
    items = response['items']
    attached_count = 0
    print("++ Checking for attachments")
    for item in items:
        attached_count += 1
        attachedID = item['id'] #ID of the parent file to check for attachments
        attachedApiURL = "https://cbs.widencollective.com/api/rest/asset/uuid/" + attachedID + "?options=attachedDocs"#Attachments have to go to V1 endpoint
        attachedResponse = requests.get(attachedApiURL, headers=headers).json()
        print("Searching #", attached_count, "/", len(response['items']))
        if attachedResponse['attachedDocs']['docs']:#If we actually get an attachment
            items = attachedResponse['attachedDocs']['docs']
            attachment_list = []
            #print(items)
            print("+ Found", len(items), "for", attachedResponse['name'])
            for item in items:
                jsonFileName = item['title'] + ".json"
                parentJsonFilename = attachedResponse['name'] + ".json"
                metadataType = attachedResponse['metadataType']
                print("- Downloading", jsonFileName)
                #Schema to write in files. Important information included for making relationships between parents and children externally.
                childDump = {
                    "type": "attachment",
                    "id": item['uuid'],
                    "filename": item['title'],
                    "parent_ID": attachedID,
                    "parent_filename": attachedResponse['name'],
                    "download_URL": item['downloadUrl']
                }
                attachment_list.append(childDump) #Add our JSON to a list to return later
                if subOrganize:
                    dumpJsonPath = wd / metadataType / "JSON"
                else:
                    dumpJsonPath = jsonPath
                #Write our attachment JSON to files
                with open(dumpJsonPath / jsonFileName, 'w') as dump:
                    json.dump(childDump, dump)
                #Load parent JSON file to add      
                with open(dumpJsonPath / parentJsonFilename, 'r', encoding='utf-8') as readFile:
                    raw_data = readFile.read()
                    json_data = json.loads(raw_data)
                    json_data["attachments"] = attachment_list #Create new key in parent JSON with an array of attachments
                with open(dumpJsonPath / parentJsonFilename, 'w') as dump:
                    json.dump(json_data, dump, indent=4) #Write the list of attachments to parent JSON file        

#Function to continue the search using the scrolling API endpoint (as opposed to using offsets that are capped at 10k results)
def scrollSearch():
    response = requests.get(scrollApiURL + scrollID, headers=headers).json()
    scrollItems = response['items']
    dumpJSON(scrollItems)
    if checkAttached == True:
        searchAttached(response)

dumpJSON(response['items']) #Dump first batch of .json files before the scroll search begins

if checkAttached == True: #Check first batch from the response for attachments
    searchAttached(response)

while dump_count < totalFiles: #Keep calling the API to get more results until we've processed the total number of results
    scrollSearch()
else:
    print(str(dump_count), ".json files have been processed out of", str(totalFiles), "| Combined total file size (not including attachments due to API restrictions): " + str(filesizeCount) + " kbytes")