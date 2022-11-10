#Looks through a folder of .json files generated from Widen and downloads the original file for each.
#Version 0.32 2022/11/9 | working | Added functionality to update Widen metadata for each downloaded asset. Meant to assist in tracking which assets have been downloaded in Widen.

import json
import requests
import shutil
import os
import glob
import sys
from pathlib import Path
from datetime import date #Only used to update metadata in Widen with 'migrated' date of Today()
import time


##Editable
#The kinds of extra info to return with results in JSON form. https://widenv2.docs.apiary.io/#reference/expands
expands = "metadata, asset_properties, file_properties, metadata_info" 
#The JSON body (as a string) to send back to Widen after the asset has been updated. Initial intent is adding a date to "migrationDate" to indicate when and that it has been downloaded | https://widenv2.docs.apiary.io/#reference/assets/asset-metadata/update-metadata
update_body = '{"fields": {"migrationDate": [' + str(date.today()) + ']}}'
update_metadata = True #Set this to False to skip updating metadata of the downloaded asset

#Sets working directory as location of the script
wd = Path(os.path.realpath(os.path.dirname(__file__)))

#Set auth token. Loads from creds.key file next to script. Contents should be only "xxx/xxxxx..."
if os.path.exists(wd / "creds.key") == False:
    print("No credential file found! Make a 'creds.key' file next to the script with only your Widen API token inside | 'xxx/xxxxx...'")
    sys.exit()
auth = open(wd / "creds.key").read().splitlines()[0]

#sets JSON directory as a "JSON" folder one level deeper than the script file.
jsonPath = wd / "JSON"
#sets destination for saved file. Set to working directory
destination = wd / "downloaded"

#Check if our file paths exist and create them if necessary
if os.path.exists(jsonPath / "processed") == False:
    os.makedirs((jsonPath / "processed"))
if os.path.exists(destination) == False:
    os.mkdir(destination)

#Processing count tracker
totalFiles = len(glob.glob(os.path.join(jsonPath, '*.json')))#Counts all .json files in the folder
print("Looping through", str(totalFiles), ".json files in", str(jsonPath))
count = 0

#Looping through JSON files in JSON folder
for file in glob.glob(os.path.join(jsonPath, '*.json')): #only loop through .JSON files in folder.
    count += 1 #Increment the counter
    print ("Processing #", str(count), "/", str(totalFiles), '|', time.asctime(time.localtime()))
    with open(file, encoding='utf-8', mode='r') as jsonFile: #open each .json file for processing
        data = json.load(jsonFile)
        fileID = data['id'] #set file ID from JSON field
        filename = data['filename']
        #set Widen refresh API URL to GET a new download link from (download token expires in 24 hours so we get a new one here)
        refreshURL = "https://api.widencollective.com/v2/assets/" + fileID + "/?" + expands
        headers = {'Authorization': 'Bearer ' + auth}
        if 'type' in data: #Type only exists in attachment JSON so we use that as the check
            attachedApiURL = "https://cbs.widencollective.com/api/rest/asset/uuid/" + data['parent_ID'] + "?options=attachedDocs"#Attachments have to go to V1 endpoint
            attachedResponse = requests.get(attachedApiURL, headers=headers).json()
            items = attachedResponse['attachedDocs']['docs']
            for item in items: #Can't look up attachment's details directly via API so we ping the parent's details for a new download url and compare the id in the attachments to the one we're processing.
                if item['uuid'] == fileID:
                    downloadURL = item['downloadUrl'] #Set the refreshed download url for handling later
            filesize = 'N/A (Attachment)' #No file size info for attachments
        else: # If it's a regular file (doesn't have 'type')
            response = requests.get(refreshURL, headers=headers).json() #refresh JSON via Widen GET requests
            downloadURL = response['_links']['download'] #Set refreshed download URL
            filesize = data['file_properties']['size_in_kbytes']
        
        #Download files to disk
        print("Downloading", filename, "| Size in kilobytes:", str(filesize)) # progress display
        with requests.get(downloadURL, stream=True) as r:
            with open(filename, 'wb') as f:
                fdst = open(destination / filename, 'wb') #wb means "write binary" instead of text
                shutil.copyfileobj(r.raw, fdst) #streaming download contents to disk at fdst location

        #checks for empty downloaded files at root (my IDE left them but terminal didn't)
        if os.path.exists(filename):
            os.remove(filename)#deletes them if they exist. real downloaded files are copied to /downloaded
        
        #Update downloaded asset's metadata in Widen
        if update_metadata == True: #Only fires if user defined variable at top is set to True
            if update_body != '': #If user defined JSON body is not empty
                putHeaders = {'Authorization': 'Bearer ' + auth, 'Content-Type': 'application/json'}
                putURL = 'https://api.widencollective.com/v2/assets/' + fileID + '/metadata'
                response = requests.put(putURL, data = update_body, headers = putHeaders)
                if response.status_code == 200:
                    print('Successfully updated asset metadata in Widen')
                else: 
                    print('Error updating metadata:', response.text)
            else:
                print('Update_body is empty! Skipping update.')

    jsonFileName = Path(str(jsonFile.name)).name #extract just the file name from current JSON file for pathlib
    shutil.move(jsonPath / jsonFileName, jsonPath / "processed" / jsonFileName) # Moving JSON files

print("All .json files have been processed!")
