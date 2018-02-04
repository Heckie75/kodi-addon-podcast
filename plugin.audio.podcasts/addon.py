#!/usr/bin/python
# -*- coding: utf-8 -*-

from datetime import datetime
from operator import itemgetter

import json
import os
import re
import urlparse
import urllib2
import sys

import xbmc
import xbmcgui
import xbmcplugin
import xbmcaddon
import xmltodict

__PLUGIN_ID__ = "plugin.audio.podcasts"

settings = xbmcaddon.Addon(id=__PLUGIN_ID__);
addon_dir = xbmc.translatePath( settings.getAddonInfo('path') )

class Mediathek:

    _GROUPS = 10
    _ENTRIES = 10

    _menu = None
    _addon_handle = None

    def __init__(self):

        groups = []
        for g in range(self._GROUPS):

            if settings.getSetting("group_%i_enable" % g) == "false":
                continue

            entries = []
            for e in range(self._ENTRIES):

                if settings.getSetting("group_%i_rss_%i_enable" % (g, e)) == "false":
                    continue

                entries += [{
                    "path" : "pod_%i" % e,
                    "name" : settings.getSetting("group_%i_rss_%i_name"
                                % (g, e)),
                    "icon" : settings.getSetting("group_%i_rss_%i_icon"
                                % (g, e)),
                    "params" : [
                        {
                            "call" : "renderRss",
                            "url" : settings.getSetting("group_%i_rss_%i_url"
                                        % (g, e))
                        }
                    ],
                        "node" : []
                }]

            groups += [{
                "path" : "group_%i" % g,
                "name" : settings.getSetting("group_%i_name" % g),
                "node" : entries
            }]

        self._menu = [
            { # root
                "path" : "",
                "node" : groups
            }
        ]


    def _loadRss(self, url):

        _file = urllib2.urlopen(url)
        _data = _file.read()
        _file.close()

        return xmltodict.parse(_data)



    def _load_rss_feed(self, url):

        rss_feed = self._loadRss(url)

        channel = rss_feed["rss"]["channel"]

        if "image" in channel:
            image = channel["image"]["url"]
        elif "itunes:image" in channel:
            image = channel["itunes:image"]["@href"]
        else:
            image = ""

        items = channel["item"]

        return items, image



    def playRss(self, parent, path, params):

        url = params["url"][0]
        items, image = self._load_rss_feed(url)
        index = int(params["index"][0])

        item = items[index]
        if "enclosure" in item:
            stream_url = item["enclosure"]["@url"]
        else:
            stream_url = ["guid"]

        xbmc.executebuiltin('PlayMedia(%s)' % stream_url)




    def renderRss(self, parent, path, params):

        url = params["url"][0]
        items, image = self._load_rss_feed(url)
        index = 0

        entries = []

        for item in items:

#       Does not work: see https://forum.kodi.tv/showthread.php?tid=112916
#            if 'pubDate' in item:
#                pubDate = datetime.strptime(item['pubDate'][:-6], '%a, %d %b %Y %H:%M:%S')
#            else:
            pubDate = None

            entries = entries + [{
                    "path" : str(index),
                    "name" : item["title"],
                    "name2" : item["description"],
                    "icon" : image,
                    "params" : [
                        {
                            "call" : "playRss",
						    "index" : str(index),
                            "url" : url
                        }
                    ],
                    "pubDate" : pubDate

                }]

            index += 1


#        entries = sorted(entries, key=itemgetter('pubDate'), reverse=True)
        for entry in entries:

            self._add_list_item(entry, path)

        xbmcplugin.endOfDirectory(self._addon_handle)




    def play(self, parent, path, params):

        url = params["url"][0]
        xbmc.executebuiltin('PlayMedia(%s)' % url)




    def _get_node_by_path(self, path):

        if path == "/":
            return self._menu[0]

        tokens = path.split("/")[1:]
        directory = self._menu[0]

        while len(tokens) > 0:
            path = tokens.pop(0)
            for node in directory["node"]:
                if node["path"] == path:
                    directory = node
                    break

        return directory




    def _build_param_string(self, params, current = ""):

        if params == None:
            return current

        for obj in params:
            for name in obj:
                current += "?" if len(current) == 0 else "&"
                current += name + "=" + str(obj[name])

        return current




    def _add_list_item(self, entry, path):

        if path == "/":
            path = ""

        item_path = path + "/" + entry["path"]
        item_id = item_path.replace("/", "_")

        param_string = ""
        if "params" in entry:
            param_string = self._build_param_string(entry["params"],
                current = param_string)

        if "node" in entry:
            is_folder = True
        else:
            is_folder = False

        label = entry["name"]

        if settings.getSetting("label%s" % item_id) != "":
            label = settings.getSetting("label%s" % item_id)

        if "icon" in entry and entry["icon"].startswith("http"):
            icon_file = entry["icon"]

        elif "icon" in entry:
            icon_file = os.path.join(addon_dir,
                                     "resources",
                                     "assets",
                                     entry["icon"] + ".png")
        else:
            icon_file = None

        li = xbmcgui.ListItem(label, iconImage = icon_file)

        if "name2" in entry:
            li.setLabel2(entry["name2"])

        xbmcplugin.addDirectoryItem(handle=self._addon_handle,
                                listitem=li,
                                url="plugin://" + __PLUGIN_ID__
                                + item_path
                                + param_string,
                                isFolder=is_folder)




    def _browse(self, parent, path):

        for entry in parent["node"]:
            self._add_list_item(entry, path)

        xbmcplugin.endOfDirectory(self._addon_handle)




    def handle(self, argv):

        self._addon_handle = int(argv[1])

        path = urlparse.urlparse(argv[0]).path

        url_params = urlparse.parse_qs(argv[2][1:])

        node = self._get_node_by_path(path)
        if "call" in url_params:

            getattr(self, url_params["call"][0])(parent = node,
                                        path = path,
                                        params = url_params)

        else:
            self._browse(parent = node, path = path)



if __name__ == '__main__':

    mediathek = Mediathek()
    mediathek.handle(sys.argv)
