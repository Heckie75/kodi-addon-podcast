# kodi-addon-deutschlandfunk
KODI Addon für Deutschlandfunk, Deutschlandfunk Kultur und Deutschlandfunk Nova für Livestream und Podcasts

Dieses Projekt stellt ein Addon für das KODI Mediacenter bereit, mit dem die Radioprogramme des Deutschlandfunks gehört werden können. Es können sowohl die Live Streams vom Deutschlandfunk, Deutschlandfunk Kultur und Deutschlandfunk Nova als auch sämtliche Podcasts der Sender bezogen werden.

## Features
* Live-Streams der Radiosender Deutschlandfunk, Deutschlandfunk Kultur und Deutschlandfunk Nova
* Streamen aller Podcasts dieser Sender

<img src="plugin.audio.deutschlandfunk/resources/assets/screen.png?raw=true">

## Voraussetzungen

Dieses Addon benötigt mehrere Pythonbibliotheken. Diese sollten weitestgehend Bestandteil einer gewöhnlichen Python sein.

Die Bibliothek ```lxml``` ist manuell zu installieren:

```
sudo apt install python-lxml
```

Weiterhin benutzt das Addon die Pythonbibliothek [xmltodict](https://github.com/martinblech/xmltodict) von Martín Blech, die aber nicht installiert werden braucht, da der Code bereits im Addon integriert ist.

## Installation
Für die Installation ist folgendes Archiv zu downloaden:
[plugin.audio.deutschlandfunk.tgz](/plugin.audio.deutschlandfunk.tgz)

Das Archiv ist im KODI-Addon Verzeichnis zu entpacken. Auf Ubuntu Systemen ist dieses Kodi-Verzeichnis unterhalb des home-Verzeichnisses zu finden:
```
# In das Kodi-Addon Verzeichnis wechseln
$ cd ~/.kodi/addons/

# Archiv-Datei auspackem
$ tar xzf ~/Downloads/plugin.audio.deutschlandfunk.tgz
```

KODI muss neu gestartet werden.
1. Start Kodi
2. In das "Addons" Menü wechseln
3. "Benutzer Addons" auswählen
4. Musik Addons wählen, "Deutschlandfunk" wählen und das Addon aktivieren

Fertig!

## Disclaimer
Dieses Addon ist als Programmierbeispiel zu verstehen, um aufzuzeigen, wie Addons dieser Art, insbesondere die Umwandlung von RSS Feeds zu Abspiellisten in KODI, unter Einbeziehung von XML Parsern entwickelt werden können. Durch die Bereitstellung dieses Addons wird nicht die tatsächliche Nutzung beabsichtigt. Es gelten die Regelungen der MIT License:

```
MIT License

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```
