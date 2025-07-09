# 📚 Documentación Técnica - Pipeline ETL

## 🏗️ Arquitectura del Sistema

### Diagrama de Arquitectura

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   FUENTES DE    │    │   PIPELINE      │    │   DESTINO       │
│     DATOS       │    │      ETL        │    │                 │
├─────────────────┤    ├─────────────────┤    ├─────────────────┤
│ • CSV Files     │───▶│ • Extract       │───▶│ • SQLite DB    │
│ • APIs          │    │ • Transform     │    │ • Reports       │
│ • Databases     │    │ • Load          │    │ • Visualizations│
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### Componentes Principales

#### 1. **Extractors** (`src/extractors/`)
- **DataExtractor**: Clase principal para extraer datos
- Soporte para múltiples fuentes:
  - Archivos CSV
  - APIs REST (simuladas)
  - Bases de datos SQLite
- Validación de datos extraídos
- Manejo de errores robusto

#### 2. **Transformers** (`src/transformers/`)
- **DataTransformer**: Clase principal para transformar datos
- Funcionalidades:
  - Limpieza de datos (duplicados, valores nulos)
  - Validación de tipos de datos
  - Transformaciones específicas por tabla
  - Creación de tablas derivadas
  - Manejo de outliers

#### 3. **Loaders** (`src/loaders/`)
- **DataLoader**: Clase principal para cargar datos
- Características:
  - Creación automática de esquemas
  - Carga masiva de datos
  - Creación de índices
  - Estadísticas de carga
  - Consultas personalizadas

#### 4. **Utils** (`src/utils/`)
- **ConfigLoader**: Gestión de configuración YAML
- **Logger**: Sistema de logging personalizado
- **ReportGenerator**: Generación de reportes y visualizaciones

## 🔧 Configuración del Sistema

### Archivo de Configuración (`config/config.yaml`)

```yaml
project:
  name: "ETL E-commerce Analytics"
  version: "1.0.0"

paths:
  data_raw: "data/raw"           # Datos sin procesar
  data_processed: "data/processed" # Datos procesados
  data_reports: "data/reports"   # Reportes generados
  logs: "logs"                   # Archivos de log

database:
  type: "sqlite"
  path: "data/processed/ecommerce_analytics.db"
  tables: ["ventas", "productos", "clientes", "categorias"]

validation:
  required_columns:
    ventas: ["id", "fecha", "producto_id", "cliente_id", "cantidad", "precio"]
    productos: ["id", "nombre", "categoria", "precio"]
    clientes: ["id", "nombre", "email", "ciudad"]

cleaning:
  remove_duplicates: true
  fill_missing:
    strategy: "forward"
    numeric: 0
    categorical: "Unknown"
  outliers:
    method: "iqr"
    threshold: 1.5
```

## 📊 Esquema de Base de Datos

### Tablas Principales

#### 1. **ventas**
```sql
CREATE TABLE ventas (
    id INTEGER PRIMARY KEY,
    fecha DATETIME NOT NULL,
    producto_id INTEGER NOT NULL,
    cliente_id INTEGER NOT NULL,
    cantidad INTEGER NOT NULL,
    precio REAL NOT NULL,
    total REAL NOT NULL,
    mes INTEGER,
    año INTEGER,
    dia_semana TEXT
);
```

#### 2. **productos**
```sql
CREATE TABLE productos (
    id INTEGER PRIMARY KEY,
    nombre TEXT NOT NULL,
    categoria TEXT NOT NULL,
    precio REAL NOT NULL,
    stock INTEGER,
    descripcion TEXT
);
```

#### 3. **clientes**
```sql
CREATE TABLE clientes (
    id INTEGER PRIMARY KEY,
    nombre TEXT NOT NULL,
    email TEXT NOT NULL,
    ciudad TEXT NOT NULL,
    telefono TEXT,
    fecha_registro DATETIME
);
```

### Tablas Derivadas

#### 1. **ventas_por_producto**
```sql
CREATE TABLE ventas_por_producto (
    producto_id INTEGER PRIMARY KEY,
    cantidad_total INTEGER NOT NULL,
    total_ventas REAL NOT NULL,
    num_ventas INTEGER NOT NULL,
    nombre_producto TEXT,
    categoria TEXT
);
```

