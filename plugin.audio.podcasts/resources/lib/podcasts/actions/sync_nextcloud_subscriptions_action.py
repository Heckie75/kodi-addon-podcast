import time

import xbmc
import xbmcaddon
import xbmcgui
from resources.lib.podcasts.actions.opml_action import OpmlAction
from resources.lib.podcasts.nextcloud import Nextcloud
from resources.lib.podcasts.podcastsaddon import PodcastsAddon
from resources.lib.podcasts.util import get_asset_path
from resources.lib.rssaddon.http_status_error import HttpStatusError


class SyncNextcloudSubscriptionsAction(OpmlAction):

    def __init__(self) -> None:
        super().__init__()

    def _query_subscriptions_from_nextcloud(self, full: bool = True) -> dict:

        try:
            host = self.addon.getSetting("nextcloud_hostname")
            user = self.addon.getSetting("nextcloud_username")
            password = self.addon.getSetting("nextcloud_password")
            nextcloud = Nextcloud(self.addon, host, user, password)

            timestamp = self.addon.getSettingInt("nextcloud_sync_timestamp")
            response = nextcloud.request_subscriptions(
                timestamp=0 if full else timestamp)
            self.addon.setSettingInt(
                "nextcloud_sync_timestamp", int(time.time()))

            return response

        except HttpStatusError as error:
            xbmc.log(str(error), xbmc.LOGERROR)
            xbmcgui.Dialog().ok(self.addon.getLocalizedString(32151), error.message)

    def _get_current_active_feeds(self) -> 'dict[str,str]':
        _known_feeds = dict()
        for g in range(self._GROUPS):
            if self.addon.getSettingBool("group_%i_enable" % g):
                for e in range(self._ENTRIES):
                    if self.addon.getSettingBool("group_%i_rss_%i_enable" % (g, e)):
                        _known_feeds[self.addon.getSetting("group_%i_rss_%i_url" % (
                            g, e))] = self.addon.getSetting("group_%i_rss_%i_name" % (g, e))

        return _known_feeds

    def _deactivate_feed_by_url(self, url: str) -> bool:

        found = False
        for g in range(self._GROUPS):
            for e in range(self._ENTRIES):
                if self.addon.getSetting("group_%i_rss_%i_url" % (g, e)) == url:
                    self.addon.setSettingBool(
                        "group_%i_rss_%i_enable" % (g, e), False)
                    found = True

        return found

    def sync_nextcloud_subscriptions(self, full: bool = True, opensettings: bool = False) -> None:

        def _inspect_feeds_to_add(candicates_to_add: 'dict[str,str]') -> 'list[tuple[str,str,str,str]]':

            if not candicates_to_add:
                return list()

            progress = xbmcgui.DialogProgress()
            progress.create(heading=self.addon.getLocalizedString(32114))

            podcastsAddon = PodcastsAddon(self.addon)
            feeds = list()
            for i, feed in enumerate(candicates_to_add):
                try:
                    progress.update(percent=int(
                        i / len(candicates_to_add) * 100), message=feed)
                    title, description, image, items = podcastsAddon.load_rss(
                        feed)
                    feeds.append((feed, title, image, description))
                    if progress.iscanceled():
                        return None
                except:
                    xbmc.log("Unable to load rssfeed %s" %
                             feed, xbmc.LOGWARNING)

            progress.close()
            return feeds

        def _handle_candicates_to_add(candicates_to_add: 'dict[str,str]') -> bool:

            feeds = _inspect_feeds_to_add(candicates_to_add)
            while feeds:

                items = list()
                for i in feeds:
                    li = xbmcgui.ListItem(label=i[1], label2=i[3])
                    li.setArt({"thumb": i[2]})
                    items.append(li)

                selected_feeds = xbmcgui.Dialog().multiselect(
                    heading=self.addon.getLocalizedString(32116), options=items, useDetails=True)

                if selected_feeds == None:
                    return False

                elif not selected_feeds:
                    return True

                group, freeslots = self._select_target_group()
                if group == -1:
                    continue

                elif freeslots < len(selected_feeds):
                    xbmcgui.Dialog().ok(self.addon.getLocalizedString(32074),
                                        self.addon.getLocalizedString(32075) % freeslots)
                    continue

                else:
                    self.addon.setSetting("group_%i_enable" % group, "True")
                    i, j = 0, 0
                    while (i < self._ENTRIES):
                        if j < len(selected_feeds) and not self.addon.getSettingBool("group_%i_rss_%i_enable" % (group, i)):
                            self.addon.setSettingBool(
                                "group_%i_rss_%i_enable" % (group, i), True)
                            self.addon.setSetting("group_%i_rss_%i_name" % (
                                group, i), feeds[selected_feeds[j]][1])
                            self.addon.setSetting("group_%i_rss_%i_url" % (
                                group, i), feeds[selected_feeds[j]][0])
                            self.addon.setSetting(
                                "group_%i_rss_%i_icon" % (group, i), feeds[selected_feeds[j]][2])
                            j += 1

                        i += 1

                feeds = [feed for i, feed in enumerate(
                    feeds) if i not in selected_feeds]

            return True

        def _handle_candicates_to_delete(candicates_to_delete: 'dict[str,str]') -> bool:

            if not candicates_to_delete:
                return True

            options = [(feed, candicates_to_delete[feed])
                       for feed in candicates_to_delete]
            selection = xbmcgui.Dialog().multiselect(
                heading=self.addon.getLocalizedString(32115), options=[o[1] for o in options])

            if selection == None:
                return False

            for i in selection:
                self._deactivate_feed_by_url(options[i][0])

            return True

        current_active_feeds = self._get_current_active_feeds()
        xbmcgui.Dialog().notification(heading=self.addon.getLocalizedString(
            32094), message=self.addon.getLocalizedString(32113), icon=get_asset_path("notification.png"))
        response = self._query_subscriptions_from_nextcloud(full)

        candicates_to_add = {
            url: None for url in response["add"] if url not in current_active_feeds}
        candicates_to_delete = {
            url: current_active_feeds[url] for url in response["remove"] if url in current_active_feeds}
        if full:
            for current in current_active_feeds:
                if current not in response["add"]:
                    candicates_to_delete[current] = current_active_feeds[current]

        if not _handle_candicates_to_add(candicates_to_add):
            return

        if not _handle_candicates_to_delete(candicates_to_delete):
            return

        xbmcgui.Dialog().notification(heading=self.addon.getLocalizedString(
            32094), message=self.addon.getLocalizedString(32117), icon=get_asset_path("notification.png"))

        if opensettings:
            xbmcaddon.Addon().openSettings()

    def check_for_updates(self) -> None:

        if self.addon.getSettingInt("remote_type") == 2 and self.addon.getSetting("nextcloud_hostname") not in ["https://", ""]:
            if time.time() - self.addon.getSettingInt("nextcloud_sync_interval") * 86400 > self.addon.getSettingInt("nextcloud_sync_timestamp"):
                syncNextcloudSubscriptionsAction = SyncNextcloudSubscriptionsAction()
                syncNextcloudSubscriptionsAction.sync_nextcloud_subscriptions(
                    False, False)
