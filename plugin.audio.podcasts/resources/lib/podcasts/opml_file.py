
import xmltodict

def parse_opml(data):

    def parse_outlines_from_opml(outline):

        if type(outline) is not list:
            outline = [outline]

        entries = []
        for i, o in enumerate(outline):
            name = o["@title"] if "@title" in o else o["@text"]
            if not name and "@xmlUrl" in o:
                m = re.match(
                    "^https?:\/\/([^\/]+).*\/?.*\/([^\/]+)\/?$", o["@xmlUrl"])
                if m:
                    name = "%s %s...%s" % (self.addon.getLocalizedString(
                        32053), m.groups()[0][:20], m.groups()[1][-40:])

            entry = {
                "path": str(i),
                "name": name,
                "node": []
            }

            if "@type" in o and o["@type"] == "rss" and "@xmlUrl" in o:
                entry["params"] = [{
                    "rss": o["@xmlUrl"]
                }]
                entries.append(entry)

            elif "outline" in o:
                entry["node"] = parse_outlines_from_opml(
                    o["outline"])
                entries.append(entry)

        return entries

    opml_data = xmltodict.parse(data)

    entries = parse_outlines_from_opml(
        opml_data["opml"]["body"]["outline"])

    return opml_data["opml"]["head"]["title"], entries

def open_opml_file(path):

    with open(path) as _opml_file:
        return _opml_file.read()