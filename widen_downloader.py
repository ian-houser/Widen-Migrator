#Looks through a folder of .json files generated from Widen and downloads the original file for each.
#Version 0.20 2022/09/21 | working
#Future: update each asset's metadata in Widen to reflect that it's been migrated?
import json
import requests
import shutil
import os
import glob
from pathlib import Path

#Set working directory as location of the script
wd = Path(os.path.realpath(os.path.dirname(__file__)))
#Set auth token. Loads from creds.key file next to script. Contents should be only "xxx/xxxxx..."
auth = open(wd / "creds.key").read().splitlines()[0]
#The kinds of extra info to return with results in JSON form.
expands = "metadata, asset_properties, file_properties, metadata_info" 

#set JSON directory as a "JSON" folder one level deeper than the script file.
jsonPath = wd / "JSON"

destination = wd / "downloaded"  #set destination for saved file. Set to working directory

#Check if our file paths exist and create them if necessary
if os.path.exists(jsonPath / "processed") == False:
    os.makedirs((jsonPath / "processed"))
if os.path.exists(destination) == False:
    os.mkdir(destination)

#Processing count tracker
totalFiles = len(glob.glob(os.path.join(jsonPath, '*.json')))#Counts all .json files in the folder
print("Looping through " + str(totalFiles) + " .json files in " + str(jsonPath))
count = 0

#Looping through JSON files in JSON folder
for file in glob.glob(os.path.join(jsonPath, '*.json')): #only loop through .JSON files in folder.
    count += 1 #Increment the counter
    print ("Processing #" + str(count) + "/" + str(totalFiles))
    with open(file, encoding='utf-8', mode='r') as jsonFile: #open each .json file for processing
        data = json.load(jsonFile)
        fileID = data['id'] #set file ID from JSON field
        #set Widen refresh API URL to GET a new download link from
        ##(download token expires in 24 hours so we get a new one here)
        refreshURL = "https://api.widencollective.com/v2/assets/" + fileID + "/?" + expands
        headers = {'Authorization': 'Bearer ' + auth}
        response = requests.get(refreshURL, headers=headers).json() #refresh JSON via Widen GET requests
        downloadURL = response['_links']['download'] #Set refreshed download URL
        filename = data['filename']
        filesize = data['file_properties']['size_in_kbytes']
        print("Downloading " + filename + " | Size in kilobytes: " + str(filesize)) # progress display
        #Download files to disk
        def download_file(url):
            with requests.get(url, stream=True) as r:
                with open(filename, 'wb') as f:
                    fdst = open(destination / filename, 'wb') #wb means "write binary" instead of text
                    shutil.copyfileobj(r.raw, fdst) #streaming download contents to disk at fdst location
        download_file(downloadURL)
        #checks for empty downloaded files at root (my IDE left them but terminal didn't)
        if os.path.exists(filename):
            os.remove(filename)#deletes them if they exist. real downloaded files are copied to /downloaded
    jsonFileName = Path(str(jsonFile.name)).name #extract just the file name from current JSON file for pathlib
    shutil.move(jsonPath / jsonFileName, jsonPath / "processed" / jsonFileName) # Moving JSON files
    print("Downloaded original file and moved .json")

print("All .json files have been processed!")
