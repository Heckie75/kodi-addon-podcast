import xbmcaddon
import xbmcgui
import xbmcvfs

class Action:

    __PLUGIN_ID__ = "plugin.audio.podcasts"

    addon = None
    addon_handle = None
    plugin_id = __PLUGIN_ID__
    addon_dir = None
    anchor_for_latest = True

    def __init__(self, addon_handle):

        self.addon = xbmcaddon.Addon(id=self.plugin_id)
        self.addon_handle = addon_handle
        self.addon_dir = xbmcvfs.translatePath(self.addon.getAddonInfo('path'))


    def _select_target_group(self):

        names = list()
        freeslots = list()
        for g in range(self._GROUPS):
            free = sum("false" == self.addon.getSetting(
                "group_%i_rss_%i_enable" % (g, r)) for r in range(self._ENTRIES))

            freeslots.append(free)

            names.append("%s %i: %s (%i %s)" %
                         (
                             self.addon.getLocalizedString(32000),
                             g + 1,
                             self.addon.getSetting("group_%i_name" % g),
                             free,
                             self.addon.getLocalizedString(32077)
                         ))

        selected = xbmcgui.Dialog().select(self.addon.getLocalizedString(32076), names)
        if selected > -1 and freeslots[selected] == 0:
            xbmcgui.Dialog().ok(heading=self.addon.getLocalizedString(32078),
                                message=self.addon.getLocalizedString(32084))
            return -1, 0

        elif selected == -1:
            return -1, 0

        else:
            return selected, freeslots[selected]