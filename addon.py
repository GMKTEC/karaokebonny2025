import sys
import urllib.parse
import xbmcgui
import xbmcplugin
import xbmcaddon
import json
import urllib.request
import xml.etree.ElementTree as ET # Importa para manejar XML

# --- Configuración de tu Addon ---
# Reemplaza esta URL con la URL Raw de tu archivo XML en GitHub
# ¡Esta es la que me acabas de pasar!
EXTERNAL_MENU_URL = "EXTERNAL_MENU_URL = "https://raw.githubusercontent.com/GMKTEC/karaokebonny2025/main/bienvenida.xml""

class KaraokeAddon:
    def __init__(self):
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
        """
        Descarga y parsea un archivo XML desde una URL, retornando una lista de diccionarios.
        """
        self.log(f"Intentando descargar y parsear XML de: {xml_url}")
        try:
            with urllib.request.urlopen(xml_url) as response:
                xml_data = response.read()
            
            root = ET.fromstring(xml_data)
            items = []
            for item_elem in root.findall('item'):
                item_data = {}
                for child in item_elem:
                    # Almacena el texto de la etiqueta
                    item_data[child.tag] = child.text
                items.append(item_data)
            self.log(f"XML parseado exitosamente. Se encontraron {len(items)} ítems.")
            return items
        except Exception as e:
            self.log(f"Error al descargar o parsear XML de {xml_url}: {e}", xbmc.LOGERROR)
            self.show_notification("Error al cargar contenido externo", "Karaoke Home")
            return []

    def display_xml_items(self, items):
        """
        Muestra los ítems de una lista de diccionarios (obtenidos de un XML) en Kodi.
        Esta función manejará tanto el menú principal como los sub-menús.
        """
        if not items:
            self.show_notification("No se pudieron cargar los ítems.", "Error")
            xbmcplugin.endOfDirectory(self.addon_handle, succeeded=False)
            return

        for item_data in items:
            title = item_data.get('title', 'Sin título')
            thumbnail = item_data.get('thumbnail', '')
            fanart = item_data.get('fanart', '')
            externallink = item_data.get('externallink', '')
            info = item_data.get('info', '')
            
            # Si en un futuro tus XML de canciones tienen 'videoid', puedes añadirlo aquí
            # videoid = item_data.get('videoid', '') 
            
            list_item = xbmcgui.ListItem(label=title)
            list_item.setArt({'thumb': thumbnail, 'fanart': fanart})
            
            # Si hay info, la ponemos en el plot (descripción)
            if info:
                list_item.setInfo('video', {'plot': info})

            # Lógica para determinar si el ítem es una carpeta o un elemento final (reproducible/externo)
            url_to_add = ''
            is_folder = False # Por defecto, no es una carpeta
            
            if externallink:
                # Si el externallink termina en .xml, lo tratamos como una carpeta que carga otro XML
                if externallink.endswith('.xml'):
                    is_folder = True
                    # El modo 'load_external_xml' cargará el XML de ese externallink
                    url_to_add = self.build_url({'mode': 'load_external_xml', 'url': externallink})
                # Si el externallink es una URL web directa, no es una carpeta para Kodi,
                # y necesitarías una acción para abrirla en un navegador externo.
                # Por ahora, si no es XML o videoid, simplemente no es navegable dentro de Kodi.
                elif externallink.startswith('http://') or externallink.startswith('https://'):
                     # Ejemplo para abrir navegador externo (requiere Kodi 18+)
                     # url_to_add = self.build_url({'mode': 'open_external_browser', 'url': externallink})
                     # is_folder = False
                     # Pero por ahora, no tiene acción directa en Kodi si no es un XML o video
                     url_to_add = '' # No añade acción si no es XML ni video
                # Si tienes videoid en otros XML de canciones, lo procesarías aquí
                # elif videoid:
                #     is_folder = False
                #     url_to_add = self.build_url({
                #         'mode': 'play',
                #         'videoid': videoid,
                #         'title': title,
                #         'artist': item_data.get('artist', '') 
                #     })
                else:
                    # Cualquier otro externallink que no sea XML o videoid, no lo manejamos como carpeta/reproducible por defecto
                    url_to_add = ''
            
            # Añadir el ítem al directorio si tiene una URL de acción
            if url_to_add:
                xbmcplugin.addDirectoryItem(
                    handle=self.addon_handle,
                    url=url_to_add,
                    listitem=list_item,
                    isFolder=is_folder
                )
        xbmcplugin.endOfDirectory(self.addon_handle)

    def main_menu(self):
        """Muestra el menú principal del addon cargado desde EXTERNAL_MENU_URL."""
        self.log("Cargando menú principal desde XML externo.")
        items = self.get_items_from_xml_url(EXTERNAL_MENU_URL)
        self.display_xml_items(items)

    # --- Router para manejar los modos ---
    def router(self, paramstring):
        params = dict(urllib.parse.parse_qsl(paramstring))
        mode = params.get('mode', None)
        url = params.get('url', '') # Para capturar la URL en el nuevo modo

        if mode is None:
            self.main_menu()
        elif mode == 'load_external_xml': # Nuevo modo para cargar un XML desde una URL
            self.log(f"Cargando XML externo para sub-menú: {url}")
            items = self.get_items_from_xml_url(url)
            self.display_xml_items(items)
        elif mode == 'play':
            videoid = params.get('videoid')
            title = params.get('title')
            artist = params.get('artist')
            youtube_url = f"plugin://plugin.video.youtube/play/?video_id={videoid}"
            self.play_karaoke(youtube_url, title, artist)
        # Puedes añadir otros modos si los necesitas, como para búsqueda local, etc.
        # elif mode == 'open_external_browser':
        #     import xbmc
        #     xbmc.executebuiltin(f'RunScript(special://home/addons/script.module.urlresolver/lib/urlresolver/thirdparty/simple_browser.py?url={url})')
        #     self.log(f"Abriendo enlace externo en navegador: {url}")
        else:
            self.log(f"Modo desconocido: {mode}", xbmc.LOGWARNING)

    # Asegúrate de que tu función play_karaoke existe si la usas con el modo 'play'
    # Si aún no la tienes, aquí te dejo una versión simple:
    def play_karaoke(self, url, title, artist):
        self.log(f"Preparando para reproducir: {title} por {artist} desde {url}")
        try:
            # La URL ya debería venir lista para el addon de YouTube
            play_item = xbmcgui.ListItem(path=url)
            play_item.setInfo('video', {'title': title, 'artist': [artist]}) # Asegúrate de que el artista es una lista
            xbmcplugin.setResolvedUrl(self.addon_handle, True, play_item)
        except Exception as e:
            self.log(f"Error al intentar reproducir video: {e}", xbmc.LOGERROR)
            self.show_notification("Error al reproducir video", "Karaoke Home")


# --- Ejecución principal del script ---
if __name__ == '__main__':
    karaoke_addon = KaraokeAddon()
    karaoke_addon.router(sys.argv[2][1:]) # Quitar el '?' inicial
