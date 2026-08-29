# ETL para reconstrucción de bibliotecas patrimoniales históricas

Herramienta diseñada bajo el marco de las Humanidades Digitales para la extracción, normalización relacional y análisis estadístico de catálogos antiguos. El sistema cruza metadatos bibliográficos institucionales (MARC/XML) con evidencia material y archivística.

## Arquitectura del Sistema

El *pipeline* está diseñado bajo estrictos principios de ingeniería de datos para garantizar su agnosticismo, escalabilidad y reproducibilidad:

* **Arquitectura Medallón:** El flujo de datos transita por capas progresivas (Bronce para extracción cruda, Plata para grafos relacionales en JSON, y Oro para el cruce matricial analítico).
* **Paradigma Data-Driven:** La lógica informática se encuentra aislada de las decisiones historiográficas. Toda regla semántica, diccionario de normalización y umbral de filtrado reside en el directorio `/config/`.
* **Patrones de Diseño:** Implementación de Patrón *Factory* para instanciar conectores (Z39.50 y SRU) y patrón *MVC* (Modelo-Vista-Controlador) en la capa de consumo analítico.

## Estructura del Repositorio

    ├── config/             # Archivos de configuración y diccionarios semánticos
    ├── data/               # Directorio base de datos (raw, procesada, reportes)
    ├── scripts/            # Utilidades de limpieza y auditoría manual de datos
    ├── src/
    │   ├── libreria/       # Módulos reutilizables (conectores, visualización)
    │   └── pipeline/       # Controladores principales (ETL)
    └── tests/              # Sondas de conectividad y pruebas de unidad

## Ejecución

1. Instalar las dependencias exactas del entorno:
   `pip install -r requirements.txt`
2. Ejecutar la fase de extracción definiendo el catálogo objetivo:
   `python src/pipeline/01_extraccion.py --catalogo bnmm`
3. Transformar los datos hacia la Capa Plata (JSON):
   `python src/pipeline/02_transformacion.py`
4. Generar reportes estadísticos y gráficos de redes:
   `python src/pipeline/03_analisis.py`

## Licencia

Este software se distribuye bajo la Licencia Pública General de GNU (GPLv3).
