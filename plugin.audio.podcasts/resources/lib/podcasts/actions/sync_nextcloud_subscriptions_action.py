import time

import json
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

    def _change_subscription_in_nextcloud(self, add: 'list[str]', remove: 'list[str]', timestamp: int = None) -> dict:

        try:
            host = self.addon.getSetting("nextcloud_hostname")
            user = self.addon.getSetting("nextcloud_username")
            password = self.addon.getSetting("nextcloud_password")
            nextcloud = Nextcloud(self.addon, host, user, password)

            payload = {
                "add": add,
                "remove": remove,
                "timestamp": timestamp if timestamp is not None else int(time.time())
            }


            xbmc.log(json.dumps(payload), xbmc.LOGINFO)
            response = nextcloud.change_subscriptions(payload=payload)

            return response

        except HttpStatusError as error:
            xbmc.log(str(error), xbmc.LOGERROR)
            xbmcgui.Dialog().ok(self.addon.getLocalizedString(32151), error.message)

    def _get_current_feeds(self) -> 'tuple[dict[str,tuple[str,str,str]],dict[str,tuple[str,str,str]]]':
        _active_feeds = dict()
        _inactive_feeds = dict()
        for g in range(self._GROUPS):
            for e in range(self._ENTRIES):
                name = self.addon.getSetting("group_%i_rss_%i_name" % (g, e))
                url = self.addon.getSetting("group_%i_rss_%i_url" % (g, e))
                icon = self.addon.getSetting("group_%i_rss_%i_icon" % (g, e))
                group = self.addon.getSetting("group_%i_name" % g)
                if name and url:
                    if self.addon.getSettingBool("group_%i_enable" % g) and self.addon.getSettingBool("group_%i_rss_%i_enable" % (g, e)):
                        _active_feeds[url] = (name, icon, group)
                    else:
                        _inactive_feeds[url] = (name, icon, group)

        return _active_feeds, _inactive_feeds

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

        def _inspect_feeds_to_add(candicates_to_add: 'dict[str,tuple[str,str,str]]') -> 'list[tuple[str,str,str,str]]':

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

        def _handle_candicates_to_add(candicates_to_add: 'dict[str,tuple[str,str,str]]') -> bool:

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

        def _handle_candicates_to_delete(candicates_to_delete: 'dict[str,tuple[str,str,str]]') -> bool:

            if not candicates_to_delete:
                return True

            items: 'list[xbmcgui.ListItem]' = list()
            for url in candicates_to_delete:
                entry = candicates_to_delete[url]
                li = xbmcgui.ListItem(label=entry[0], label2="%s: %s" % (
                    self.addon.getLocalizedString(32000), entry[2]), path=url)
                if entry[1]:
                    li.setArt({"thumb": entry[1]})
                else:
                    li.setArt({"thumb": get_asset_path("notification.png")})
                items.append(li)

            selection = xbmcgui.Dialog().multiselect(
                heading=self.addon.getLocalizedString(32115), options=items, useDetails=True)

            if selection == None:
                return False

            for i in selection:
                self._deactivate_feed_by_url(items[i].getPath())

            return True

        current_active_feeds, current_inactive_feeds = self._get_current_feeds()
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

    def export_to_nextcloud(self) -> None:

        def _handle_candicates(candidates: 'dict[str,tuple[str,str,str]]', heading: str) -> 'list[str]':

            if not candidates:
                return []

            items: 'list[xbmcgui.ListItem]' = list()
            for url in candidates:
                entry = candidates[url]
                li = xbmcgui.ListItem(label=entry[0], label2="%s: %s" % (
                    self.addon.getLocalizedString(32000), entry[2]), path=url)
                if entry[1]:
                    li.setArt({"thumb": entry[1]})
                else:
                    li.setArt({"thumb": get_asset_path("notification.png")})

                items.append(li)

            selection = xbmcgui.Dialog().multiselect(
                heading=heading, options=items, useDetails=True)

            if selection == None:
                return None

            return [items[i].getPath() for i in selection]

        current_active_feeds, current_inactive_feeds = self._get_current_feeds()
        xbmcgui.Dialog().notification(heading=self.addon.getLocalizedString(
            32094), message=self.addon.getLocalizedString(32113), icon=get_asset_path("notification.png"))
        response = self._query_subscriptions_from_nextcloud()

        candicates_to_add = {
            url: current_active_feeds[url] for url in current_active_feeds if url not in response["add"]}
        candicates_to_delete = {
            url: current_inactive_feeds[url] for url in current_inactive_feeds if url in response["add"] and url not in current_active_feeds}

        _to_add = _handle_candicates(
            candicates_to_add, heading=self.addon.getLocalizedString(32119))
        if _to_add == None:
            return

        _to_delete = _handle_candicates(
            candicates_to_delete, heading=self.addon.getLocalizedString(32120))
        if _to_delete == None:
            return

        xbmc.log("\n".join(_to_add), xbmc.LOGINFO)
        xbmc.log("\n".join(_to_delete), xbmc.LOGINFO)

        self._change_subscription_in_nextcloud(add=_to_add, remove=_to_delete, timestamp=0)

        xbmcgui.Dialog().notification(heading=self.addon.getLocalizedString(
            32094), message=self.addon.getLocalizedString(32117), icon=get_asset_path("notification.png"))

        xbmcaddon.Addon().openSettings()

    def check_for_updates(self) -> None:

        if self.addon.getSettingInt("remote_type") == 2 and self.addon.getSetting("nextcloud_hostname") not in ["https://", ""]:
            if time.time() - self.addon.getSettingInt("nextcloud_sync_interval") * 86400 > self.addon.getSettingInt("nextcloud_sync_timestamp"):
                syncNextcloudSubscriptionsAction = SyncNextcloudSubscriptionsAction()
                syncNextcloudSubscriptionsAction.sync_nextcloud_subscriptions(
                    False, False)
