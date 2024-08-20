import requests
from veracode_api_signing.plugin_requests import RequestsAuthPluginVeracodeHMAC
import xml.etree.ElementTree as ET
import time
import argparse
import os

# Constantes para los endpoints de la API de Veracode
BASE_URL = 'https://analysiscenter.veracode.com/api/5.0/'
PDF_BASE_URL = 'https://analysiscenter.veracode.com/api/4.0/'
GET_APP_LIST_ENDPOINT = 'getapplist.do'
UPLOAD_FILE_ENDPOINT = 'uploadfile.do'
BEGINPRESCAN_ENDPOINT = 'beginprescan.do'
GET_BUILD_INFO_ENDPOINT = 'getbuildinfo.do'
DETAILEDREPORTPDF_ENDPOINT = 'detailedreportpdf.do'

# Función para listar las aplicaciones disponibles
def list_apps():
    url = BASE_URL + GET_APP_LIST_ENDPOINT
    auth = RequestsAuthPluginVeracodeHMAC()
    try:
        response = requests.get(url, auth=auth)
        response.raise_for_status()

        root = ET.fromstring(response.text)
        namespace = {'ns': 'https://analysiscenter.veracode.com/schema/2.0/applist'}

        for app in root.findall('ns:app', namespace):
            app_id = app.get('app_id')
            app_name = app.get('app_name')
            print(f"App Name: {app_name}, App ID: {app_id}")

    except requests.exceptions.RequestException as e:
        print(f"Error en la solicitud getapplist: {e}")

# Función para subir un archivo para su análisis
def upload_file(app_id, file_path):
    url = BASE_URL + UPLOAD_FILE_ENDPOINT
    auth = RequestsAuthPluginVeracodeHMAC()

    with open(file_path, 'rb') as file:
        files = {'file': file}
        data = {'app_id': app_id}

        try:
            response = requests.post(url, auth=auth, files=files, data=data)
            response.raise_for_status()
            print("Archivo subido con éxito. Código de estado:", response.status_code)
        except requests.exceptions.RequestException as e:
            print(f"Error en la solicitud upload_file: {e}")

# Función para iniciar un preescan
def begin_prescan(app_id):
    url = BASE_URL + BEGINPRESCAN_ENDPOINT
    auth = RequestsAuthPluginVeracodeHMAC()
    data = {'app_id': app_id}

    try:
        response = requests.post(url, auth=auth, data=data)
        response.raise_for_status()

        root = ET.fromstring(response.text)
        build_id = root.attrib['build_id']
        print("Preescan iniciado con éxito. Código de estado:", response.status_code)
        return build_id

    except requests.exceptions.RequestException as e:
        print(f"Error en la solicitud begin_prescan: {e}")
        return None

# Función para verificar el estado del escaneo
def check_scan_status(app_id, build_id):
    url = BASE_URL + GET_BUILD_INFO_ENDPOINT
    auth = RequestsAuthPluginVeracodeHMAC()
    params = {'app_id': app_id, 'build_id': build_id}

    while True:
        try:
            response = requests.get(url, auth=auth, params=params)
            response.raise_for_status()

            response_xml = response.text
            if ' results_ready="true"' in response_xml:
                print("El escaneo está completo y los resultados están listos.")
                break
            else:
                print("El escaneo aún no está completo. Verificando nuevamente en 30 segundos...")

        except requests.exceptions.RequestException as e:
            print(f"Error en la solicitud getbuildinfo: {e}")
        time.sleep(30)

# Función para obtener el reporte detallado en formato PDF
def get_detailed_report_pdf(build_id):
    url = PDF_BASE_URL + DETAILEDREPORTPDF_ENDPOINT
    auth = RequestsAuthPluginVeracodeHMAC()
    params = {'build_id': build_id}

    try:
        response = requests.get(url, auth=auth, params=params)
        response.raise_for_status()

        # Determinar la ruta absoluta para la carpeta "reports"
        root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        reports_dir = os.path.join(root_dir, 'reports')

        # Crear la carpeta "reports" si no existe
        os.makedirs(reports_dir, exist_ok=True)

        # Guardar el reporte PDF en la carpeta "reports"
        pdf_filename = os.path.join(reports_dir, f'detailed_report_{build_id}.pdf')
        with open(pdf_filename, 'wb') as file:
            file.write(response.content)

        print(f"El informe PDF ha sido guardado como '{pdf_filename}'.")

    except requests.exceptions.RequestException as e:
        print(f"Error en la solicitud detailedreportpdf: {e}")

# Función principal
def main():
    parser = argparse.ArgumentParser(description='Script para interactuar con la API XML de Veracode.')
    parser.add_argument('--list_apps', action='store_true', help='Lista todas las aplicaciones con sus IDs.')
    parser.add_argument('--app_id', type=str, help='El ID de la aplicación.')
    parser.add_argument('--file_path', type=str, help='La ruta del archivo a analizar.')

    args = parser.parse_args()

    if args.list_apps:
        list_apps()
    elif args.app_id and args.file_path:
        upload_file(args.app_id, args.file_path)
        build_id = begin_prescan(args.app_id)

        if build_id:
            check_scan_status(args.app_id, build_id)
            get_detailed_report_pdf(build_id)
    else:
        print("Debe especificar '--list_apps' para listar las aplicaciones o '--app_id' y '--file_path' para realizar un análisis.")

if __name__ == '__main__':
    main()
