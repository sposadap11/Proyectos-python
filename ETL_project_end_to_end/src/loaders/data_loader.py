"""
Módulo principal para la carga de datos en base de datos.
"""

import pandas as pd
import sqlite3
import sqlalchemy as sa
from pathlib import Path
from typing import Dict, Any, Optional, List
import json
from datetime import datetime

from ..utils.logger import LoggerMixin
from ..utils.config_loader import ConfigLoader


class DataLoader(LoggerMixin):
    """Clase principal para cargar datos en base de datos."""
    
    def __init__(self, config: ConfigLoader):
        """
        Inicializar el cargador de datos.
        
        Args:
            config: Instancia de ConfigLoader con la configuración
        """
        self.config = config
        self.db_config = self.config.get_database_config()
        self.db_path = Path(self.db_config.get('path', 'data/processed/ecommerce_analytics.db'))
        
        # Crear directorio si no existe
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        self.logger.info(f"Cargador de datos inicializado. Base de datos: {self.db_path}")
    
    def load_all(self, transformed_data: Dict[str, pd.DataFrame]) -> bool:
        """
        Cargar todos los datos transformados en la base de datos.
        
        Args:
            transformed_data: Diccionario con DataFrames transformados
            
        Returns:
            True si la carga fue exitosa, False en caso contrario
        """
        self.logger.info("Iniciando carga de todos los datos en base de datos")
        
        try:
            # Crear conexión a la base de datos
            engine = self._create_database_connection()
            
            # Crear tablas si no existen
            self._create_tables(engine)
            
            # Cargar datos en cada tabla
            for table_name, df in transformed_data.items():
                self.logger.info(f"Cargando datos en tabla: {table_name}")
                
                success = self._load_table(engine, table_name, df)
                if not success:
                    self.logger.error(f"Error al cargar tabla {table_name}")
                    return False
            
            # Crear índices para optimizar consultas
            self._create_indexes(engine)
            
            # Generar estadísticas de carga
            self._generate_load_statistics(transformed_data)
            
            self.logger.info("Carga de datos completada exitosamente")
            return True
            
        except Exception as e:
            self.logger.error(f"Error en carga de datos: {str(e)}")
            return False
    
    def _create_database_connection(self) -> sa.engine.Engine:
        """
        Crear conexión a la base de datos SQLite.
        
        Returns:
            Engine de SQLAlchemy
        """
        try:
            # Crear URL de conexión
            db_url = f"sqlite:///{self.db_path}"
            
            # Crear engine
            engine = sa.create_engine(db_url, echo=False)
            
            self.logger.info(f"Conexión a base de datos creada: {db_url}")
            return engine
            
        except Exception as e:
            self.logger.error(f"Error al crear conexión a base de datos: {str(e)}")
            raise
    
    def _create_tables(self, engine: sa.engine.Engine) -> None:
        """
        Crear tablas en la base de datos si no existen.
        
        Args:
            engine: Engine de SQLAlchemy
        """
        try:
            # Definir esquemas de tablas
            table_schemas = {
                'ventas': '''
                    CREATE TABLE IF NOT EXISTS ventas (
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
                    )
                ''',
                'productos': '''
                    CREATE TABLE IF NOT EXISTS productos (
                        id INTEGER PRIMARY KEY,
                        nombre TEXT NOT NULL,
                        categoria TEXT NOT NULL,
                        precio REAL NOT NULL,
                        stock INTEGER,
                        descripcion TEXT
                    )
                ''',
                'clientes': '''
                    CREATE TABLE IF NOT EXISTS clientes (
                        id INTEGER PRIMARY KEY,
                        nombre TEXT NOT NULL,
                        email TEXT NOT NULL,
                        ciudad TEXT NOT NULL,
                        telefono TEXT,
                        fecha_registro DATETIME
                    )
                ''',
                'categorias': '''
                    CREATE TABLE IF NOT EXISTS categorias (
                        id INTEGER PRIMARY KEY,
                        nombre TEXT NOT NULL,
                        descripcion TEXT,
                        activo BOOLEAN
                    )
                ''',
                'inventario': '''
                    CREATE TABLE IF NOT EXISTS inventario (
                        producto_id INTEGER PRIMARY KEY,
                        stock_actual INTEGER NOT NULL,
                        stock_minimo INTEGER NOT NULL,
                        ultima_actualizacion DATETIME,
                        stock_bajo BOOLEAN
                    )
                ''',
                'ventas_por_producto': '''
                    CREATE TABLE IF NOT EXISTS ventas_por_producto (
                        producto_id INTEGER PRIMARY KEY,
                        cantidad_total INTEGER NOT NULL,
                        total_ventas REAL NOT NULL,
                        num_ventas INTEGER NOT NULL,
                        nombre_producto TEXT,
                        categoria TEXT
                    )
                ''',
                'ventas_por_cliente': '''
                    CREATE TABLE IF NOT EXISTS ventas_por_cliente (
                        cliente_id INTEGER PRIMARY KEY,
                        cantidad_total INTEGER NOT NULL,
                        total_compras REAL NOT NULL,
                        num_compras INTEGER NOT NULL,
                        nombre_cliente TEXT,
                        ciudad TEXT
                    )
                ''',
                'ventas_por_categoria': '''
                    CREATE TABLE IF NOT EXISTS ventas_por_categoria (
                        categoria TEXT PRIMARY KEY,
                        cantidad_total INTEGER NOT NULL,
                        total_ventas REAL NOT NULL,
                        num_ventas INTEGER NOT NULL
                    )
                '''
            }
            
            # Crear tablas
            with engine.connect() as conn:
                for table_name, schema in table_schemas.items():
                    conn.execute(sa.text(schema))
                    self.logger.debug(f"Tabla {table_name} creada/verificada")
                
                conn.commit()
            
            self.logger.info(f"Esquema de base de datos creado con {len(table_schemas)} tablas")
            
        except Exception as e:
            self.logger.error(f"Error al crear tablas: {str(e)}")
            raise
    
    def _load_table(self, engine: sa.engine.Engine, table_name: str, df: pd.DataFrame) -> bool:
        """
        Cargar datos de un DataFrame en una tabla específica.
        
        Args:
            engine: Engine de SQLAlchemy
            table_name: Nombre de la tabla
            df: DataFrame con los datos a cargar
            
        Returns:
            True si la carga fue exitosa, False en caso contrario
        """
        try:
            if df.empty:
                self.logger.warning(f"DataFrame vacío para tabla {table_name}")
                return True
            
            # Preparar datos para inserción
            df_to_insert = self._prepare_data_for_insertion(df, table_name)
            
            # Cargar datos usando pandas to_sql
            df_to_insert.to_sql(
                name=table_name,
                con=engine,
                if_exists='replace',  # Reemplazar datos existentes
                index=False,
                method='multi',
                chunksize=1000
            )
            
            self.logger.info(f"Cargados {len(df_to_insert)} registros en tabla {table_name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error al cargar tabla {table_name}: {str(e)}")
            return False
    
    def _prepare_data_for_insertion(self, df: pd.DataFrame, table_name: str) -> pd.DataFrame:
        """
        Preparar DataFrame para inserción en base de datos.
        
        Args:
            df: DataFrame original
            table_name: Nombre de la tabla
            
        Returns:
            DataFrame preparado para inserción
        """
        try:
            df_prepared = df.copy()
            
            # Mapear nombres de columnas según la tabla
            column_mapping = {
                'ventas_por_producto': {
                    'id': 'producto_id',
                    'cantidad': 'cantidad_total',
                    'total': 'total_ventas',
                    'num_ventas': 'num_ventas',
                    'nombre': 'nombre_producto'
                },
                'ventas_por_cliente': {
                    'id': 'cliente_id',
                    'cantidad': 'cantidad_total',
                    'total': 'total_compras',
                    'num_ventas': 'num_compras',
                    'nombre': 'nombre_cliente'
                }
            }
            
            # Aplicar mapeo de columnas si existe
            if table_name in column_mapping:
                df_prepared = df_prepared.rename(columns=column_mapping[table_name])
            
            # Convertir tipos de datos para compatibilidad con SQLite
            for col in df_prepared.columns:
                if df_prepared[col].dtype == 'bool':
                    df_prepared[col] = df_prepared[col].astype(int)
                elif df_prepared[col].dtype == 'datetime64[ns]':
                    df_prepared[col] = df_prepared[col].dt.strftime('%Y-%m-%d %H:%M:%S')
            
            return df_prepared
            
        except Exception as e:
            self.logger.error(f"Error al preparar datos para {table_name}: {str(e)}")
            raise
    
    def _create_indexes(self, engine: sa.engine.Engine) -> None:
        """
        Crear índices para optimizar consultas.
        
        Args:
            engine: Engine de SQLAlchemy
        """
        try:
            indexes = [
                "CREATE INDEX IF NOT EXISTS idx_ventas_fecha ON ventas(fecha)",
                "CREATE INDEX IF NOT EXISTS idx_ventas_producto ON ventas(producto_id)",
                "CREATE INDEX IF NOT EXISTS idx_ventas_cliente ON ventas(cliente_id)",
                "CREATE INDEX IF NOT EXISTS idx_productos_categoria ON productos(categoria)",
                "CREATE INDEX IF NOT EXISTS idx_clientes_ciudad ON clientes(ciudad)",
                "CREATE INDEX IF NOT EXISTS idx_inventario_stock ON inventario(stock_actual)"
            ]
            
            with engine.connect() as conn:
                for index_sql in indexes:
                    conn.execute(sa.text(index_sql))
                
                conn.commit()
            
            self.logger.info(f"Creados {len(indexes)} índices para optimización")
            
        except Exception as e:
            self.logger.error(f"Error al crear índices: {str(e)}")
    
    def _generate_load_statistics(self, transformed_data: Dict[str, pd.DataFrame]) -> None:
        """
        Generar estadísticas de la carga de datos.
        
        Args:
            transformed_data: Diccionario con DataFrames transformados
        """
        try:
            stats = {
                'fecha_carga': datetime.now().isoformat(),
                'tablas_cargadas': len(transformed_data),
                'total_registros': sum(len(df) for df in transformed_data.values()),
                'detalle_por_tabla': {}
            }
            
            for table_name, df in transformed_data.items():
                stats['detalle_por_tabla'][table_name] = {
                    'registros': len(df),
                    'columnas': len(df.columns),
                    'memoria_mb': round(df.memory_usage(deep=True).sum() / 1024 / 1024, 2)
                }
            
            # Guardar estadísticas en archivo JSON
            stats_file = Path(self.config.get('paths.data_processed')) / 'load_statistics.json'
            stats_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(stats_file, 'w', encoding='utf-8') as f:
                json.dump(stats, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"Estadísticas de carga guardadas en: {stats_file}")
            
        except Exception as e:
            self.logger.error(f"Error al generar estadísticas: {str(e)}")
    
    def load_specific_table(self, table_name: str, df: pd.DataFrame) -> bool:
        """
        Cargar datos en una tabla específica.
        
        Args:
            table_name: Nombre de la tabla
            df: DataFrame con los datos a cargar
            
        Returns:
            True si la carga fue exitosa, False en caso contrario
        """
        try:
            self.logger.info(f"Cargando datos en tabla específica: {table_name}")
            
            engine = self._create_database_connection()
            success = self._load_table(engine, table_name, df)
            
            if success:
                self.logger.info(f"Carga exitosa en tabla {table_name}")
            else:
                self.logger.error(f"Error en carga de tabla {table_name}")
            
            return success
            
        except Exception as e:
            self.logger.error(f"Error al cargar tabla específica {table_name}: {str(e)}")
            return False
    
    def get_table_info(self, table_name: str) -> Optional[Dict[str, Any]]:
        """
        Obtener información de una tabla específica.
        
        Args:
            table_name: Nombre de la tabla
            
        Returns:
            Diccionario con información de la tabla o None si no existe
        """
        try:
            engine = self._create_database_connection()
            
            with engine.connect() as conn:
                # Verificar si la tabla existe
                result = conn.execute(sa.text(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}'"))
                if not result.fetchone():
                    self.logger.warning(f"Tabla {table_name} no existe")
                    return None
                
                # Obtener información de la tabla
                result = conn.execute(sa.text(f"PRAGMA table_info({table_name})"))
                columns_info = result.fetchall()
                
                # Contar registros
                result = conn.execute(sa.text(f"SELECT COUNT(*) FROM {table_name}"))
                row_count = result.fetchone()[0]
                
                table_info = {
                    'nombre': table_name,
                    'columnas': len(columns_info),
                    'registros': row_count,
                    'esquema': [{'nombre': col[1], 'tipo': col[2], 'not_null': bool(col[3])} for col in columns_info]
                }
                
                return table_info
                
        except Exception as e:
            self.logger.error(f"Error al obtener información de tabla {table_name}: {str(e)}")
            return None
    
    def execute_query(self, query: str) -> Optional[pd.DataFrame]:
        """
        Ejecutar una consulta SQL personalizada.
        
        Args:
            query: Consulta SQL a ejecutar
            
        Returns:
            DataFrame con los resultados o None si hay error
        """
        try:
            engine = self._create_database_connection()
            
            with engine.connect() as conn:
                df = pd.read_sql_query(query, conn)
                self.logger.info(f"Consulta ejecutada exitosamente. Resultados: {len(df)} registros")
                return df
                
        except Exception as e:
            self.logger.error(f"Error al ejecutar consulta: {str(e)}")
            return None 