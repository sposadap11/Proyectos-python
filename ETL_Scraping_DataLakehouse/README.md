# 🚀 Competitive Price Intelligence Platform

## 📋 Descripción del Proyecto

**Competitive Price Intelligence Platform** es una solución completa de ingeniería de datos que automatiza la recolección, procesamiento y análisis de precios de productos de la competencia en e-commerce. Esta plataforma permite a las empresas tomar decisiones estratégicas de precios basadas en datos en tiempo real.

### 🎯 Caso de Uso Real

**Problema de Negocio**: Una empresa de e-commerce necesita mantener precios competitivos pero no tiene visibilidad de los precios de la competencia en tiempo real.

**Solución**: Sistema automatizado que:
- Extrae precios de múltiples competidores
- Procesa y almacena datos en un data lakehouse
- Genera insights para decisiones de precios
- Proporciona alertas de cambios de precios

**ROI Esperado**: 15-25% de mejora en márgenes de beneficio mediante optimización de precios.

## 🏗️ Arquitectura del Sistema

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   WEB SCRAPING  │    │   DATA LAKE     │    │      DBT        │    │   ANALYTICS     │
│                 │    │                 │    │                 │    │                 │
├─────────────────┤    ├─────────────────┤    ├─────────────────┤    ├─────────────────┤
│ • Selenium      │───▶│ • Parquet Files │───▶│ • Transformations│───▶│ • Power BI      │
│ • Scrapy        │    │ • Delta Lake    │    │ • Data Models   │    │ • Tableau       │
│ • APIs          │    │ • S3/MinIO      │    │ • Testing       │    │ • Alerts        │
└─────────────────┘    └─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │                       │
         ▼                       ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   ORCHESTRATION │    │   MONITORING    │    │   DATA QUALITY  │    │   API ENDPOINTS │
│                 │    │                 │    │                 │    │                 │
├─────────────────┤    ├─────────────────┤    ├─────────────────┤    ├─────────────────┤
│ • Apache Airflow│    │ • Grafana       │    │ • Great Expect. │    │ • FastAPI       │
│ • Prefect       │    │ • Prometheus    │    │ • Data Tests    │    │ • REST API      │
│ • Cron Jobs     │    │ • Logs          │    │ • Validation    │    │ • Webhooks      │
└─────────────────┘    └─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 🛠️ Stack Tecnológico

### Core Technologies
- **Python 3.9+**: Lenguaje principal
- **Apache Airflow**: Orquestación de workflows
- **DBT (Data Build Tool)**: Transformaciones de datos
- **Delta Lake**: Data lakehouse
- **DuckDB**: Base de datos analítica
- **Selenium/Scrapy**: Web scraping

### Infrastructure
- **Docker**: Containerización
- **MinIO**: Object storage (S3 compatible)
- **Grafana**: Monitoreo y visualización
- **FastAPI**: API REST

### Data Quality & Testing
- **Great Expectations**: Validación de datos
- **pytest**: Testing unitario
- **DBT Tests**: Testing de datos

## 📦 Instalación y Configuración

### Prerrequisitos
```bash
# Python 3.9+
python --version

# Docker
docker --version

# Git
git --version
```

### 1. Clonar el Repositorio
```bash
git clone https://github.com/tu-usuario/competitive-price-intelligence.git
cd competitive-price-intelligence
```

### 2. Configurar Entorno Virtual
```bash
# Crear entorno virtual
python -m venv venv

# Activar entorno (Windows)
venv\Scripts\activate

# Activar entorno (Linux/Mac)
source venv/bin/activate
```

### 3. Instalar Dependencias
```bash
# Instalar dependencias de Python
pip install -r requirements.txt

# Instalar DBT
pip install dbt-core dbt-duckdb

# Instalar Great Expectations
pip install great-expectations
```

### 4. Configurar Variables de Entorno
```bash
# Copiar archivo de ejemplo
cp .env.example .env

# Editar variables de entorno
nano .env
```

### 5. Inicializar DBT
```bash
# Navegar al directorio DBT
cd dbt_project

# Inicializar proyecto DBT
dbt init competitive_pricing

# Instalar dependencias
dbt deps
```

### 6. Levantar Infraestructura con Docker
```bash
# Construir y levantar servicios
docker-compose up -d

# Verificar servicios
docker-compose ps
```

## 🚀 Uso del Sistema

### Ejecución Manual

#### 1. Scraping de Datos
```bash
# Ejecutar scraping de Amazon
python src/scrapers/amazon_scraper.py

# Ejecutar scraping de MercadoLibre
python src/scrapers/mercadolibre_scraper.py

# Ejecutar todos los scrapers
python main.py --stage scrape
```

