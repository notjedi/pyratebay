# TODO: Get the top result for India from "https://piratebay-proxylist.net" and update finalUrl dynamically


import urllib.parse
import webbrowser

targetName = input("Which movie/song? ")
types = ["audio", "video", "apps", "games", "other"]
params = {}
typeOfMedia = input(
    "Any specific type: 1.Audio 2.Video 3.Applications 4.Games 5.Other\n").lower()
for i in types:
    if i in typeOfMedia:
        params.update({i: "on"})
params = urllib.parse.urlencode(params)
params = "&" if (len(params) == 0) else "&"+params+"&"
path = urllib.parse.quote_plus(targetName)
finalUrl = "https://tpbpirate.org/s/?q={0}{1}category=0&page=0&orderby=99".format(
    path, params)
print(finalUrl)
# webbrowser.open(finalUrl)