#### 2. **ventas_por_cliente**
```sql
CREATE TABLE ventas_por_cliente (
    cliente_id INTEGER PRIMARY KEY,
    cantidad_total INTEGER NOT NULL,
    total_compras REAL NOT NULL,
    num_compras INTEGER NOT NULL,
    nombre_cliente TEXT,
    ciudad TEXT
);
```

#### 3. **ventas_por_categoria**
```sql
CREATE TABLE ventas_por_categoria (
    categoria TEXT PRIMARY KEY,
    cantidad_total INTEGER NOT NULL,
    total_ventas REAL NOT NULL,
    num_ventas INTEGER NOT NULL
);
```

## 🔄 Flujo de Datos

### 1. **Extracción (Extract)**
```python
# Ejemplo de extracción
extractor = DataExtractor(config)
raw_data = extractor.extract_all()

# Resultado: Dict[str, pd.DataFrame]
{
    'ventas': DataFrame(...),
    'productos': DataFrame(...),
    'clientes': DataFrame(...),
    'categorias': DataFrame(...),
    'inventario': DataFrame(...)
}
```

### 2. **Transformación (Transform)**
```python
# Ejemplo de transformación
transformer = DataTransformer(config)
transformed_data = transformer.transform_all(raw_data)

# Transformaciones aplicadas:
# - Limpieza de datos
# - Validación de tipos
# - Creación de columnas derivadas
# - Generación de tablas agregadas
```

### 3. **Carga (Load)**
```python
# Ejemplo de carga
loader = DataLoader(config)
success = loader.load_all(transformed_data)

# Resultado: Base de datos SQLite con todas las tablas
```

## 📈 Reportes y Visualizaciones

### Tipos de Reportes Generados

1. **Reportes de Ventas**
   - Ventas por día (gráfico de líneas)
   - Ventas por categoría (gráfico de barras)
   - Top productos más vendidos (gráfico horizontal)

2. **Reportes de Productos**
   - Estado del inventario (gráfico de barras con colores)
   - Productos con stock bajo (indicadores)

3. **Reportes de Clientes**
   - Top clientes (gráfico horizontal)
   - Ventas por ciudad (gráfico de barras)

4. **Reporte General**
   - Métricas principales (dashboard)
   - Resumen ejecutivo

### Formatos de Salida

- **Gráficos**: PNG (alta resolución)
- **Datos**: CSV
- **Reporte completo**: HTML interactivo
- **Métricas**: JSON

## 🧪 Testing

### Estructura de Tests

```
tests/
├── __init__.py
└── test_etl_pipeline.py
```

### Tipos de Tests

1. **Tests Unitarios**
   - ConfigLoader
   - DataExtractor
   - DataTransformer
   - DataLoader

2. **Tests de Integración**
   - Pipeline completo
   - Validación de datos
   - Manejo de errores

3. **Tests de Datos**
   - Limpieza de datos
   - Transformaciones específicas

### Ejecutar Tests

```bash
# Ejecutar todos los tests
pytest tests/ -v

# Ejecutar con cobertura
pytest tests/ --cov=src --cov-report=html

# Ejecutar tests específicos
pytest tests/test_etl_pipeline.py::TestETLPipeline::test_data_extractor -v
```

## 🔍 Consultas SQL de Ejemplo

### Análisis de Ventas

```sql
-- Top 10 productos más vendidos
SELECT 
    vpp.nombre_producto,
    vpp.total_ventas,
    vpp.num_ventas,
    ROUND(vpp.total_ventas / vpp.num_ventas, 2) as ticket_promedio
FROM ventas_por_producto vpp
ORDER BY vpp.total_ventas DESC
LIMIT 10;

-- Ventas por mes
SELECT 
    v.año,
    v.mes,
    COUNT(*) as num_ventas,
    SUM(v.total) as total_ventas,
    AVG(v.total) as ticket_promedio
FROM ventas v
GROUP BY v.año, v.mes
ORDER BY v.año, v.mes;

-- Clientes más valiosos
SELECT 
    vpc.nombre_cliente,
    vpc.ciudad,
    vpc.total_compras,
    vpc.num_compras,
    ROUND(vpc.total_compras / vpc.num_compras, 2) as ticket_promedio
FROM ventas_por_cliente vpc
ORDER BY vpc.total_compras DESC
LIMIT 10;
```

