"""
Módulo para generar reportes y visualizaciones de datos.
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import sqlite3
import sqlalchemy as sa
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime
import json
from jinja2 import Template
import warnings

# Configurar matplotlib para no mostrar warnings
warnings.filterwarnings('ignore')
plt.style.use('seaborn-v0_8')

from .logger import LoggerMixin
from .config_loader import ConfigLoader


class ReportGenerator(LoggerMixin):
    """Clase para generar reportes y visualizaciones de datos."""
    
    def __init__(self, config: ConfigLoader):
        """
        Inicializar el generador de reportes.
        
        Args:
            config: Instancia de ConfigLoader con la configuración
        """
        self.config = config
        self.reports_config = self.config.get('reports', {})
        self.reports_path = Path(self.config.get('paths.data_reports'))
        
        # Crear directorio de reportes si no existe
        self.reports_path.mkdir(parents=True, exist_ok=True)
        
        # Configurar estilo de gráficos
        self._setup_plot_style()
        
        self.logger.info("Generador de reportes inicializado")
    
    def generate_all_reports(self) -> bool:
        """
        Generar todos los reportes disponibles.
        
        Returns:
            True si la generación fue exitosa, False en caso contrario
        """
        self.logger.info("Iniciando generación de todos los reportes")
        
        try:
            # Conectar a la base de datos
            engine = self._create_database_connection()
            
            # Generar reportes de ventas
            self._generate_sales_reports(engine)
            
            # Generar reportes de productos
            self._generate_product_reports(engine)
            
            # Generar reportes de clientes
            self._generate_customer_reports(engine)
            
            # Generar reporte general
            self._generate_general_report(engine)
            
            # Generar reporte HTML
            self._generate_html_report()
            
            self.logger.info("Generación de reportes completada exitosamente")
            return True
            
        except Exception as e:
            self.logger.error(f"Error en generación de reportes: {str(e)}")
            return False
    
    def _setup_plot_style(self) -> None:
        """Configurar estilo de gráficos."""
        try:
            # Configurar estilo de matplotlib
            plt.rcParams['figure.figsize'] = (12, 8)
            plt.rcParams['font.size'] = 10
            plt.rcParams['axes.titlesize'] = 14
            plt.rcParams['axes.labelsize'] = 12
            
            # Configurar estilo de seaborn
            sns.set_palette("husl")
            
        except Exception as e:
            self.logger.warning(f"Error al configurar estilo de gráficos: {str(e)}")
    
    def _create_database_connection(self) -> sa.engine.Engine:
        """
        Crear conexión a la base de datos.
        
        Returns:
            Engine de SQLAlchemy
        """
        try:
            db_path = Path(self.config.get('database.path'))
            db_url = f"sqlite:///{db_path}"
            engine = sa.create_engine(db_url, echo=False)
            return engine
            
        except Exception as e:
            self.logger.error(f"Error al conectar a base de datos: {str(e)}")
            raise
    
    def _generate_sales_reports(self, engine: sa.engine.Engine) -> None:
        """
        Generar reportes relacionados con ventas.
        
        Args:
            engine: Engine de SQLAlchemy
        """
        try:
            self.logger.info("Generando reportes de ventas")
            
            # Reporte de ventas por día
            query = """
                SELECT fecha, COUNT(*) as num_ventas, SUM(total) as total_ventas
                FROM ventas
                GROUP BY fecha
                ORDER BY fecha
            """
            df_ventas_dia = pd.read_sql_query(query, engine)
            
            if not df_ventas_dia.empty:
                # Gráfico de ventas por día
                plt.figure(figsize=(15, 6))
                plt.plot(df_ventas_dia['fecha'], df_ventas_dia['total_ventas'], marker='o')
                plt.title('Ventas Totales por Día')
                plt.xlabel('Fecha')
                plt.ylabel('Total de Ventas (€)')
                plt.xticks(rotation=45)
                plt.tight_layout()
                plt.savefig(self.reports_path / 'ventas_por_dia.png', dpi=300, bbox_inches='tight')
                plt.close()
                
                # Guardar datos en CSV
                df_ventas_dia.to_csv(self.reports_path / 'ventas_por_dia.csv', index=False)
            
            # Reporte de ventas por categoría
            query = """
                SELECT vpc.categoria, vpc.cantidad_total, vpc.total_ventas, vpc.num_ventas
                FROM ventas_por_categoria vpc
                ORDER BY vpc.total_ventas DESC
            """
            df_ventas_categoria = pd.read_sql_query(query, engine)
            
            if not df_ventas_categoria.empty:
                # Gráfico de ventas por categoría
                plt.figure(figsize=(12, 8))
                bars = plt.bar(df_ventas_categoria['categoria'], df_ventas_categoria['total_ventas'])
                plt.title('Ventas Totales por Categoría')
                plt.xlabel('Categoría')
                plt.ylabel('Total de Ventas (€)')
                plt.xticks(rotation=45)
                
                # Agregar valores en las barras
                for bar in bars:
                    height = bar.get_height()
                    plt.text(bar.get_x() + bar.get_width()/2., height + 0.01,
                            f'{height:.0f}€', ha='center', va='bottom')
                
                plt.tight_layout()
                plt.savefig(self.reports_path / 'ventas_por_categoria.png', dpi=300, bbox_inches='tight')
                plt.close()
                
                # Guardar datos en CSV
                df_ventas_categoria.to_csv(self.reports_path / 'ventas_por_categoria.csv', index=False)
            
            self.logger.info("Reportes de ventas generados")
            
        except Exception as e:
            self.logger.error(f"Error al generar reportes de ventas: {str(e)}")
    
    def _generate_product_reports(self, engine: sa.engine.Engine) -> None:
        """
        Generar reportes relacionados con productos.
        
        Args:
            engine: Engine de SQLAlchemy
        """
        try:
            self.logger.info("Generando reportes de productos")
            
            # Top 10 productos más vendidos
            query = """
                SELECT vpp.nombre_producto, vpp.cantidad_total, vpp.total_ventas, vpp.num_ventas
                FROM ventas_por_producto vpp
                ORDER BY vpp.total_ventas DESC
                LIMIT 10
            """
            df_top_productos = pd.read_sql_query(query, engine)
            
            if not df_top_productos.empty:
                # Gráfico de top productos
                plt.figure(figsize=(14, 8))
                bars = plt.barh(df_top_productos['nombre_producto'], df_top_productos['total_ventas'])
                plt.title('Top 10 Productos Más Vendidos')
                plt.xlabel('Total de Ventas (€)')
                plt.ylabel('Producto')
                
                # Agregar valores en las barras
                for i, bar in enumerate(bars):
                    width = bar.get_width()
                    plt.text(width + 0.01, bar.get_y() + bar.get_height()/2,
                            f'{width:.0f}€', ha='left', va='center')
                
                plt.tight_layout()
                plt.savefig(self.reports_path / 'top_productos.png', dpi=300, bbox_inches='tight')
                plt.close()
                
                # Guardar datos en CSV
                df_top_productos.to_csv(self.reports_path / 'top_productos.csv', index=False)
            
            # Análisis de inventario
            query = """
                SELECT p.nombre, p.categoria, i.stock_actual, i.stock_minimo, i.stock_bajo
                FROM inventario i
                JOIN productos p ON i.producto_id = p.id
                ORDER BY i.stock_actual ASC
            """
            df_inventario = pd.read_sql_query(query, engine)
            
            if not df_inventario.empty:
                # Gráfico de stock por producto
                plt.figure(figsize=(16, 8))
                colors = ['red' if bajo else 'green' for bajo in df_inventario['stock_bajo']]
                bars = plt.bar(df_inventario['nombre'], df_inventario['stock_actual'], color=colors)
                plt.title('Stock Actual por Producto')
                plt.xlabel('Producto')
                plt.ylabel('Stock Actual')
                plt.xticks(rotation=45, ha='right')
                
                # Agregar línea de stock mínimo
                plt.axhline(y=df_inventario['stock_minimo'].mean(), color='orange', linestyle='--', 
                           label=f'Stock Mínimo Promedio: {df_inventario["stock_minimo"].mean():.0f}')
                plt.legend()
                
                plt.tight_layout()
                plt.savefig(self.reports_path / 'stock_productos.png', dpi=300, bbox_inches='tight')
                plt.close()
                
                # Guardar datos en CSV
                df_inventario.to_csv(self.reports_path / 'inventario.csv', index=False)
            
            self.logger.info("Reportes de productos generados")
            
        except Exception as e:
            self.logger.error(f"Error al generar reportes de productos: {str(e)}")
    
    def _generate_customer_reports(self, engine: sa.engine.Engine) -> None:
        """
        Generar reportes relacionados con clientes.
        
        Args:
            engine: Engine de SQLAlchemy
        """
        try:
            self.logger.info("Generando reportes de clientes")
            
            # Top 10 clientes con más compras
            query = """
                SELECT vpc.nombre_cliente, vpc.ciudad, vpc.cantidad_total, vpc.total_compras, vpc.num_compras
                FROM ventas_por_cliente vpc
                ORDER BY vpc.total_compras DESC
                LIMIT 10
            """
            df_top_clientes = pd.read_sql_query(query, engine)
            
            if not df_top_clientes.empty:
                # Gráfico de top clientes
                plt.figure(figsize=(14, 8))
                bars = plt.barh(df_top_clientes['nombre_cliente'], df_top_clientes['total_compras'])
                plt.title('Top 10 Clientes con Más Compras')
                plt.xlabel('Total de Compras (€)')
                plt.ylabel('Cliente')
                
                # Agregar valores en las barras
                for i, bar in enumerate(bars):
                    width = bar.get_width()
                    plt.text(width + 0.01, bar.get_y() + bar.get_height()/2,
                            f'{width:.0f}€', ha='left', va='center')
                
                plt.tight_layout()
                plt.savefig(self.reports_path / 'top_clientes.png', dpi=300, bbox_inches='tight')
                plt.close()
                
                # Guardar datos en CSV
                df_top_clientes.to_csv(self.reports_path / 'top_clientes.csv', index=False)
            
            # Ventas por ciudad
            query = """
                SELECT c.ciudad, COUNT(v.id) as num_ventas, SUM(v.total) as total_ventas
                FROM ventas v
                JOIN clientes c ON v.cliente_id = c.id
                GROUP BY c.ciudad
                ORDER BY total_ventas DESC
            """
            df_ventas_ciudad = pd.read_sql_query(query, engine)
            
            if not df_ventas_ciudad.empty:
                # Gráfico de ventas por ciudad
                plt.figure(figsize=(12, 8))
                bars = plt.bar(df_ventas_ciudad['ciudad'], df_ventas_ciudad['total_ventas'])
                plt.title('Ventas Totales por Ciudad')
                plt.xlabel('Ciudad')
                plt.ylabel('Total de Ventas (€)')
                plt.xticks(rotation=45)
                
                # Agregar valores en las barras
                for bar in bars:
                    height = bar.get_height()
                    plt.text(bar.get_x() + bar.get_width()/2., height + 0.01,
                            f'{height:.0f}€', ha='center', va='bottom')
                
                plt.tight_layout()
                plt.savefig(self.reports_path / 'ventas_por_ciudad.png', dpi=300, bbox_inches='tight')
                plt.close()
                
                # Guardar datos en CSV
                df_ventas_ciudad.to_csv(self.reports_path / 'ventas_por_ciudad.csv', index=False)
            
            self.logger.info("Reportes de clientes generados")
            
        except Exception as e:
            self.logger.error(f"Error al generar reportes de clientes: {str(e)}")
    
    def _generate_general_report(self, engine: sa.engine.Engine) -> None:
        """
        Generar reporte general con métricas clave.
        
        Args:
            engine: Engine de SQLAlchemy
        """
        try:
            self.logger.info("Generando reporte general")
            
            # Obtener métricas generales
            metrics = {}
            
            # Total de ventas
            query = "SELECT COUNT(*) as total_ventas, SUM(total) as total_ingresos FROM ventas"
            result = pd.read_sql_query(query, engine)
            metrics['total_ventas'] = result['total_ventas'].iloc[0]
            metrics['total_ingresos'] = result['total_ingresos'].iloc[0]
            
            # Total de productos
            query = "SELECT COUNT(*) as total_productos FROM productos"
            result = pd.read_sql_query(query, engine)
            metrics['total_productos'] = result['total_productos'].iloc[0]
            
            # Total de clientes
            query = "SELECT COUNT(*) as total_clientes FROM clientes"
            result = pd.read_sql_query(query, engine)
            metrics['total_clientes'] = result['total_clientes'].iloc[0]
            
            # Productos con stock bajo
            query = "SELECT COUNT(*) as productos_stock_bajo FROM inventario WHERE stock_bajo = 1"
            result = pd.read_sql_query(query, engine)
            metrics['productos_stock_bajo'] = result['productos_stock_bajo'].iloc[0]
            
            # Ticket promedio
            query = "SELECT AVG(total) as ticket_promedio FROM ventas"
            result = pd.read_sql_query(query, engine)
            metrics['ticket_promedio'] = result['ticket_promedio'].iloc[0]
            
            # Guardar métricas en JSON
            metrics['fecha_generacion'] = datetime.now().isoformat()
            metrics_file = self.reports_path / 'metricas_generales.json'
            
            with open(metrics_file, 'w', encoding='utf-8') as f:
                json.dump(metrics, f, indent=2, ensure_ascii=False)
            
            # Crear gráfico de métricas
            plt.figure(figsize=(15, 10))
            
            # Subplot 1: Métricas principales
            plt.subplot(2, 2, 1)
            metric_names = ['Ventas', 'Ingresos (€)', 'Productos', 'Clientes']
            metric_values = [metrics['total_ventas'], metrics['total_ingresos'], 
                           metrics['total_productos'], metrics['total_clientes']]
            bars = plt.bar(metric_names, metric_values, color=['blue', 'green', 'orange', 'red'])
            plt.title('Métricas Principales')
            plt.ylabel('Cantidad')
            
            # Agregar valores en las barras
            for bar in bars:
                height = bar.get_height()
                plt.text(bar.get_x() + bar.get_width()/2., height + 0.01,
                        f'{height:.0f}', ha='center', va='bottom')
            
            # Subplot 2: Ticket promedio
            plt.subplot(2, 2, 2)
            plt.pie([metrics['ticket_promedio'], 100], labels=['Ticket Promedio', ''], 
                   autopct='%1.1f€', startangle=90)
            plt.title('Ticket Promedio por Venta')
            
            # Subplot 3: Productos con stock bajo
            plt.subplot(2, 2, 3)
            stock_data = [metrics['productos_stock_bajo'], 
                         metrics['total_productos'] - metrics['productos_stock_bajo']]
            plt.pie(stock_data, labels=['Stock Bajo', 'Stock OK'], 
                   autopct='%1.1f%%', startangle=90, colors=['red', 'green'])
            plt.title('Estado del Inventario')
            
            # Subplot 4: Resumen temporal
            plt.subplot(2, 2, 4)
            plt.text(0.1, 0.8, f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M')}", 
                    fontsize=12, transform=plt.gca().transAxes)
            plt.text(0.1, 0.6, f"Total Ventas: {metrics['total_ventas']}", 
                    fontsize=12, transform=plt.gca().transAxes)
            plt.text(0.1, 0.4, f"Total Ingresos: {metrics['total_ingresos']:.2f}€", 
                    fontsize=12, transform=plt.gca().transAxes)
            plt.text(0.1, 0.2, f"Ticket Promedio: {metrics['ticket_promedio']:.2f}€", 
                    fontsize=12, transform=plt.gca().transAxes)
            plt.axis('off')
            plt.title('Resumen General')
            
            plt.tight_layout()
            plt.savefig(self.reports_path / 'reporte_general.png', dpi=300, bbox_inches='tight')
            plt.close()
            
            self.logger.info("Reporte general generado")
            
        except Exception as e:
            self.logger.error(f"Error al generar reporte general: {str(e)}")
    
    def _generate_html_report(self) -> None:
        """Generar reporte HTML con todos los gráficos y métricas."""
        try:
            self.logger.info("Generando reporte HTML")
            
            # Plantilla HTML
            html_template = """
            <!DOCTYPE html>
            <html lang="es">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>{{ title }}</title>
                <style>
                    body { font-family: Arial, sans-serif; margin: 20px; background-color: #f5f5f5; }
                    .container { max-width: 1200px; margin: 0 auto; background-color: white; padding: 20px; border-radius: 10px; box-shadow: 0 0 10px rgba(0,0,0,0.1); }
                    h1 { color: #2c3e50; text-align: center; border-bottom: 3px solid #3498db; padding-bottom: 10px; }
                    h2 { color: #34495e; margin-top: 30px; }
                    .metric-card { background-color: #ecf0f1; padding: 15px; margin: 10px 0; border-radius: 5px; border-left: 4px solid #3498db; }
                    .metric-value { font-size: 24px; font-weight: bold; color: #2c3e50; }
                    .metric-label { color: #7f8c8d; font-size: 14px; }
                    .chart-section { margin: 30px 0; }
                    .chart-container { text-align: center; margin: 20px 0; }
                    img { max-width: 100%; height: auto; border-radius: 5px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }
                    .footer { text-align: center; margin-top: 40px; padding-top: 20px; border-top: 1px solid #bdc3c7; color: #7f8c8d; }
                    table { width: 100%; border-collapse: collapse; margin: 20px 0; }
                    th, td { padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }
                    th { background-color: #3498db; color: white; }
                    tr:nth-child(even) { background-color: #f2f2f2; }
                </style>
            </head>
            <body>
                <div class="container">
                    <h1>{{ title }}</h1>
                    <p><strong>Fecha de generación:</strong> {{ fecha_generacion }}</p>
                    
                    <h2>📊 Métricas Generales</h2>
                    <div class="metric-card">
                        <div class="metric-value">{{ metricas.total_ventas }}</div>
                        <div class="metric-label">Total de Ventas</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value">{{ "%.2f"|format(metricas.total_ingresos) }}€</div>
                        <div class="metric-label">Total de Ingresos</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value">{{ "%.2f"|format(metricas.ticket_promedio) }}€</div>
                        <div class="metric-label">Ticket Promedio</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value">{{ metricas.productos_stock_bajo }}</div>
                        <div class="metric-label">Productos con Stock Bajo</div>
                    </div>
                    
                    <h2>📈 Gráficos de Análisis</h2>
                    
                    <div class="chart-section">
                        <h3>Ventas por Día</h3>
                        <div class="chart-container">
                            <img src="ventas_por_dia.png" alt="Ventas por Día">
                        </div>
                    </div>
                    
                    <div class="chart-section">
                        <h3>Ventas por Categoría</h3>
                        <div class="chart-container">
                            <img src="ventas_por_categoria.png" alt="Ventas por Categoría">
                        </div>
                    </div>
                    
                    <div class="chart-section">
                        <h3>Top 10 Productos Más Vendidos</h3>
                        <div class="chart-container">
                            <img src="top_productos.png" alt="Top Productos">
                        </div>
                    </div>
                    
                    <div class="chart-section">
                        <h3>Estado del Inventario</h3>
                        <div class="chart-container">
                            <img src="stock_productos.png" alt="Stock Productos">
                        </div>
                    </div>
                    
                    <div class="chart-section">
                        <h3>Top 10 Clientes</h3>
                        <div class="chart-container">
                            <img src="top_clientes.png" alt="Top Clientes">
                        </div>
                    </div>
                    
                    <div class="chart-section">
                        <h3>Ventas por Ciudad</h3>
                        <div class="chart-container">
                            <img src="ventas_por_ciudad.png" alt="Ventas por Ciudad">
                        </div>
                    </div>
                    
                    <div class="chart-section">
                        <h3>Reporte General</h3>
                        <div class="chart-container">
                            <img src="reporte_general.png" alt="Reporte General">
                        </div>
                    </div>
                    
                    <div class="footer">
                        <p>Reporte generado automáticamente por el Pipeline ETL</p>
                        <p>Proyecto: Análisis de E-commerce</p>
                    </div>
                </div>
            </body>
            </html>
            """
            
            # Cargar métricas
            metrics_file = self.reports_path / 'metricas_generales.json'
            if metrics_file.exists():
                with open(metrics_file, 'r', encoding='utf-8') as f:
                    metrics = json.load(f)
            else:
                metrics = {
                    'total_ventas': 0,
                    'total_ingresos': 0,
                    'ticket_promedio': 0,
                    'productos_stock_bajo': 0
                }
            
            # Renderizar plantilla
            template = Template(html_template)
            html_content = template.render(
                title=self.reports_config.get('report_title', 'Reporte de Análisis E-commerce'),
                fecha_generacion=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                metricas=metrics
            )
            
            # Guardar archivo HTML
            html_file = self.reports_path / 'reporte_completo.html'
            with open(html_file, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            self.logger.info(f"Reporte HTML generado: {html_file}")
            
        except Exception as e:
            self.logger.error(f"Error al generar reporte HTML: {str(e)}")
    
    def generate_specific_report(self, report_type: str) -> bool:
        """
        Generar un reporte específico.
        
        Args:
            report_type: Tipo de reporte ('ventas', 'productos', 'clientes', 'general')
            
        Returns:
            True si la generación fue exitosa, False en caso contrario
        """
        try:
            self.logger.info(f"Generando reporte específico: {report_type}")
            
            engine = self._create_database_connection()
            
            if report_type == 'ventas':
                self._generate_sales_reports(engine)
            elif report_type == 'productos':
                self._generate_product_reports(engine)
            elif report_type == 'clientes':
                self._generate_customer_reports(engine)
            elif report_type == 'general':
                self._generate_general_report(engine)
            else:
                self.logger.error(f"Tipo de reporte no válido: {report_type}")
                return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error al generar reporte específico {report_type}: {str(e)}")
            return False 