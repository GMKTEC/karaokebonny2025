import sys
import urllib.parse
import xbmcgui
import xbmcplugin
import xbmcaddon
import json
import urllib.request
import xml.etree.ElementTree as ET # Importa para manejar XML
import re # ¡IMPORTANTE! Necesario para las expresiones regulares de YouTube

# --- Configuración de tu Addon ---
# ¡IMPORTANTE! Esta URL DEBE apuntar a tu 'bienvenida.xml'
# que contiene la lista de artistas/categorías principales.
EXTERNAL_MENU_URL = "https://raw.githubusercontent.com/GMKTEC/karaokebonny2025/main/bienvenida.xml"

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
        Descarga y parsea un archivo XML desde una URL.
        Puede manejar XMLs con una raíz <items> (como bienvenida.xml)
        o <channels> (como cumbias.xml y otros XML de artistas).
        Retorna una lista de diccionarios con los datos de los ítems/canales.
        """
        self.log(f"Intentando descargar y parsear XML de: {xml_url}")
        try:
            with urllib.request.urlopen(xml_url) as response:
                xml_data = response.read()
            
            root = ET.fromstring(xml_data)
            parsed_items = []

            # Lógica para manejar XMLs con raíz <items> (como bienvenida.xml)
            if root.tag == 'items':
                for item_elem in root.findall('item'):
                    item_data = {}
                    for child in item_elem:
                        # Asegura que el texto no sea None, reemplazándolo con cadena vacía
                        item_data[child.tag] = child.text if child.text is not None else '' 
                    parsed_items.append(item_data)
            
            # Lógica para manejar XMLs con raíz <channels> (como cumbias.xml, vanesamartin.xml, etc.)
            elif root.tag == 'channels':
                for channel_elem in root.findall('channel'):
                    channel_data = {}
                    # Recopila los datos del canal (nombre, thumbnail, fanart)
                    for child in channel_elem:
                        if child.tag != 'items': # No procesar el tag 'items' directamente aquí
                            channel_data[child.tag] = child.text if child.text is not None else ''

                    # Si el canal contiene items (canciones) dentro de un tag <items> anidado
                    items_elem = channel_elem.find('items')
                    if items_elem is not None:
                        for item_elem in items_elem.findall('item'):
                            song_data = {}
                            for child in item_elem:
                                song_data[child.tag] = child.text if child.text is not None else ''
                            
                            # Combina los datos del canal (artista) con los de la canción
                            # Esto permite que las canciones hereden thumbnail/fanart del artista si no tienen uno propio
                            combined_data = {**channel_data, **song_data} 
                            parsed_items.append(combined_data)
                    else:
                        # Si es un <channel> sin <items> anidados (ej. una categoría de artista que no tiene canciones directamente,
                        # sino que es un sub-menú que apunta a otro XML con canciones)
                        # Aunque tu bienvenida.xml ya maneja esto, esta rama es para flexibilidad si usas <channel> sin items.
                        parsed_items.append(channel_data)

            self.log(f"XML parseado exitosamente. Se encontraron {len(parsed_items)} ítems/canales.")
            return parsed_items
        except Exception as e:
            self.log(f"Error al descargar o parsear XML de {xml_url}: {e}", xbmc.LOGERROR)
            self.show_notification("Error al cargar contenido externo", "Karaoke Home")
            return []

    def display_xml_items(self, items):
        """
        Muestra los ítems de una lista de diccionarios (obtenidos de un XML) en Kodi.
        Esta función manejará tanto el menú principal como los sub-menús (categorías y canciones).
        """
        if not items:
            self.show_notification("No se pudieron cargar los ítems.", "Error")
            xbmcplugin.endOfDirectory(self.addon_handle, succeeded=False)
            return

        for item_data in items:
            title = item_data.get('title', 'Sin título')
            thumbnail = item_data.get('thumbnail', '')
            fanart = item_data.get('fanart', '')
            info = item_data.get('info', '')
            
            # Etiqueta para enlaces a otros XML (carpetas)
            externallink = item_data.get('externallink', '') 
            # Etiqueta para URLs directas de video/audio (canciones)
            url_video_audio = item_data.get('url', '') 

            list_item = xbmcgui.ListItem(label=title)
            list_item.setArt({'thumb': thumbnail, 'fanart': fanart})
            
            if info:
                list_item.setInfo('video', {'plot': info})

            url_to_add = ''
            is_folder = False 

            if externallink:
                # Si el externallink termina en .xml, es una carpeta que carga otro XML
                if externallink.endswith('.xml'):
                    is_folder = True
                    url_to_add = self.build_url({'mode': 'load_external_xml', 'url': externallink})
                else:
                    # Si externallink no es XML, no tiene acción definida como carpeta o reproducible
                    self.log(f"Advertencia: externallink '{externallink}' no es un XML y no tiene acción definida.", xbmc.LOGWARNING)
                    url_to_add = '' 
            elif url_video_audio:
                is_folder = False # No es una carpeta
                url_to_add = '' # Inicializar

                # ASUMIMOS que url_video_audio ahora contiene directamente el ID de YouTube (11 caracteres)
                # o una URL COMPLETA de YouTube.

                # Intentamos extraer el ID de YouTube de cualquier formato.
                # Esta expresión regular es más robusta y captura el ID tanto de URLs estándar
                # como si directamente le pasamos el ID.
                video_id_match = re.search(r'(?:v=|youtu\.be/|embed/|)([a-zA-Z0-9_-]{11})', url_video_audio)
                
                if video_id_match:
                    video_id = video_id_match.group(1)
                    # Aseguramos que solo usamos el ID si es de 11 caracteres
                    if len(video_id) == 11:
                        url_to_add = f"plugin://plugin.video.youtube/play/?video_id={video_id}"
                        list_item.setProperty('IsPlayable', 'true')
                        self.log(f"ID de YouTube detectado y convertido: {url_to_add}")
                    else:
                        self.log(f"Advertencia: El ID extraído '{video_id}' no es un ID de YouTube válido (11 caracteres). URL: {url_video_audio}", xbmc.LOGWARNING)
                        url_to_add = '' # No se puede reproducir con el plugin de YouTube
                else:
                    # Si no es un ID de YouTube ni una URL de YouTube, se asume que es una URL directa reproducible por Kodi
                    # y la pasamos tal cual. (Esto cubre MP4, etc. si los tuvieras)
                    url_to_add = url_video_audio
                    list_item.setProperty('IsPlayable', 'true')
                    self.log(f"URL directa de video/audio detectada: {url_to_add}")

            else:
                # Si no tiene ni externallink ni url_video_audio, no es navegable ni reproducible
                self.log(f"Advertencia: Ítem '{title}' no tiene externallink ni url de video/audio.", xbmc.LOGWARNING)
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
        elif mode == 'load_external_xml': # Modo para cargar un XML desde una URL
            self.log(f"Cargando XML externo para sub-menú: {url}")
            items = self.get_items_from_xml_url(url)
            self.display_xml_items(items)
        # El modo 'play' se mantiene aquí por si se necesita una lógica de reproducción más compleja
        # o para otros tipos de enlaces que no sean YouTube directos.
        # Por ahora, la reproducción de YouTube se maneja directamente en display_xml_items
        # al construir la URL para el addon de YouTube.
        elif mode == 'play':
            # En este caso, 'url' del parámetro ya debería ser la URL lista para reproducir
            video_url = params.get('url_to_play') # Asegúrate de que este parámetro se pase si usas este modo
            title = params.get('title')
            artist = params.get('artist', '')
            self.play_karaoke(video_url, title, artist)
        else:
            self.log(f"Modo desconocido: {mode}", xbmc.LOGWARNING)

    def play_karaoke(self, url, title, artist):
        self.log(f"Preparando para reproducir: {title} por {artist} desde {url}")
        try:
            play_item = xbmcgui.ListItem(path=url)
            play_item.setInfo('video', {'title': title, 'artist': [artist]})
            # Importante: Kodi necesita saber que este ítem es reproducible
            play_item.setProperty('IsPlayable', 'true') 
            xbmcplugin.setResolvedUrl(self.addon_handle, True, play_item)
        except Exception as e:
            self.log(f"Error al intentar reproducir video: {e}", xbmc.LOGERROR)
            self.show_notification("Error al reproducir video", "Karaoke Home")


# --- Ejecución principal del script ---
if __name__ == '__main__':
    karaoke_addon = KaraokeAddon()
    karaoke_addon.router(sys.argv[2][1:]) # Quitar el '?' inicial