### Análisis de Inventario

```sql
-- Productos con stock bajo
SELECT 
    p.nombre,
    p.categoria,
    i.stock_actual,
    i.stock_minimo,
    CASE 
        WHEN i.stock_actual <= i.stock_minimo THEN 'CRÍTICO'
        WHEN i.stock_actual <= i.stock_minimo * 1.5 THEN 'BAJO'
        ELSE 'OK'
    END as estado_stock
FROM inventario i
JOIN productos p ON i.producto_id = p.id
WHERE i.stock_actual <= i.stock_minimo * 1.5
ORDER BY i.stock_actual ASC;

-- Análisis de categorías
SELECT 
    p.categoria,
    COUNT(*) as num_productos,
    AVG(p.precio) as precio_promedio,
    SUM(i.stock_actual) as stock_total,
    COUNT(CASE WHEN i.stock_bajo = 1 THEN 1 END) as productos_stock_bajo
FROM productos p
JOIN inventario i ON p.id = i.producto_id
GROUP BY p.categoria
ORDER BY num_productos DESC;
```

## 🚀 Optimizaciones y Mejoras

### Optimizaciones Implementadas

1. **Procesamiento por Lotes**
   - Carga de datos en chunks
   - Procesamiento paralelo donde es posible

2. **Índices de Base de Datos**
   - Índices en columnas frecuentemente consultadas
   - Optimización de consultas

3. **Manejo de Memoria**
   - Procesamiento eficiente de DataFrames
   - Limpieza automática de memoria

### Posibles Mejoras Futuras

1. **Escalabilidad**
   - Soporte para bases de datos distribuidas
   - Procesamiento en paralelo con multiprocessing

2. **Monitoreo**
   - Métricas de rendimiento
   - Alertas automáticas

3. **Automatización**
   - Programación de tareas (cron jobs)
   - Integración con orquestadores (Airflow)

4. **Seguridad**
   - Encriptación de datos sensibles
   - Autenticación y autorización

## 🐛 Troubleshooting

### Problemas Comunes

#### 1. **Error de Importación**
```bash
# Solución: Instalar dependencias
pip install -r requirements.txt
```

#### 2. **Error de Permisos**
```bash
# Solución: Verificar permisos de directorios
chmod -R 755 data/
chmod -R 755 logs/
```

#### 3. **Error de Base de Datos**
```bash
# Solución: Verificar que SQLite esté disponible
python -c "import sqlite3; print('SQLite OK')"
```

#### 4. **Error de Memoria**
```python
# Solución: Reducir tamaño de chunks
config.set('processing.chunk_size', 1000)
```

### Logs y Debugging

Los logs se guardan en `logs/` con diferentes niveles:
- `info.log`: Información general
- `error.log`: Errores y excepciones
- `debug.log`: Información detallada

Para activar modo debug:
```python
logger = setup_logger(level="DEBUG")
```

## 📚 Referencias y Recursos

### Documentación de Librerías
- [pandas](https://pandas.pydata.org/docs/)
- [SQLAlchemy](https://docs.sqlalchemy.org/)
- [matplotlib](https://matplotlib.org/stable/contents.html)
- [seaborn](https://seaborn.pydata.org/)

### Mejores Prácticas
- [Python ETL Best Practices](https://www.databricks.com/blog/2017/10/30/from-etl-to-streaming-with-apache-kafka-and-databricks.html)
- [Data Pipeline Design Patterns](https://martinfowler.com/articles/data-pipeline-design-patterns.html)

### Herramientas Relacionadas
- [Apache Airflow](https://airflow.apache.org/)
- [Prefect](https://www.prefect.io/)
- [DBT](https://www.getdbt.com/)

---

*Esta documentación se actualiza regularmente. Para contribuir, consulta el README.md principal.* 