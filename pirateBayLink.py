import urllib.parse
import webbrowser
import bs4
import os
import argparse
import requests
from prettytable import *


parser = argparse.ArgumentParser()
parser.add_argument('-n', '--name', nargs='*', metavar='name',
                    help="Name of the media to download")
parser.add_argument('-c', '--category', default="all", choices=[
                    "all", "audio", "video", "apps", "games", "other"], type=str, help="Searches for the given 'name' in the specified category (default = all)")
args = parser.parse_args()
# parser.print_help()


def findPirateSite():
    # Finding a working piratesite
    try:
        siteList = requests.get("https://piratebay-proxylist.net")
        siteList.raise_for_status()
    except Exception as e:
        print(e)
        exit(0)
    soup = bs4.BeautifulSoup(siteList.text, features="lxml")
    countries = soup.select(".country")
    domains = soup.select(".domain")
    for country in countries:
        if country.getText().strip() == "IN":
            index = countries.index(country)
            pirateSite = domains[index].getText()
            break
    return pirateSite


def main():
    # Finding a working piratesite
    pirateSite = findPirateSite()

    os.system("mode 500")  # changing size of cmd

    # Input for text name
    if args.name != None:
        mediaName = ' '.join(args.name)
        typeOfMedia = args.category
    else:
        mediaName = input("Which movie/song? ")
        typeOfMedia = input(
            "Any specific type: 1.All 2.Audio 3.Video 4.Applications 5.Games 6.Other:  ").lower()
    types = ["audio", "video", "apps", "games", "other"]
    parameters = {}
    os.system("cls")

    # URL encoding and finding the URL of the final page
    for i in types:
        if i in typeOfMedia:
            parameters.update({i: "on"})

    if parameters:
        parameters.update([('category', 0), ('page', 0), ('orderby', 99)])
    # params = urllib.parse.urlencode(params)
    # params = "&" if (len(params) == 0) else "&"+params+"&"
    path = urllib.parse.quote_plus(mediaName)
    finalUrl = "https://{0}/s/?q={1}".format(
        pirateSite, path)  # URL after search
    # webbrowser.open(finalUrl)

    # Parsing table data from search result website
    try:
        siteFile = requests.get(url=finalUrl, params=parameters)
        siteFile.raise_for_status()
    except Exception as e:
        print(e)
        exit(0)
    # webbrowser.open(siteFile.url)
    soup = bs4.BeautifulSoup(siteFile.text, features="lxml")
    try:
        tableRows = soup.findAll("table")[0].findAll("tr")
    except IndexError:
        print("\nNO TORRENTS FOUND")
        os.system("pause >nul")
        exit(0)

    siteLinks = soup.select(".detLink")
    del tableRows[0]
    tableHeader = ["S.No", "Type", "Name",
                   "Upload Date", "Size", "ULed by", "SE", "LE"]
    table = PrettyTable(tableHeader)
    # table.align["Name"] = "l"
    # table.align["Type"] = "l"
    table.align = "l"
    table.hrules = ALL
    table.padding_width = 4
    sNo = 1
    for tableRow in tableRows:
        text = tableRow.text  # getting table data td
        tableData = text.split("\n")  # spliting data values
        # removing extra elements with no data
        tableData = list(filter(("").__ne__, tableData))
        # removing "\t\t\t" element from list
        tableData = list(filter(("\t\t\t").__ne__, tableData))
        # removing tab spaces from "type" data
        tableData[1] = ' '.join(tableData[1].split())
        # spliting Uploaded, Size and ULed data
        tableData[3:4] = tableData[3].split(", ")
        # joining both "type" data
        tableData[0:2] = ["\n".join(tableData[0:2])]
        tableData[2] = tableData[2].replace(
            "Uploaded ", "")  # removing "Uploaded" from text
        tableData[3] = tableData[3].replace(
            "Size ", "")  # removing "Size" from text
        tableData[4] = tableData[4].replace(
            "ULed by ", "")  # removing "ULed" from text
        tableData.insert(0, sNo)  # inserting S.No to table
        table.add_row(tableData)  # adding row data to table
        sNo += 1
        # print(tableData)

    print(table)

    # input from user
    usrIn = int(input("\nEnter the number - press 0 to exit: "))
    if usrIn == 0:
        i = input("Do you want to do another search(y/n)? ").lower()
        if i == 'y':
            main()
        exit(0)
    else:
        target = siteLinks[usrIn - 1]["href"]
        finalUrl = "https://" + pirateSite + target  # URL after selecting media
    # webbrowser.open(finalUrl)

    # Getting the link of torrent file
    try:
        sitefile = requests.get(finalUrl)
        siteFile.raise_for_status()
    except Exception as e:
        print(e)
        exit(0)
    soup = bs4.BeautifulSoup(sitefile.text, features="lxml")
    elems = soup.select(".download > a")
    torrentLink = elems[0]["href"]
    webbrowser.open(torrentLink)
    i = input("Do you want to do another search(y/n)? ").lower()
    if i == 'y':
        main()
    # os.system("pause")


if __name__ == "__main__":
    main()
