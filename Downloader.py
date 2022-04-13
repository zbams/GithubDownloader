import os
import sys
import requests
from bs4 import BeautifulSoup

# dev: get text of all elements in list
# params: list of soup web elements 
# returns list()<str>
def get_elements_text(elements:list) -> list:
    return [l.text for l in elements]

# dev: split files and folders, and add hrefs
# params: list of soup web elements 
# returns dict()<list()<str>, list()<str>, list()<str>>
def split_files_folders(links:list) -> dict:
    split = {
        "files": [],
        "folders": []
    } # create split element
    for link in links:
        if "." in link.text: # TODO: better link checking if file or dir (without requesting page)
            split["files"].append(link) # append file to files in split
        else:
            split["folders"].append(link) # append dir to folders in split
    # create and format href's for Github raw file
    split["hrefs"] = ["https://raw.githubusercontent.com" + file["href"].replace("/blob", "") for file in split["files"]]
    return split

# dev: get links from given url
# params: string url of where to return links
# returns list()<Element>
def get_links(url:str) -> list:
    soup = BeautifulSoup(requests.get(url).text, features="html.parser") # get page and parse
    return soup.find_all("a", {"class": "js-navigation-open Link--primary"}) # return all "a" elements with matching class

# dev: download file and write in folder
# params: url to download, folder to store downloaded file
# returns None
def download(url:str, folder:str):
    folder = folder + "/" if folder[-1] != "/" else folder # add trailing "/"
    with open(folder + url.split("/")[-1], "w", encoding="utf-8") as f: # open file
        text = requests.get(url).text # get text from page
        f.write(text) # write to file

# dev: recursively download dirs from url
# params: url to search, folder to store files from search
# returns: None
def handle_url_folder(url:str, data_folder:str):
    #data_folder = data_folder + url.split("/")[-1]
    if not os.path.exists(data_folder):
        os.makedirs(data_folder) # create dir if it doesnt already exist
    page_data = split_files_folders(get_links(url))
    for href in page_data["hrefs"]:
        download(href, data_folder) # download href
        
    for folder in get_elements_text(page_data["folders"]):
        handle_url_folder((url + "/" if url[-1] != "/" else url) + folder, data_folder + folder + "/") # create and loop through next dir


if __name__ == "__main__":
    data_folder = os.getcwd() + "/Data/" # data location
    if not os.path.exists(data_folder):
        os.makedirs(data_folder) # create dir if it doesnt already exist

    url = input("Enter URL: ") if not len(sys.argv) > 1 else sys.argv[1] # get url from args or user input
    url = url if not url[-1] == "/" else url[0:-1] # strip trailing "/"
    print("Downloading please wait...")
    handle_url_folder(url, data_folder + url.split("/")[-1] + "/")
    print("Complete.")
