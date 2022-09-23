# Widen Migrator

This is a set of scripts that assist in exporting files from Widen in two stages: 
 
1) Exports .json files of metadata for each file returned in a query.  
2) Loops through those .json files and downloads the original file for each.

## Requirements
1) The only external module used is [Requests](https://pypi.org/project/requests/). After installation the scripts should run without needing anything else.

## Usage

1) Make a "creds.key" file next to the scripts that only contains your Widen API token ('xxx/xxxxx...')  

2) Edit widen_exporter.py - At least the "query" variable - that's how you'll target files to export. Usage of Advanced Search syntax is best. Create a search formula that you like in Widen and then copy it here. [More info](https://community.widen.com/collective/s/article/How-do-I-search-for-assets)
  
3) Run widen_exporter.py - It will generate a "JSON" folder with your files inside by calling Widen's scrolling search endpoint. It will export files 100 at a time and should process very quickly.

4) Run widen_downloader.py with your JSON folder next to it. It will process the files at the top level of that folder then move the processed JSON files into a "processed" subfolder. It will download your original files into a "downloaded" folder next to the script. You can stop and start the downloader as much as you want since won't re-process already downloaded files.

## Notes
1) If you're dealing with a large number of files, break the exports into pieces and name the folders according to their query. 
2) Alterations to the script can be made to arrange the JSON files into folders according to their Categories/"field_set" to make organization and batch processing easier.
3) I didn't hit any rate limits but it is theoretically possible though unlikely. Placing a strategic "sleep" in the download function could offset this.
4) Tested on Windows & MacOS in a Python 3 enviroment.

## Contact
I'm available! Let me know if I can help.
ian.houser@cbsinteractive.com