#### 2. Procesamiento de Datos
```bash
# Transformar datos con DBT
cd dbt_project
dbt run

# Ejecutar tests
dbt test

# Generar documentación
dbt docs generate
dbt docs serve
```

#### 3. Análisis y Reportes
```bash
# Generar reportes de precios
python src/utils/report_generator.py

# Ejecutar análisis de competitividad
python src/analytics/price_analysis.py
```

### Ejecución Automatizada

#### Con Apache Airflow
```bash
# Acceder a la interfaz de Airflow
# http://localhost:8080

# Activar DAGs
# - price_scraping_dag
# - data_processing_dag
# - reporting_dag
```

#### Con Prefect
```bash
# Iniciar servidor de Prefect
prefect server start

# Ejecutar deployment
prefect deployment run price-intelligence/main-flow
```

## 📊 Estructura del Proyecto

```
competitive-price-intelligence/
├── 📄 README.md                    # Documentación principal
├── 📄 requirements.txt             # Dependencias Python
├── 📄 docker-compose.yml           # Orquestación de servicios
├── 📄 .env.example                 # Variables de entorno
├── 📄 main.py                      # Script principal
├── 📄 LICENSE                      # Licencia MIT
├── 📄 .gitignore                   # Archivos a ignorar
├── 📄 DOCUMENTACION.md             # Documentación técnica
├── 📁 src/                         # Código fuente
│   ├── 📁 scrapers/                # Web scrapers
│   │   ├── 📄 amazon_scraper.py
│   │   ├── 📄 mercadolibre_scraper.py
│   │   └── 📄 base_scraper.py
│   ├── 📁 transformers/            # Transformaciones
│   ├── 📁 loaders/                 # Carga de datos
│   ├── 📁 utils/                   # Utilidades
│   ├── 📁 analytics/               # Análisis
│   └── 📁 orchestration/           # Orquestación
├── 📁 dbt_project/                 # Proyecto DBT
│   ├── 📁 models/                  # Modelos de datos
│   ├── 📁 tests/                   # Tests de datos
│   ├── 📁 macros/                  # Macros DBT
│   └── 📄 dbt_project.yml          # Configuración DBT
├── 📁 data/                        # Datos
│   ├── 📁 raw/                     # Datos sin procesar
│   ├── 📁 processed/               # Datos procesados
│   └── 📁 reports/                 # Reportes
├── 📁 config/                      # Configuraciones
├── 📁 docker/                      # Configuración Docker
├── 📁 tests/                       # Tests unitarios
└── 📁 logs/                        # Logs del sistema
```

## 🔍 Funcionalidades Principales

### 1. Web Scraping Inteligente
- **Multi-plataforma**: Amazon, MercadoLibre, eBay, etc.
- **Anti-detección**: Rotación de User-Agents, proxies
- **Rate Limiting**: Respeto a robots.txt
- **Retry Logic**: Manejo de errores robusto

### 2. Data Lakehouse
- **Formato Delta**: ACID transactions
- **Particionado**: Por fecha y categoría
- **Compresión**: Optimización de almacenamiento
- **Versionado**: Historial de cambios

### 3. Transformaciones con DBT
- **Modelos Incrementales**: Procesamiento eficiente
- **Tests de Calidad**: Validación automática
- **Documentación**: Auto-generada
- **Lineage**: Trazabilidad de datos

### 4. Análisis de Precios
- **Price Positioning**: Posicionamiento vs competencia
- **Price Elasticity**: Elasticidad de precios
- **Market Share**: Cuota de mercado
- **Alertas**: Cambios significativos

### 5. Monitoreo y Alertas
- **Dashboards**: Grafana + Prometheus
- **Alertas**: Email, Slack, Webhook
- **Logs**: Centralizados y estructurados
- **Métricas**: KPIs de negocio

## 📈 Modelos de Datos

### Raw Layer (Bronze)
```sql
-- Productos extraídos
CREATE TABLE raw_products (
    id STRING,
    name STRING,
    price DECIMAL(10,2),
    competitor STRING,
    category STRING,
    url STRING,
    scraped_at TIMESTAMP,
    raw_data JSON
);

-- Historial de precios
CREATE TABLE raw_price_history (
    product_id STRING,
    price DECIMAL(10,2),
    competitor STRING,
    scraped_at TIMESTAMP,
    availability BOOLEAN
);
```

### Processed Layer (Silver)
```sql
-- Productos normalizados
CREATE TABLE dim_products (
    product_id STRING,
    name STRING,
    category STRING,
    brand STRING,
    competitor STRING,
    url STRING,
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);

-- Fact table de precios
CREATE TABLE fact_prices (
    product_id STRING,
    competitor STRING,
    price DECIMAL(10,2),
    date_id INTEGER,
    availability BOOLEAN,
    price_change DECIMAL(10,2),
    price_change_pct DECIMAL(5,2)
);
```

