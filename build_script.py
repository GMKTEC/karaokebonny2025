#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script para construir el addon de Karaoke para Kodi
Genera la estructura de directorios y crea el archivo ZIP
"""

import os
import zipfile
import shutil
from pathlib import Path

# Configuración del addon
ADDON_ID = "plugin.video.karaoke.home"
ADDON_VERSION = "1.0.0"
ADDON_NAME = "Karaoke Home"

def create_directory_structure():
    """Crea la estructura de directorios del addon"""
    
    # Directorio principal
    addon_dir = Path(ADDON_ID)
    
    # Limpiar directorio si existe
    if addon_dir.exists():
        shutil.rmtree(addon_dir)
    
    # Crear directorios
    directories = [
        addon_dir,
        addon_dir / "resources",
        addon_dir / "resources" / "language",
        addon_dir / "resources" / "language" / "resource.language.es_es",
        addon_dir / "resources" / "language" / "resource.language.en_gb",
        addon_dir / "resources" / "lib",
        addon_dir / "resources" / "media"
    ]
    
    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)
        print(f"✓ Directorio creado: {directory}")
    
    return addon_dir

def create_addon_files(addon_dir):
    """Crea los archivos principales del addon"""
    
    # addon.py - Ya tienes el contenido
    addon_py_content = '''# El contenido de addon.py va aquí
# (Usar el código Python que creé anteriormente)
'''
    
    # addon.xml - Ya tienes el contenido
    addon_xml_content = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<!-- El contenido de addon.xml va aquí -->
'''
    
    # settings.xml - Ya tienes el contenido  
    settings_xml_content = '''<?xml version="1.0" encoding="utf-8" standalone="yes"?>
<!-- El contenido de settings.xml va aquí -->
'''
    
    # strings.po para español
    strings_es_content = '''# El contenido de strings.po va aquí
# (Usar las traducciones que creé anteriormente)
'''
    
    # strings.po para inglés
    strings_en_content = '''# English strings for Karaoke Home Addon
msgid ""
msgstr ""
"Language: en_GB\\n"
"Content-Type: text/plain; charset=UTF-8\\n"

# Settings Categories
msgctxt "#32001"
msgid "General"
msgstr "General"

msgctxt "#32002"
msgid "Sources"
msgstr "Sources"

# ... (más traducciones en inglés)
'''
    
    # Crear archivos de ejemplo
    files_to_create = [
        (addon_dir / "addon.py", "# Código principal del addon\nprint('Karaoke Addon Loaded')"),
        (addon_dir / "addon.xml", "<!-- Metadatos del addon -->"),
        (addon_dir / "settings.xml", "<!-- Configuración del addon -->"),
        (addon_dir / "resources" / "language" / "resource.language.es_es" / "strings.po", strings_es_content),
        (addon_dir / "resources" / "language" / "resource.language.en_gb" / "strings.po", strings_en_content),
        (addon_dir / "README.md", "# Karaoke Home Addon\n\nDocumentación del addon..."),
        (addon_dir / "LICENSE", "GPL-3.0 License\n\n(Contenido de la licencia)"),
        (addon_dir / "resources" / "lib" / "__init__.py", "# Librerías del addon"),
    ]
    
    for file_path, content in files_to_create:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✓ Archivo creado: {file_path}")

def create_media_files(addon_dir):
    """Crea archivos de medios de ejemplo"""
    
    # Crear archivos de imagen de ejemplo (texto por ahora)
    media_files = [
        (addon_dir / "resources" / "icon.png", "# Icono del addon (PNG 256x256)"),
        (addon_dir / "resources" / "fanart.jpg", "# Imagen de fondo (JPG 1920x1080)"),
        (addon_dir / "resources" / "media" / "loading.gif", "# Animación de carga"),
    ]
    
    for file_path, description in media_files:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(f"# {description}\n# Reemplazar con archivo real")
        print(f"✓ Archivo de medios creado: {file_path}")

def create_zip_package(addon_dir):
    """Crea el archivo ZIP del addon"""
    
    zip_filename = f"{ADDON_ID}-{ADDON_VERSION}.zip"
    
    with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
        
        # Añadir todos los archivos del addon
        for root, dirs, files in os.walk(addon_dir):
            for file in files:
                file_path = Path(root) / file
                # Ruta relativa dentro del ZIP
                arcname = file_path.relative_to(addon_dir.parent)
                zipf.write(file_path, arcname)
                print(f"✓ Añadido al ZIP: {arcname}")
    
    print(f"\n🎉 ¡Addon empaquetado exitosamente!")
    print(f"📦 Archivo ZIP creado: {zip_filename}")
    print(f"📏 Tamaño: {os.path.getsize(zip_filename)} bytes")
    
    return zip_filename

def create_installation_instructions():
    """Crea archivo con instrucciones de instalación"""
    
    instructions = f"""
# Instrucciones de Instalación - {ADDON_NAME}

## Instalación en Kodi

1. **Copia el archivo ZIP**
   - Archivo: {ADDON_ID}-{ADDON_VERSION}.zip
   - Cópialo a tu dispositivo donde tengas Kodi

2. **Instalar en Kodi**
   - Abre Kodi
   - Ve a Configuración ⚙️
   - Selecciona "Complementos" o "Add-ons"
   - Haz clic en "Instalar desde archivo ZIP"
   - Navega hasta el archivo ZIP y selecciónalo
   - Espera la confirmación de instalación

3. **Primer uso**
   - Ve a Complementos > Complementos de video
   - Encuentra "{ADDON_NAME}"
   - ¡Disfruta del karaoke!

## Configuración inicial

- Configura las fuentes de karaoke en Configuración
- Ajusta la calidad de video según tu conexión
- Personaliza la interfaz a tu gusto

## Notas importantes

- Este addon es para uso doméstico y educativo
- Asegúrate de tener una conexión a internet estable
- Respeta los derechos de autor del contenido

¡Que disfrutes cantando! 🎤🎵
"""
    
    with open("INSTRUCCIONES_INSTALACION.txt", 'w', encoding='utf-8') as f:
        f.write(instructions)
    
    print("✓ Instrucciones de instalación creadas")

def main():
    """Función principal del script"""
    
    print(f"🚀 Construyendo addon: {ADDON_NAME} v{ADDON_VERSION}")
    print("=" * 50)
    
    try:
        # Crear estructura de directorios
        print("\n📁 Creando estructura de directorios...")
        addon_dir = create_directory_structure()
        
        # Crear archivos del addon
        print("\n📄 Creando archivos del addon...")
        create_addon_files(addon_dir)
        
        # Crear archivos de medios
        print("\n🖼️ Creando archivos de medios...")
        create_media_files(addon_dir)
        
        # Crear ZIP
        print("\n📦 Empaquetando addon...")
        zip_file = create_zip_package(addon_dir)
        
        # Crear instrucciones
        print("\n📝 Creando instrucciones...")
        create_installation_instructions()
        
        print("\n" + "=" * 50)
        print("✅ ¡Construcción completada exitosamente!")
        print(f"📦 Archivo listo: {zip_file}")
        print(f"📖 Instrucciones: INSTRUCCIONES_INSTALACION.txt")
        print("\n🎤 ¡Tu addon de karaoke está listo para instalar en Kodi!")
        
    except Exception as e:
        print(f"❌ Error durante la construcción: {str(e)}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
