# veracode-xmlapi-script
Este repositorio contiene un script en Python que interactúa con la API XML de Veracode para realizar operaciones como listar aplicaciones, subir archivos, iniciar prescans y descargar informes detallados en formato PDF.

## Requisitos
- Python 3.x
- Paquetes listados en requirements.txt

## Administrar credenciales de API
Seguir los pasos descritos en la documentación para administrar correctamente las credenciales. 
Link: https://docs.veracode.com/r/c_api_credentials3

# Configuración del Entorno
Es recomendable usar un entorno virtual para evitar conflictos de dependencias. Sigue estos pasos:

1. Crear el entorno virtual:
```bash
python -m venv env
```

2.Activar el entorno virtual:

En Windows:
```bash
.\env\Scripts\activate
```

En macOS/Linux:
```bash
source env/bin/activate
```

3.Instalar las dependencias:
```bash
pip install -r requirements.txt
```

# Estructura del Proyecto
La estructura del proyecto es la siguiente:
```bash
entornov/
│
├── env/                 # Carpeta del entorno virtual (NO pongas los reportes aquí)
│   ├── Lib/
│   ├── Scripts/
│   └── ...
│
├── src/                 # Carpeta donde está tu código fuente
│   └── veracode_script.py               # Tu script principal
│
├── reports/             # Carpeta donde se guardarán los reportes generados
│   └── detailed_report.pdf    # Tu reporte de scan
│
└── requirements.txt     # Dependencias del proyecto
```

# Manual de uso
El script tiene dos funcionalidades principales que puedes ejecutar desde la línea de comandos:

Listar Aplicaciones
Subir un Archivo y Ejecutar un Escaneo

## Opción 1: Listar Aplicaciones
Esta opción lista todas las aplicaciones disponibles en tu cuenta de Veracode.

Comando para listar aplicaciones:
```bash
python src/tu_script.py --list_apps
```
Esto ejecutará la función list_apps(), que hará una solicitud a la API de Veracode para obtener la lista de aplicaciones y sus IDs. Imprimirá los nombres y IDs de las aplicaciones en la consola.


## Opción 2: Subir un Archivo y Ejecutar un Escaneo
Esta opción permite subir un archivo a Veracode y luego ejecutar un escaneo prescan. Después, verifica el estado del escaneo y descarga el informe detallado.

Preparación del comando:
Necesitarás proporcionar dos argumentos: --app_id (ID de la aplicación) y --file_path (ruta del archivo que deseas analizar).

Comando para subir un archivo y ejecutar un escaneo:
```bash
python src/tu_script.py --app_id <ID_DE_LA_APLICACION> --file_path <RUTA_DEL_ARCHIVO>
```
Reemplaza <ID_DE_LA_APLICACION> con el ID de la aplicación donde deseas subir el archivo.
Reemplaza <RUTA_DEL_ARCHIVO> con la ruta al archivo que deseas analizar.

## El flujo será el siguiente:

1. Subir el archivo: Se ejecuta upload_file(app_id, file_path), que sube el archivo a Veracode.
2. Iniciar el prescan: Se ejecuta begin_prescan(app_id), que inicia el escaneo prescan para la aplicación y devuelve el build_id.
3. Verificar el estado del escaneo: Se ejecuta check_scan_status(app_id, build_id), que consulta repetidamente el estado del escaneo hasta que los resultados estén listos.
4. Obtener el informe detallado: Se ejecuta get_detailed_report(build_id), que descarga el informe detallado y lo guarda en detailed_report.xml.
5. Descarga y guarda el archivo "detailed_report.pdf" de reporte del scan en la carpeta "reportes".

# Ejemplo de Uso
Supongamos que quieres listar aplicaciones en Veracode:
```bash
python src/tu_script.py --list_apps
```

Si deseas subir un archivo para el escaneo, por ejemplo, para la aplicación con ID 2194204 y el archivo está en path/to/your/file.zip, usarías:
```bash
python src/tu_script.py --app_id "2194204" --file_path "path/to/your/file.zip"
```

# Nota Adicional
-Asegúrate de que el archivo a subir esté accesible y la ruta proporcionada sea correcta.
-La autenticación HMAC para RequestsAuthPluginVeracodeHMAC debe estar correctamente configurada con tus credenciales de Veracode.
-El script usa un bucle para esperar el estado del escaneo y consulta cada 30 segundos. Puedes ajustar el tiempo de espera según sea necesario.
