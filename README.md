# Sistema Multipropósito de IA para la Comisión Corográfica del Siglo XXI

[![License: CC BY 4.0](https://img.shields.io/badge/License-CC%20BY%204.0-lightgrey.svg)](https://creativecommons.org/licenses/by/4.0/)
[![Python Version](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
![Streamlit](https://img.shields.io/badge/Frontend-Streamlit-red)
![GEE](https://img.shields.io/badge/Satellite-Google%20Earth%20Engine-green)
![AI](https://img.shields.io/badge/AI-Llama3%20%7C%20RandomForest-purple)

## Descripción

Este proyecto es un prototipo de sistema geoespacial impulsado por IA, diseñado para apoyar la comprensión y gestión del territorio colombiano, especialmente en zonas periféricas. Inspirado en la histórica Comisión Corográfica (1849-1859), busca democratizar el acceso a datos abiertos sobre biodiversidad, servicios ecosistémicos y recursos naturales. El sistema permite delimitar áreas de interés, extraer información de Datos Abiertos como IDEAM, SIPRA, NASA (GEDI, Landsat), ESA (Sentinel) y GBIF, calcular métricas ambientales (biomasa aérea, captación de CO2, biodiversidad), generar informes automatizados con Quarto y consultar via chatbot.

El objetivo es empoderar comunidades étnicas, campesinas y excombatientes, facilitando procesos como Concesiones Forestales Campesinas y contribuyendo a la paz, desarrollo sostenible y mitigación climática.

Esta es una iniciativa en el marco del concurso Datos al Ecosistema - 2025 del MinTIC.

### Problemática Abordada
Colombia enfrenta un desconocimiento territorial que fomenta conflictos y precariedad. Este sistema integra IA para generar conocimiento actualizado, involucrando comunidades locales.

### Impactos Esperados
- **Social**: Democratiza datos para comunidades y excombatientes.
- **Económico**: Agiliza acceso a fondos (bonos carbono, PSA).
- **Ambiental**: Identifica hotspots de biodiversidad y captación potencial de CO2.

## 📂 Estructura del Proyecto

```bash
comision_corografica_ia/
├── src/                  # Código fuente modular
│   ├── polygons/         # Generación de polígonos
│   ├── apis/             # Integraciones con APIs externas (datos.gov.co, GBIF)
│   ├── analysis/         # Extracción y cálculos (rasters, vectores, satélites, ML)
│   ├── reports/          # Generación de informes (Quarto)
│   └── chatbot/          # Lógica del chatbot (Groq/Llama)
├── data/                 # Datos
│   ├── raw/              # Datos originales (CSVs, GPKGs)
│   └── processed/        # Outputs intermedios
├── notebooks/            # Prototipos y algoritmos en desarrollo
├── tests/                # Pruebas unitarias
├── docs/                 # Documentación y templates Quarto
├── config/               # Configuraciones (.env, yaml)
├── static/               # Assets para UI (imágenes)
├── main.py               # Frontend Streamlit
├── README.md             # Este archivo
├── .gitignore            # Ignora archivos no versionados
├── pyproject.toml        # Dependencias con UV
└── uv.lock               # Lockfile de dependencias
```

---

## 🛠️ Fuentes de Datos Utilizadas

El sistema integra fuentes de datos abiertos nacionales e internacionales para garantizar precisión y transparencia.

| Nombre de la Fuente | Descripción | Tipo de Acceso | Enlace Oficial |
| :--- | :--- | :--- | :--- |
| **Cambio de Coberturas Boscosas (IDEAM)** | Raster que identifica Bosque estable, Deforestación y Restauración (2021-2022). | Descarga (Datos Abiertos) | [Datos.gov.co](https://www.datos.gov.co/Ambiente-y-Desarrollo-Sostenible/Cambio-en-la-superficie-cubierta-por-bosque-natura/39dh-rc72/about_data) |
| **Frontera Agrícola (UPRA/SIPRA)** | Datos vectoriales que delimitan la frontera agrícola nacional, condicionantes y exclusiones (Jun 2025). | Descarga (Datos Abiertos) | [Datos.gov.co](https://www.datos.gov.co/Agricultura-y-Desarrollo-Rural/Identificaci-n-de-la-frontera-agr-cola-y-frontera-/fyc7-sbtz/about_data) |
| **Vectores Base (IGAC/DANE)** | Capas de referencia: Centros Poblados, Vías, Límites Municipales/Departamentales, Veredas. | Descarga | [Colombia en Mapas](https://www.colombiaenmapas.gov.co/) |
| **Áreas Protegidas (RUNAP)** | Registro Único Nacional de Áreas Protegidas (Parques Nacionales, Reservas). | Descarga | [RUNAP / Colombia en Mapas](https://www.colombiaenmapas.gov.co/) |
| **Territorios Étnicos y Campesinos** | Polígonos de Consejos Comunitarios, Resguardos Indígenas y Zonas de Reserva Campesina. | Descarga | [Colombia en Mapas](https://www.colombiaenmapas.gov.co/) |
| **NASA GEDI L4A** | Densidad de Biomasa Aérea (LiDAR en la Estación Espacial Internacional). | API Google Earth Engine | [GEDI Mission](https://gedi.umd.edu/) |
| **Sentinel-2 (ESA)** | Imágenes ópticas multiespectrales para índices de vegetación (NDVI, SAVI). | API Google Earth Engine | [Copernicus ESA](https://sentinels.copernicus.eu/) |
| **Global Canopy Height (Meta)** | Mapa de altura de árboles a 1m de resolución (IA sobre imágenes satelitales). | API Google Earth Engine | [Meta Forest Monitoring](https://gee-community-catalog.org/projects/meta_trees/) |
| **SRTM (NASA)** | Modelo Digital de Elevación del terreno (Topografía). | API Google Earth Engine | [NASA EarthData](https://www.earthdata.nasa.gov/data/instruments/srtm) |
| **GBIF** | Registros biológicos históricos (observaciones y colectas) georreferenciados. | API REST (PyGBIF) | [GBIF API](https://techdocs.gbif.org/en/openapi/) |

---

## Acceso a la data utilizada
[Data](https://drive.google.com/drive/folders/1BsUhES4dArZy-bwCSDxKqgNs06zU3cIM?usp=sharing)

## Equipo

Somos un equipo de 4 personas apasionadas por la ciencia de datos, el impacto ambiental y la equidad territorial. Cada uno contribuye con su experiencia para hacer realidad esta visión de la Comisión Corográfica del Siglo XXI.

- **Carlos Fernando Betancur Morales**: Administrador Ambiental. Rol: Líder técnico, comunicador.
- **Paula Andrea Castro Espinal**: Ingeniera de Sistemas. Rol: Desarrolladora.
- **Mario Alejandro Ortegón Gonzalez**: Ingeniero Físico. Rol: Científico de Datos.
- **Santiago Restrepo Calle**: Administrador Ambiental. Rol: Ingeniero de Datos.

## Licencia
Creative Commons Attribution 4.0 International (CC BY 4.0). Ver [LICENSE](LICENSE) para detalles.