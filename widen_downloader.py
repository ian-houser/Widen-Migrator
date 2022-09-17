#Looks through a folder of .json files generated from Widen and downloads the original file for each.
#Version 0.13 2022/09/16 | working
#Future: update each asset's metadata in Widen to reflect that it's been migrated?
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

#Processing count tracker
totalFiles = len(glob.glob(os.path.join(jsonPath, '*.json')))#Counts all .json files in the folder
print("Looping through " + str(totalFiles) + " .json files in " + jsonPath)
count = 0

#Looping through JSON files in JSON folder
for file in glob.glob(os.path.join(jsonPath, '*.json')): #only loop through .JSON files in folder.
    count += 1 #Increment the counter
    print ("Processing #" + str(count) + "/" + 3
    222str(totalFiles))
    with open(file, encoding='utf-8', mode='r') as jsonFile: #open each .json file for processing
        data = json.load(jsonFile)
        fileID = data['id'] #set file ID from JSON field
        #set Widen refresh API URL to GET a new download link from
        ##(download token expires in 24 hours so we get a new one here)
        refreshURL = "https://api.widencollective.com/v2/assets/" + fileID + "/?expand=metadata,asset_properties,file_properties"
        headers = {'Authorization': 'Bearer ' + auth}
        response = requests.get(refreshURL, headers=headers).json() #refresh JSON via Widen GET requests
        downloadURL = response['_links']['download'] #Set refreshed download URL
        filename = data['filename']
        filesize = data['file_properties']['size_in_kbytes']
        print("Downloading " + filename + " | Size in kilobytes: " + str(filesize)) # progress display
        #Download files to disk
        def download_file(url):
            local_filename = data['filename']
            with requests.get(url, stream=True) as r:
                with open(local_filename, 'wb') as f:
                    dest = wd + "\\downloaded\\" + filename  #set destination for saved file. Set to working directory
                    fdst = open(dest, 'wb') #wb means "write binary" instead of text
                    shutil.copyfileobj(r.raw, fdst) #streaming download contents to disk at fdst location
            return local_filename
        download_file(downloadURL) #almost forgot to actually call the function!
        jsonFile.close() # Closing JSON file so it can be moved
        shutil.move(jsonPath + filename + ".json", jsonPath + "processed\\" + filename + ".json") # Moving JSON files
        print("Downloaded original file and moved .json")

print("All .json files have been processed!")
