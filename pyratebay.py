import re
import json
import requests
import argparse
import pyperclip
from urllib.parse import quote

from prettytable import *
from datetime import datetime
from bs4 import BeautifulSoup


def print_banner():
    # Print banner
    print(r"""
                                                                                                         __                       _______
                                                                                                        /  |                     /       \
                                                                 ______   __    __   ______   ______   _$$ |_     ______         $$$$$$$  |  ______   __    __
                                                                /      \ /  |  /  | /      \ /      \ / $$   |   /      \        $$ |__$$ | /      \ /  |  /  |
                                                                /$$$$$$  |$$ |  $$ |/$$$$$$  |$$$$$$  |$$$$$$/   /$$$$$$  |      $$    $$<  $$$$$$  |$$ |  $$ |
                                                                $$ |  $$ |$$ |  $$ |$$ |  $$/ /    $$ |  $$ | __ $$    $$ |      $$$$$$$  | /    $$ |$$ |  $$ |
                                                                $$ |__$$ |$$ \__$$ |$$ |     /$$$$$$$ |  $$ |/  |$$$$$$$$/       $$ |__$$ |/$$$$$$$ |$$ \__$$ |
                                                                $$    $$/ $$    $$ |$$ |     $$    $$ |  $$  $$/ $$       |      $$    $$/ $$    $$ |$$    $$ |
                                                                $$$$$$$/   $$$$$$$ |$$/       $$$$$$$/    $$$$/   $$$$$$$/       $$$$$$$/   $$$$$$$/  $$$$$$$ |
                                                                $$ |      /  \__$$ |                                                                 /  \__$$ |
                                                                $$ |      $$    $$/                                                                  $$    $$/
                                                                $$/        $$$$$$/                                                                    $$$$$$/
    """)

def find_site(isDebug):
    """
    Finds a functional piratebay site

    @return: returns the URL of the functional piratebay site
    """
    try:
        siteList = requests.get("https://proxybay.github.io")
        siteList.raise_for_status()
    except HTTPError as e:
        print(e)
        exit(0)

    soup = BeautifulSoup(siteList.text, features="lxml")
    domains = soup.select(".site")
    if isDebug:
        print(domains[1].text)
        countries = soup.select(".country")
        print(countries[0].find('img')['title'])
    return domains[1].text


def get_server(site):
    resp = requests.get(site + "/static/main.js").text
    server = re.match(r'var server=\'(.+?)\';var', resp)[1]
    return server

def format_bytes(size):
    power = 2**10 # 2**10 = 1024
    n = 0
    labels = {0 : 'B', 1: 'KB', 2: 'MB', 3: 'GB', 4: 'TB'}
    while size > power:
        size /= power
        n += 1
    return str(round(size, 2)) + " " + labels[n]


def build_table(json):
    tableHeader = ["S.No", "Type", "Name",
                   "Upload Date", "Size", "ULed by", "SE", "LE"]
    category = {"0": "", "1": 'Audio', "2": 'Video', "3": 'Application',
                "4": 'Games', "5": 'Porn', "6": 'Other'}
    table = PrettyTable(tableHeader)
    table.align = "l"
    table.hrules = ALL
    table.padding_width = 2

    for i, obj in enumerate(json):
        row = []
        row.append(i+1)
        row.append(category[obj['category'][0]])
        row.append(obj['name'])
        row.append(format_bytes(int(obj['size'])))
        row.append(datetime.fromtimestamp(int(obj['added'])).strftime("%Y-%m-%d"))
        row.append(obj['username'])
        row.append(obj['seeders'])
        row.append(obj['leechers'])
        table.add_row(row)
        
    return table

def download(baseUrl, id, trackers):
    # https://pirateproxy.how/newapi/f.php?id=11490904 # files
    # https://pirateproxy.how/newapi/t.php?id=11490904 # torrent info

    if (id == '0'):
        print("Torrent does not exist")
        return

    info = json.loads(requests.get(baseUrl + "t.php?id=" + id ).text)
    files = json.loads(requests.get(baseUrl + "f.php?id=" + id ).text)
    print(info['descr'])
    print()

    if len(files) == 1:
            print(files[0]['name'][0].ljust(50, ' '), end='\t\t')
            print(format_bytes(int(files[0]['size'][0])))
    else:
        for file in files:
            print(file['name']['0'].ljust(50, ' '), end='\t\t')
            print(format_bytes(int(file['size']['0'])))

    confirm = input("\nDo you want to download this torrent(y/n)? ")
    if confirm.lower() in ["y", "yes"]:
        link = "magnet:?xt=urn:btih:" + info['info_hash'] + "&dn=" + quote(info['name'])
        for tracker in trackers:
            link += "&tr=" + quote(tracker, safe='')
        pyperclip.copy(link)


def get_trackers():
    resp = requests.get("https://ngosang.github.io/trackerslist/trackers_best.txt").text
    return list(filter(lambda x: x != '', resp.split('\n')))


def main(args):

    isDebug = args.debug
    print_banner()
    site = "https://" + find_site(isDebug)
    server = get_server(site)
    trackers = get_trackers()
    baseUrl = site + server

    inText = {0: "\n=>> Search for torrents (:q to quit)", 1: "\n=>> Select a torrent to download (:q to quit)"}
    cnt = 0
    resp = []

    while True:
        print(inText[cnt])
        query = input("> ")
        cnt = 1
        if (query.lower().strip() == ":q"):
            break

        try:
            idx = int(query)
            if (idx < 1 or idx > 100):
                print("Select a valid torrent")
                continue
            download(baseUrl, resp[idx-1]['id'], trackers)
        except ValueError:
            searchUrl = baseUrl + "/q.php?q=" + quote(query) + "&cat="
            resp = requests.get(searchUrl).text
            resp = json.loads(resp)
            table = build_table(resp)
            print(table)


if __name__ == "__main__":

    # TODO:
    # Add support to download multiple files
    # Add support to view the description of file before downloading
    # Use xdg-open?

    # Parse command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--debug', dest='debug',
                        action='store_true', help="Prints debug messages")
    args = parser.parse_args()

    main(args)
