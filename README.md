# Terraquipu Data 🛰️🌱

> **Ciencia de Datos Geoespaciales, Pipelines Satelitales NASA y Modelado Agronómico Andino**  
> *Parte del ecosistema [Terraquipu](https://github.com/TerraQuipu)*

---

## 📌 Propósito del Repositorio

`terraquipu-data` alberga el cerebro de datos y la ciencia agroclimática de Terraquipu. Este repositorio es responsable de:
1. Extraer y procesar series temporales históricas y actuales de **NASA POWER** (precipitación y temperaturas) para calcular anomalías de **El Niño**.
2. Obtener diagnósticos edáficos globales a resolución de 250 m mediante la **API REST de SoilGrids v2.0** (ISRIC).
3. Construir y validar la **Matriz Agronómica Andina** (`crop_matrix.json`) basada en las guías técnicas del **INIA** y **SENAMHI**.
4. Desarrollar el **Algoritmo de Scoring Multicriterio Determinista** (`scoring_engine.py`) que califica la viabilidad de rotación sin depender de modelos de lenguaje opacos.

---

## 👥 Equipo y Roles Asignados

| Integrante | Rol | Responsabilidad en el Sprint de 48h |
| :--- | :--- | :--- |
| **Ing. Ambiental** | **Agronomía & Salud del Suelo Lead** | Definición de umbrales fenológicos (requerimientos hídricos en mm, límites térmicos, pH, fijación de nitrógeno biológico en kg/ha) y validación de reglas de rotación sucesiva según manuales del INIA. |
| **Ciencia de Datos** | **Geodata & Modelado Matemático Lead** | Scripts de ingesta de NASA POWER y SoilGrids, cálculo de índices de sequía / anomalías climáticas, normalización de variables y desarrollo del motor multicriterio (`scoring_engine.py`). |

---

## 🛰️ Fuentes de Datos y APIs Integradas

### 1. NASA POWER API (Meteorología y Agroclimatología)
* **Endpoint:** `GET https://power.larc.nasa.gov/api/temporal/daily/point?parameters=T2M,T2M_MAX,T2M_MIN,PRECTOTCORR,RH2M&community=AG&longitude={lon}&latitude={lat}&start=YYYYMMDD&end=YYYYMMDD&format=JSON`
* **Variables:** `PRECTOTCORR` (precipitación con corrección de sesgo), `T2M_MAX`/`T2M_MIN` (temperaturas extremas).
* **Uso:** Detección de anomalías respecto a la climatología histórica de 20 años.

### 2. ISRIC SoilGrids v2.0 REST API
* **Endpoint:** `GET https://rest.isric.org/soilgrids/v2.0/properties/query?lon={lon}&lat={lat}&property=phh2o&property=soc&property=nitrogen&property=clay&depth=0-5cm&depth=5-15cm&value=mean`
* **Variables:** `phh2o` (pH), `soc` (carbono orgánico g/kg), `nitrogen` (nitrógeno total), `clay` (% arcilla).
* **Uso:** Diagnóstico basal de la fertilidad y capacidad de retención de agua de la parcela.

### 3. Open-Meteo Elevation (SRTM DEM 90m/30m)
* **Endpoint:** `GET https://api.open-meteo.com/v1/elevation?latitude={lat}&longitude={lon}`
* **Uso:** Determinación del piso altitudinal andino (Quechua, Suni, Puna) y cálculo de pendiente.

---

## 📁 Archivos Centrales del Repositorio

* **`crop_matrix.json` (Contrato 1):** Base de datos agronómica de cultivos andinos (Papa Nativa, Tarwi, Quinua) con sus tolerancias edafoclimáticas y balances de nutrientes.
* **`scoring_engine.py`:** Algoritmo que calcula el puntaje de idoneidad (0–100%) ponderando:
  $$\text{Score} = w_1 \cdot \text{Balance Hídrico} + w_2 \cdot \text{Riesgo Térmico} + w_3 \cdot \text{Regeneración de Suelo} + w_4 \cdot \text{Corte de Plagas}$$
* **`notebooks/`:** Exploración de datos, visualización de series temporales y mapas de anomalías en Cusco.

---

## 💻 Instalación y Uso de Scripts

```bash
# 1. Clonar el repositorio
git clone https://github.com/TerraQuipu/terraquipu-data.git
cd terraquipu-data

# 2. Crear entorno virtual
python -m venv venv
# Activar entorno (Windows):
venv\Scripts\activate
# Activar entorno (Linux/macOS):
source venv/bin/activate

# 3. Instalar librerías científicas
pip install requests pandas numpy geopandas matplotlib jupyter

# 4. Probar el motor de scoring multicriterio
python scoring_engine.py
```
