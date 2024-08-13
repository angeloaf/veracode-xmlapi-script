import requests
from veracode_api_signing.plugin_requests import RequestsAuthPluginVeracodeHMAC
import xml.etree.ElementTree as ET
import time
import argparse

# URL base de la API de Veracode
BASE_URL = 'https://analysiscenter.veracode.com/api/5.0/'
GET_APP_LIST_ENDPOINT = 'getapplist.do'
UPLOAD_FILE_ENDPOINT = 'uploadfile.do'
BEGINPRESCAN_ENDPOINT = 'beginprescan.do'
GET_BUILD_INFO_ENDPOINT = 'getbuildinfo.do'
DETAILEDREPORT_ENDPOINT = 'detailedreport.do'

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

def upload_file(app_id, file_path):
    url = BASE_URL + UPLOAD_FILE_ENDPOINT
    auth = RequestsAuthPluginVeracodeHMAC()
    
    # Leer el archivo en modo binario
    with open(file_path, 'rb') as file:
        files = {'file': file}
        data = {'app_id': app_id}
        
        try:
            # Realizar la solicitud POST
            response = requests.post(url, auth=auth, files=files, data=data)
            response.raise_for_status()  # Lanza una excepción para códigos de estado HTTP 4xx/5xx
            print("Request to upload_file successful. Status code:", response.status_code)
            print("Response text:", response.text)
        except requests.exceptions.RequestException as e:
            print(f"Error en la solicitud upload_file: {e}")

def begin_prescan(app_id):
    url = BASE_URL + BEGINPRESCAN_ENDPOINT
    auth = RequestsAuthPluginVeracodeHMAC()
    
    # Datos de la solicitud
    data = {'app_id': app_id}
    
    try:
        # Realizar la solicitud POST
        response = requests.post(url, auth=auth, data=data)
        response.raise_for_status()  # Lanza una excepción para códigos de estado HTTP 4xx/5xx

        root = ET.fromstring(response.text)

        # Extraer los valores de app_id y build_id
        app_id = root.attrib['app_id']
        build_id = root.attrib['build_id']

        print("Request to begin_prescan successful. Status code:", response.status_code)
        print("Response text:", response.text)
        
        return build_id  # Devolver el build_id
        
    except requests.exceptions.RequestException as e:
        print(f"Error en la solicitud begin_prescan: {e}")
        return None

def check_scan_status(app_id, build_id):
    url = BASE_URL + GET_BUILD_INFO_ENDPOINT
    auth = RequestsAuthPluginVeracodeHMAC()
    
    # Datos de la solicitud
    params = {'app_id': app_id, 'build_id': build_id}
    
    while True:
        try:
            # Realizar la solicitud GET
            response = requests.get(url, auth=auth, params=params)
            response.raise_for_status()  # Lanza una excepción para códigos de estado HTTP 4xx/5xx
            
            # Procesar la respuesta
            if response.ok:
                response_xml = response.text
                if ' results_ready="true"' in response_xml:
                    root = ET.fromstring(response_xml)

                    # Extraer los valores de app_id y build_id
                    app_id = root.attrib['app_id']
                    build_id = root.attrib['build_id']
                    print("El escaneo está completo y los resultados están listos.")
                    break  # Salir del bucle ya que los resultados están listos
                else:
                    print("El escaneo aún no está completo. Resultados listos:", ' results_ready="true"' in response_xml)
            else:
                print("Error en la solicitud getbuildinfo. Código de estado:", response.status_code)
                print("Respuesta del servidor:", response.text)
        except requests.exceptions.RequestException as e:
            print(f"Error en la solicitud getbuildinfo: {e}")

        # Esperar unos segundos antes de la próxima solicitud
        time.sleep(30)

def get_detailed_report(build_id):
    url = BASE_URL + DETAILEDREPORT_ENDPOINT
    auth = RequestsAuthPluginVeracodeHMAC()
    
    # Datos de la solicitud
    params = {'build_id': build_id}
    
    try:
        # Realizar la solicitud GET
        response = requests.get(url, auth=auth, params=params)
        response.raise_for_status()  # Lanza una excepción para códigos de estado HTTP 4xx/5xx
        
        # Guardar la respuesta en un archivo XML
        with open('detailed_report.xml', 'w', encoding='utf-8') as file:
            file.write(response.text)
        
        print("Request to detailedreport successful. Status code:", response.status_code)
        print("The detailed report has been saved to 'detailed_report.xml'.")
    except requests.exceptions.RequestException as e:
        print(f"Error en la solicitud detailedreport: {e}")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Script para interactuar con la API XML de Veracode.')
    parser.add_argument('--list_apps', action='store_true', help='Lista todas las aplicaciones con sus IDs.')
    parser.add_argument('--app_id', type=str, help='El ID de la aplicación.')
    parser.add_argument('--file_path', type=str, help='La ruta del archivo a analizar.')
    
    args = parser.parse_args()
    
    if args.list_apps:
        list_apps()
    elif args.app_id and args.file_path:
        # Ejecutar la carga del archivo
        upload_file(args.app_id, args.file_path)
        
        # Ejecutar el prescan
        build_id = begin_prescan(args.app_id)
        
        if build_id:
            # Verificar el estado del escaneo
            check_scan_status(args.app_id, build_id)
            
            # Ejecutar la solicitud del informe detallado
            get_detailed_report(build_id)
    else:
        print("Debe especificar '--list_apps' para listar las aplicaciones o '--app_id' y '--file_path' para realizar un análisis.")