### Analytics Layer (Gold)
```sql
-- KPIs de precios
CREATE TABLE kpi_price_competitiveness (
    date_id INTEGER,
    category STRING,
    avg_price DECIMAL(10,2),
    min_price DECIMAL(10,2),
    max_price DECIMAL(10,2),
    price_variance DECIMAL(10,2),
    products_count INTEGER
);

-- Alertas de precios
CREATE TABLE price_alerts (
    alert_id STRING,
    product_id STRING,
    alert_type STRING,
    old_price DECIMAL(10,2),
    new_price DECIMAL(10,2),
    change_pct DECIMAL(5,2),
    created_at TIMESTAMP
);
```

## 🧪 Testing y Calidad de Datos

### Tests Unitarios
```bash
# Ejecutar tests
pytest tests/ -v

# Con cobertura
pytest tests/ --cov=src --cov-report=html
```

### Tests de Datos (DBT)
```bash
# Ejecutar tests DBT
dbt test

# Tests específicos
dbt test --models dim_products
```

### Great Expectations
```bash
# Validar datos
python src/utils/data_validation.py

# Generar suite de validación
great_expectations suite new
```

## 📊 Dashboards y Reportes

### KPIs Principales
- **Price Competitiveness Index**: Índice de competitividad
- **Market Share by Price Range**: Cuota por rango de precios
- **Price Change Velocity**: Velocidad de cambios
- **Competitor Price Distribution**: Distribución de precios

### Alertas Automáticas
- **Price Drops > 10%**: Caídas significativas
- **New Competitor Entry**: Nuevos competidores
- **Stock Outages**: Agotamiento de stock
- **Price Wars**: Guerras de precios

## 🔧 Configuración Avanzada

### Variables de Entorno
```bash
# Scraping
SCRAPER_DELAY=2
SCRAPER_TIMEOUT=30
SCRAPER_RETRIES=3

# Database
DATABASE_URL=duckdb:///data/warehouse.db
MINIO_ENDPOINT=localhost:9000
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin

# Airflow
AIRFLOW_HOME=./airflow
AIRFLOW__CORE__EXECUTOR=LocalExecutor

# Monitoring
GRAFANA_URL=http://localhost:3000
PROMETHEUS_URL=http://localhost:9090
```

### Configuración DBT
```yaml
# dbt_project.yml
name: 'competitive_pricing'
version: '1.0.0'
config-version: 2

profile: 'competitive_pricing'

models:
  competitive_pricing:
    staging:
      +materialized: view
    marts:
      +materialized: table
    intermediate:
      +materialized: incremental
```

## 🚀 Deployment

### Desarrollo Local
```bash
# Levantar servicios
docker-compose up -d

# Ejecutar pipeline completo
python main.py --full-pipeline

# Monitorear logs
docker-compose logs -f
```

### Producción
```bash
# Usar docker-compose.prod.yml
docker-compose -f docker-compose.prod.yml up -d

# Configurar backups
./scripts/backup.sh

# Monitorear métricas
./scripts/monitoring.sh
```

## 📈 Métricas de Negocio

### ROI Esperado
- **15-25%** mejora en márgenes de beneficio
- **30-40%** reducción en tiempo de análisis
- **50-60%** mejora en precisión de precios

### KPIs Técnicos
- **99.9%** uptime del sistema
- **< 5 minutos** latencia de datos
- **< 1%** tasa de error en scraping
- **100%** cobertura de tests

## 🤝 Contribución

1. Fork el proyecto
2. Crear rama feature (`git checkout -b feature/AmazingFeature`)
3. Commit cambios (`git commit -m 'Add AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abrir Pull Request

## 📄 Licencia

Este proyecto está bajo la Licencia MIT - ver [LICENSE](LICENSE) para detalles.

## 👨‍💻 Autor

**Tu Nombre** - Senior Data Engineer
- GitHub: [@tu-usuario](https://github.com/tu-usuario)
- LinkedIn: [Tu Perfil](https://linkedin.com/in/tu-perfil)
- Portfolio: [tu-portfolio.com](https://tu-portfolio.com)

## 🙏 Agradecimientos

- Comunidad de DBT por las mejores prácticas
- Apache Airflow por la orquestación robusta
- Delta Lake por el data lakehouse
- Herramientas open source utilizadas

---

⭐ **¡No olvides dar una estrella al repositorio si te fue útil!**

## 📞 Soporte

Para soporte técnico o consultas comerciales:
- 📧 Email: tu-email@ejemplo.com
- 💬 Slack: [Canal de soporte](https://slack.com/app_redirect?channel=soporte)
- 📖 Docs: [Documentación completa](DOCUMENTACION.md) 