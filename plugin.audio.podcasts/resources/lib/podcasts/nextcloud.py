from resources.lib.rssaddon.http_status_error import HttpStatusError
from resources.lib.rssaddon.http_client import http_request
import base64
import json

import xbmcaddon


class Nextcloud:

    _NEXTCLOUD_API = {
        "status": "%s/status.php",
        "subscriptions": "%s/index.php/apps/gpoddersync/subscriptions?since=%i",
        "subscription_change": "/index.php/apps/gpoddersync/subscription_change/create"
    }

    _addon = None
    _host = None
    _user = None
    _password = None

    def __init__(self, addon: xbmcaddon.Addon, host: str, user: str, password: str) -> None:

        self._addon = addon
        self._host = host
        self._user = user
        self._password = password

    def _get_auth(self) -> dict:

        auth_string = "%s:%s" % (self._user, self._password)
        return {
            "Authorization": "Basic %s" % base64.urlsafe_b64encode(auth_string.encode("utf-8")).decode("utf-8")
        }

    def request_subscriptions(self, timestamp: int = 0) -> dict:

        response, cookies = http_request(self._addon,
                                         self._NEXTCLOUD_API["subscriptions"] % (self._host, timestamp), self._get_auth())

        return json.loads(response)


