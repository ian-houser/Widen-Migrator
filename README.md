
# Widen Migrator

  

This is a set of scripts that assist in exporting files from Widen in two stages:

1) Exports .json files of metadata for each file returned in a query.

2) Loops through those .json files and downloads the original file for each.

  

## Requirements

1) The only external module used is [Requests](https://pypi.org/project/requests/). After installation the scripts should run without needing anything else.

  

## Usage

 1. Make a "creds.key" file next to the scripts that only contains your Widen API token ('xxx/xxxxx...')
 2. Edit widen_exporter.py
		 - "query" variable: how you'll target files to export. Usage of Advanced Search syntax is best. Create a search formula that you like in Widen and then copy it here. [More info](https://community.widen.com/collective/s/article/How-do-I-search-for-assets)
		 - "expands": The kinds of extra info to return with results in JSON form. [More info](https://widenv2.docs.apiary.io/#reference/expands)
		 - "limit": The number of results to return with each scroll. Accepts numbers 1-100.
		 - "checkAttached": Whether or not to check for attached documents on each asset and download the JSON
		 - "subOrganize": Whether or not to organize JSON in to sub-folders based on their categories (field_set)
 3. Run widen_exporter.py - Depending on the "subOrganize" option, it will generate folders with your files inside by calling Widen's scrolling search endpoint. It will export files 100 at a time and should process very quickly (checkAttached option takes more time due to API logistics).
 4. Run widen_downloader.py with your JSON folder next to it. It will process the files at the top level of that folder then move the processed JSON files into a "processed" subfolder. It will download your original files into a "downloaded" folder next to the script. You can stop and start the downloader as much as you want since won't re-process already downloaded files.

  

## Notes

 1. If you're dealing with a large number of files, break the exports into pieces and name the folders according to their query.
 2. Rate limits only apply to customers who joined after April 2022. I did not develop with rate limits in mind but this should still be a fairly efficient way of handling it.
 3. Tested on Windows & MacOS in a Python 3 enviroment.

  

## Contact

I'm available! Let me know if I can help.

ian.houser@cbsinteractive.com