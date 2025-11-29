import requests
import pandas as pd

def descargar_datos_soda(api_id, formato='json', limite=None, where=None, output_file=None):
    """
    Descarga datos desde la SODA API del Portal Nacional de Datos Abiertos de Colombia.
    
    Parámetros:
    - api_id: string. Identificador del conjunto de datos (dataset) en datos.gov.co
    - formato: 'json' o 'csv' (por defecto 'json')
    - limite: int o None — si se quiere limitar la cantidad de filas
    - where: string o None — cláusula WHERE (SODA) para filtrar resultados
    - output_file: str o None — si se indica, el resultado se guarda en archivo con este nombre
    
    Retorna:
    - pandas.DataFrame con los datos descargados
    """
    base_url = f"https://www.datos.gov.co/resource/{api_id}.{formato}"
    params = {}
    if limite is not None:
        params['$limit'] = limite
    if where is not None:
        params['$where'] = where  # por ejemplo: "year = 2023"
    
    resp = requests.get(base_url, params=params)
    resp.raise_for_status()
    
    if formato == 'json':
        data = resp.json()
        df = pd.DataFrame(data)
    else:
        # formato == 'csv'
        from io import StringIO
        df = pd.read_csv(StringIO(resp.text))
    
    if output_file:
        df.to_csv(output_file, index=False, encoding='utf-8')
        print(f"Guardado en {output_file}")
    return df


if __name__ == "__main__":
    # Ejemplo de uso:
    api_id = 'tu_api_id_aqui'  # <-- reemplaza por el ID real del conjunto de datos
    # Descarga hasta 500 filas:
    df = descargar_datos_soda(api_id, formato='json', limite=500)
    print(df.head())
