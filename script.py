import requests
from veracode_api_signing.plugin_requests import RequestsAuthPluginVeracodeHMAC
import xml.etree.ElementTree as ET
import time

# URL base de la API de Veracode
BASE_URL = 'https://analysiscenter.veracode.com/api/5.0/'
GET_APP_LIST_ENDPOINT = 'getapplist.do'
UPLOAD_FILE_ENDPOINT = 'uploadfile.do'
BEGINPRESCAN_ENDPOINT = 'beginprescan.do'
GET_BUILD_INFO_ENDPOINT = 'getbuildinfo.do'
DETAILEDREPORT_ENDPOINT = 'detailedreport.do'

def get_app_id(app_name):
    url = BASE_URL + GET_APP_LIST_ENDPOINT
    auth = RequestsAuthPluginVeracodeHMAC()
    try:
        # Realizar la solicitud GET
        response = requests.get(url, auth=auth)
        response.raise_for_status()  # Lanza una excepción para códigos de estado HTTP 4xx/5xx
        
        # Parsear el XML de la respuesta
        root = ET.fromstring(response.text)
        
        # Buscar la aplicación por nombre y devolver el app_id
        namespace = {'ns': 'https://analysiscenter.veracode.com/schema/2.0/applist'}
        for app in root.findall('ns:app', namespace):
            if app.get('app_name') == app_name:
                return app.get('app_id')
        
        print(f"Aplicación con nombre '{app_name}' no encontrada.")
        return None
        
    except requests.exceptions.RequestException as e:
        print(f"Error en la solicitud getapplist: {e}")
        return None

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
    # Solicitar el nombre de la aplicación por consola
    app_name = input("Introduce el nombre de la aplicación: ")
    
    # Obtener el app_id
    app_id = get_app_id(app_name)
    if app_id:
        print(f"El ID de la aplicación '{app_name}' es: {app_id}")
        
        # Solicitar datos de entrada por consola
        file_path = input("Introduce la ruta del archivo a subir: ")
        
        # Ejecutar la carga del archivo
        upload_file(app_id, file_path)
        
        # Ejecutar el prescan
        build_id = begin_prescan(app_id)
        
        if build_id:
            # Verificar el estado del escaneo
            check_scan_status(app_id, build_id)
            
            # Ejecutar la solicitud del informe detallado
            get_detailed_report(build_id)
    else:
        print(f"No se encontró la aplicación con nombre '{app_name}'.")
