from resources.lib.podcasts.podcastsaddon import PodcastsAddon
from resources.lib.podcasts.actions.import_gpodder_subscriptions_action import ImportGPodderSubscriptionsAction
from resources.lib.podcasts.actions.import_opml_action import ImportOpmlAction
from resources.lib.podcasts.actions.unassign_opml_action import UnassignOpmlAction
import sys

if __name__ == '__main__':

    if sys.argv[1] == "import_gpodder_subscriptions":
        importGPodderSubscriptionsAction = ImportGPodderSubscriptionsAction(
            int(sys.argv[1]))
        importGPodderSubscriptionsAction.import_gpodder_subscriptions(
            "True" == sys.argv[2])

    elif sys.argv[1] == "import_opml":
        importOpmlAction = ImportOpmlAction(int(sys.argv[1]))
        importOpmlAction.import_opml()

    elif sys.argv[1] == "download_gpodder_subscriptions":
        importGPodderSubscriptionsAction = ImportGPodderSubscriptionsAction(
            int(sys.argv[1]))
        importGPodderSubscriptionsAction.import_gpodder_subscriptions()

    elif sys.argv[1] == "unassign_opml":
        unassignOpmlAction = UnassignOpmlAction(int(sys.argv[1]))
        unassignOpmlAction.unassign_opml()

    else:
        podcastsAddon = PodcastsAddon(int(sys.argv[1]))
        podcastsAddon.handle(sys.argv)
