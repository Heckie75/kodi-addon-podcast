from resources.lib.actions.action import Action
from resources.lib.rssaddon.httpstatuserror import HttpStatusError
import resources.lib.gpodder.gpodder as gpodder

import xmltodict

import xbmcgui

class ImportOpmlAction(Action):

    def __init__(self, addon_handle):
        super().__init__(addon_handle)

    def download_gpodder_subscriptions(self):

        # Step 1: download subscriptions from gPodder
        try:
            sessionid = gpodder._login_at_gpodder()
            opml_data = gpodder._load_gpodder_subscriptions(sessionid)

        except HttpStatusError as error:
            xbmcgui.Dialog().ok(self.addon.getLocalizedString(32151), error.message)
            return

        # Step 2: Save file in folder
        path, filename = self._save_opml_file(opml_data)
        if not path:
            return

        # Success
        xbmcgui.Dialog().notification(self.addon.getLocalizedString(
            32085), "%s %s" % (self.addon.getLocalizedString(32083), filename))

        # Step 3: Select target opml slot
        slot = self._select_target_opml_slot(
            self.addon.getLocalizedString(32079))
        if slot == -1:
            return

        self.addon.setSetting("opml_file_%i" % slot, path)

        # Success
        xbmcgui.Dialog().notification(self.addon.getLocalizedString(
            32085), self.addon.getLocalizedString(32086))

    def _save_opml_file(self, data):

        opml = xmltodict.parse(data)
        filename = "%s.opml" % re.sub(
            "[^A-Za-z0-9']", " ", opml["opml"]["head"]["title"])

        path = xbmcgui.Dialog().browse(
            type=3, heading=self.addon.getLocalizedString(32080), shares="")

        if not path:
            return None, None

        try:
            fullpath = "%s%s" % (path, filename)
            with open(fullpath, "w") as _file:
                _file.write(data)

            return fullpath, filename

        except:
            xbmcgui.Dialog().ok(heading=self.addon.getLocalizedString(
                32081), message=self.addon.getLocalizedString(32082))

            return None, None
