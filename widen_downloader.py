print("version 0.12 2022/09/15 | working")
import json
import requests
import shutil
import os
import glob

#Set working directory as location of the script (run via CMD, not opening script directly)
wd = os.path.dirname(__file__)

#Set auth token. Loads from creds.key file next to script. Contents should be only "xxx/xxxxx..."
auth = open(wd + "\\creds.key").read().splitlines()[0]

#set JSON directory as a "JSON" folder one level deeper than the script.
jsonPath = wd + "\\JSON\\"

#Processing count tracker
totalFiles = len(glob.glob(os.path.join(jsonPath, '*.json')))
print("Looping through " + str(totalFiles) + " .json files in " + jsonPath)
count = 0

#Looping through JSON files in JSON folder
for file in glob.glob(os.path.join(jsonPath, '*.json')): #only process .JSON files in folder.
    count += 1
    print ("Processing #" + str(count))
    with open(file, encoding='utf-8', mode='r') as jsonFile:
        data = json.load(jsonFile)
        #set file ID from JSON field
        fileID = data['id']
        #set Widen refresh API URL to GET a new download link from
        ##(download token expires in 24 hours so we get a new one here)
        refreshURL = "https://api.widencollective.com/v2/assets/" + fileID + "/?expand=metadata,asset_properties,file_properties"
        headers = {'Authorization': 'Bearer ' + auth}
        #refresh JSON via Widen GET requests
        response = requests.get(refreshURL, headers=headers).json()
        #Set refreshed download URL
        downloadURL = response['_links']['download']
        filename = data['filename']
        filesize = data['file_properties']['size_in_kbytes']
        print("Downloading " + filename + " | Size in kilobytes: " + str(filesize))
        #Download files to disk
        def download_file(url):
            local_filename = data['filename']
            with requests.get(url, stream=True) as r:
                with open(local_filename, 'wb') as f:
                    #set destination for saved file. Set to working directory
                    dest = wd + "\\" + filename
                    fdst = open(dest, 'wb')
                    shutil.copyfileobj(r.raw, fdst)
            return local_filename
        download_file(downloadURL)
        # Closing JSON file so it can be moved
        jsonFile.close()
        # Moving JSON files
        shutil.move(jsonPath + filename + ".json", jsonPath + "processed\\" + filename + ".json")
        print("Downloaded and moved .json")

print("All .json files have been processed!")
