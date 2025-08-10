import sys
import urllib.parse
import xbmcgui
import xbmcplugin
import xbmcaddon
import json
import urllib.request
import xml.etree.ElementTree as ET
import re

# --- Configuración de tu Addon ---
EXTERNAL_MENU_URL = "https://raw.githubusercontent.com/GMKTEC/karaokebonny2025/main/bienvenida.xml"
INTRO_VIDEO_URL = "https://www.youtube.com/watch?v=TjycZ8xMmDk"

class KaraokeAddon:
    def init(self):
        self.addon_handle = int(sys.argv[1])
        self.addon = xbmcaddon.Addon()
        self.addon_path = self.addon.getAddonInfo('path')
        self.addon_id = self.addon.getAddonInfo('id')
        self.base_url = sys.argv[0]

    def build_url(self, query):
        return f"{self.base_url}?{urllib.parse.urlencode(query)}"

    def log(self, message, level=xbmc.LOGINFO):
        xbmc.log(f"[{self.addon_id}] {message}", level)

    def show_notification(self, message, title=None, time=5000):
        if title is None:
            title = self.addon.getAddonInfo('name')
        xbmcgui.Dialog().notification(title, message, time=time)

    def get_items_from_xml_url(self, xml_url):
        self.log(f"Intentando descargar y parsear XML de: {xml_url}")
        try:
            with urllib.request.urlopen(xml_url) as response:
                xml_data = response.read()

            root = ET.fromstring(xml_data)
            parsed_items = []

            if root.tag == 'items':
                for item_elem in root.findall('item'):
                    item_data = {}
                    for child in item_elem:
                        item_data[child.tag] = child.text if child.text is not None else ''
                    parsed_items.append(item_data)

            elif root.tag == 'channels':
                for channel_elem in root.findall('channel'):
                    channel_data = {}
                    for child in channel_elem:
                        if child.tag != 'items':
                            channel_data[child.tag] = child.text if child.text is not None else ''
        except Exception as e:
            self.log(f"Error al procesar XML: {e}", level=xbmc.LOGERROR)
            self.show_notification("Error al cargar el menú. Revisa el log de Kodi.")
            return []
        return parsed_items

def play_intro_video():
    """Reproduce el video de intro."""
    list_item = xbmcgui.ListItem()
    list_item.setInfo('video', {'title': 'Intro'})
    xbmcplugin.setResolvedUrl(int(sys.argv[1]), True, list_item)
    xbmc.Player().play(INTRO_VIDEO_URL, list_item)

def main():
    addon = KaraokeAddon()
    params = dict(urllib.parse.parse_qsl(sys.argv[2][1:]))
    mode = params.get('mode', 'main')

    if mode == 'main':
        play_intro_video()
        items = addon.get_items_from_xml_url(EXTERNAL_MENU_URL)
        addon.add_menu_items(items)

    xbmcplugin.endOfDirectory(addon.addon_handle)

if name == 'main':
    main()p
