# Sistema Multipropósito de IA para la Comisión Corográfica del Siglo XXI

[![License: CC BY 4.0](https://img.shields.io/badge/License-CC%20BY%204.0-lightgrey.svg)](https://creativecommons.org/licenses/by/4.0/)
[![Python Version](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)

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

## Equipo

Somos un equipo de 4 personas apasionadas por la ciencia de datos, el impacto ambiental y la equidad territorial. Cada uno contribuye con su experiencia para hacer realidad esta visión de la Comisión Corográfica del Siglo XXI.

- **Carlos Fernando Betancur Morales**: Administrador Ambiental. Rol: Líder técnico, comunicador.
- **Paula Andrea Castro Espinal**: Ingeniera de Sistemas. Rol: Desarrolladora.
- **Mario Alejandro Ortegón Gonzalez**: Ingeniero Físico. Rol: Científico de Datos.
- **Santiago Restrepo Calle**: Administrador Ambiental. Rol: Ingeniero de Datos.

## Licencia
Creative Commons Attribution 4.0 International (CC BY 4.0). Ver [LICENSE](LICENSE) para detalles.