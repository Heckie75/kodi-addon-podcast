import xbmc
import xbmcaddon
import xbmcgui
from resources.lib.podcasts.actions.action import Action
from resources.lib.podcasts.gpodder import GPodder
from resources.lib.rssaddon.http_status_error import HttpStatusError


class CommitGPodderAction(Action):

    def commit_gpodder(self) -> None:

        try:
            host = self.addon.getSetting("gpodder_hostname")
            user = self.addon.getSetting("gpodder_username")
            password = self.addon.getSetting("gpodder_password")

            gPodder = GPodder(self.addon, host, user)
            gPodder.login(password)

        except HttpStatusError as error:
            xbmcgui.Dialog().ok(self.addon.getLocalizedString(32151), error.message)

        xbmcaddon.Addon().openSettings()
