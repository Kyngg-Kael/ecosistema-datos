from pygbif import maps
import os

def descargar_mapa(taxon_key, z=0, x=0, y=0,
                   output_filename='mapa.png', 
                   style='classic.point', format='@1x.png'):
    """
    Descarga un tile del mapa para un taxon dado usando la Maps API de GBIF.
    """
    result = maps.map(taxonKey=taxon_key, z=z, x=x, y=y,
                      format=format, style=style)
    # `result.img` contiene los bytes de imagen
    with open(output_filename, 'wb') as f:
        f.write(result.img)
    print(f'Mapa guardado en {output_filename}')
