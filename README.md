# veracode-xmlapi-script
Análisis estático y generación de archivo xml con los resultados.

# Veracode API Script

Este script permite interactuar con la API de Veracode para subir archivos, iniciar un prescan, verificar el estado del escaneo y obtener un informe detallado.

## Requisitos

- Python 3.x
- Paquetes: requests, veracode_api_signing

## Instalación

Clona el repositorio y navega al directorio:

```bash
git clone https://github.com/<tu-usuario>/veracode-api-script.git
cd veracode-api-script

## Administrar credenciales de API

Seguir los pasos descritos en la documentación para administrar correctamente las credenciales. 
Link: https://docs.veracode.com/r/c_api_credentials3

## Manual de uso
El script tiene dos funcionalidades principales que puedes ejecutar desde la línea de comandos:

Listar Aplicaciones
Subir un Archivo y Ejecutar un Escaneo

#Opción 1: Listar Aplicaciones
Esta opción lista todas las aplicaciones disponibles en tu cuenta de Veracode.

Comando para listar aplicaciones:
python tu_script.py --list_apps

Esto ejecutará la función list_apps(), que hará una solicitud a la API de Veracode para obtener la lista de aplicaciones y sus IDs. Imprimirá los nombres y IDs de las aplicaciones en la consola.


#Opción 2: Subir un Archivo y Ejecutar un Escaneo
Esta opción permite subir un archivo a Veracode y luego ejecutar un escaneo prescan. Después, verifica el estado del escaneo y descarga el informe detallado.

Preparación del comando:
Necesitarás proporcionar dos argumentos: --app_id (ID de la aplicación) y --file_path (ruta del archivo que deseas analizar).

Comando para subir un archivo y ejecutar un escaneo:
python tu_script.py --app_id <ID_DE_LA_APLICACION> --file_path <RUTA_DEL_ARCHIVO>

Reemplaza <ID_DE_LA_APLICACION> con el ID de la aplicación donde deseas subir el archivo.
Reemplaza <RUTA_DEL_ARCHIVO> con la ruta al archivo que deseas analizar.

##El flujo será el siguiente:

1. Subir el archivo: Se ejecuta upload_file(app_id, file_path), que sube el archivo a Veracode.
2. Iniciar el prescan: Se ejecuta begin_prescan(app_id), que inicia el escaneo prescan para la aplicación y devuelve el build_id.
3. Verificar el estado del escaneo: Se ejecuta check_scan_status(app_id, build_id), que consulta repetidamente el estado del escaneo hasta que los resultados estén listos.
4. Obtener el informe detallado: Se ejecuta get_detailed_report(build_id), que descarga el informe detallado y lo guarda en detailed_report.xml.

#Ejemplo de Uso
Supongamos que quieres listar aplicaciones en Veracode:
python tu_script.py --list_apps

Si deseas subir un archivo para el escaneo, por ejemplo, para la aplicación con ID 2194204 y el archivo está en path/to/your/file.zip, usarías:
python tu_script.py --app_id "2194204" --file_path "path/to/your/file.zip"

#Nota Adicional
-Asegúrate de que el archivo a subir esté accesible y la ruta proporcionada sea correcta.
-La autenticación HMAC para RequestsAuthPluginVeracodeHMAC debe estar correctamente configurada con tus credenciales de Veracode.
-El script usa un bucle para esperar el estado del escaneo y consulta cada 30 segundos. Puedes ajustar el tiempo de espera según sea necesario.
