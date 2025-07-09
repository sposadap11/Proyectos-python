"""
Módulo principal para la extracción de datos de múltiples fuentes.
"""

import pandas as pd
import sqlite3
import requests
import json
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime
import time

from ..utils.logger import LoggerMixin
from ..utils.config_loader import ConfigLoader


class DataExtractor(LoggerMixin):
    """Clase principal para extraer datos de múltiples fuentes."""
    
    def __init__(self, config: ConfigLoader):
        """
        Inicializar el extractor de datos.
        
        Args:
            config: Instancia de ConfigLoader con la configuración
        """
        self.config = config
        self.raw_data_path = Path(self.config.get('paths.data_raw'))
        self.api_config = self.config.get_api_config()
        
        # Crear directorio si no existe
        self.raw_data_path.mkdir(parents=True, exist_ok=True)
        
        self.logger.info("Extractor de datos inicializado")
    
    def extract_all(self) -> Dict[str, pd.DataFrame]:
        """
        Extraer datos de todas las fuentes configuradas.
        
        Returns:
            Diccionario con DataFrames de datos extraídos
        """
        self.logger.info("Iniciando extracción de datos de todas las fuentes")
        
        extracted_data = {}
        
        try:
            # Extraer datos de archivos CSV
            extracted_data.update(self._extract_csv_files())
            
            # Extraer datos de API (simulada)
            extracted_data.update(self._extract_api_data())
            
            # Extraer datos de base de datos (si existe)
            extracted_data.update(self._extract_database_data())
            
            self.logger.info(f"Extracción completada. {len(extracted_data)} fuentes procesadas")
            return extracted_data
            
        except Exception as e:
            self.logger.error(f"Error en extracción de datos: {str(e)}")
            raise
    
    def _extract_csv_files(self) -> Dict[str, pd.DataFrame]:
        """
        Extraer datos de archivos CSV en el directorio raw.
        
        Returns:
            Diccionario con DataFrames de archivos CSV
        """
        csv_data = {}
        
        try:
            # Buscar archivos CSV en el directorio raw
            csv_files = list(self.raw_data_path.glob("*.csv"))
            
            if not csv_files:
                self.logger.warning("No se encontraron archivos CSV en el directorio raw")
                return csv_data
            
            for csv_file in csv_files:
                try:
                    # Extraer nombre del archivo sin extensión como clave
                    key = csv_file.stem
                    
                    self.logger.info(f"Extrayendo datos de: {csv_file.name}")
                    
                    # Leer archivo CSV
                    df = pd.read_csv(csv_file, encoding='utf-8')
                    
                    # Validar que el DataFrame no esté vacío
                    if df.empty:
                        self.logger.warning(f"Archivo {csv_file.name} está vacío")
                        continue
                    
                    csv_data[key] = df
                    self.logger.info(f"Extraídos {len(df)} registros de {csv_file.name}")
                    
                except Exception as e:
                    self.logger.error(f"Error al extraer {csv_file.name}: {str(e)}")
                    continue
            
            return csv_data
            
        except Exception as e:
            self.logger.error(f"Error al extraer archivos CSV: {str(e)}")
            raise
    
    def _extract_api_data(self) -> Dict[str, pd.DataFrame]:
        """
        Extraer datos de APIs externas (simulado).
        
        Returns:
            Diccionario con DataFrames de datos de API
        """
        api_data = {}
        
        try:
            # Simular datos de API de categorías
            self.logger.info("Extrayendo datos de API de categorías")
            
            # Datos simulados de categorías
            categorias_data = {
                'id': [1, 2, 3, 4, 5],
                'nombre': ['Electrónicos', 'Accesorios', 'Ropa', 'Hogar', 'Deportes'],
                'descripcion': [
                    'Productos electrónicos y tecnológicos',
                    'Accesorios para dispositivos',
                    'Ropa y moda',
                    'Productos para el hogar',
                    'Artículos deportivos'
                ],
                'activo': [True, True, False, True, False]
            }
            
            api_data['categorias'] = pd.DataFrame(categorias_data)
            self.logger.info(f"Extraídos {len(api_data['categorias'])} registros de API de categorías")
            
            # Simular datos de inventario
            self.logger.info("Extrayendo datos de API de inventario")
            
            inventario_data = {
                'producto_id': [101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111],
                'stock_actual': [45, 25, 85, 20, 180, 10, 65, 130, 8, 35, 50],
                'stock_minimo': [10, 5, 20, 5, 50, 3, 15, 30, 2, 10, 15],
                'ultima_actualizacion': [
                    '2024-01-15', '2024-01-16', '2024-01-17', '2024-01-18',
                    '2024-01-19', '2024-01-20', '2024-01-21', '2024-01-22',
                    '2024-01-23', '2024-01-24', '2024-01-25'
                ]
            }
            
            api_data['inventario'] = pd.DataFrame(inventario_data)
            self.logger.info(f"Extraídos {len(api_data['inventario'])} registros de API de inventario")
            
            return api_data
            
        except Exception as e:
            self.logger.error(f"Error al extraer datos de API: {str(e)}")
            raise
    
    def _extract_database_data(self) -> Dict[str, pd.DataFrame]:
        """
        Extraer datos de base de datos existente (si existe).
        
        Returns:
            Diccionario con DataFrames de datos de base de datos
        """
        db_data = {}
        
        try:
            # Verificar si existe una base de datos previa
            db_path = Path(self.config.get('database.path'))
            
            if not db_path.exists():
                self.logger.info("No se encontró base de datos previa para extraer")
                return db_data
            
            self.logger.info(f"Extrayendo datos de base de datos: {db_path}")
            
            # Conectar a la base de datos
            with sqlite3.connect(db_path) as conn:
                # Obtener lista de tablas
                cursor = conn.cursor()
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
                tables = cursor.fetchall()
                
                for table in tables:
                    table_name = table[0]
                    try:
                        # Leer tabla completa
                        df = pd.read_sql_query(f"SELECT * FROM {table_name}", conn)
                        
                        if not df.empty:
                            db_data[table_name] = df
                            self.logger.info(f"Extraídos {len(df)} registros de tabla {table_name}")
                        else:
                            self.logger.warning(f"Tabla {table_name} está vacía")
                            
                    except Exception as e:
                        self.logger.error(f"Error al extraer tabla {table_name}: {str(e)}")
                        continue
            
            return db_data
            
        except Exception as e:
            self.logger.error(f"Error al extraer datos de base de datos: {str(e)}")
            raise
    
    def extract_specific_source(self, source_name: str) -> Optional[pd.DataFrame]:
        """
        Extraer datos de una fuente específica.
        
        Args:
            source_name: Nombre de la fuente ('ventas', 'productos', 'clientes', etc.)
            
        Returns:
            DataFrame con los datos extraídos o None si no se encuentra
        """
        try:
            self.logger.info(f"Extrayendo datos de fuente específica: {source_name}")
            
            # Buscar en archivos CSV
            csv_file = self.raw_data_path / f"{source_name}.csv"
            if csv_file.exists():
                df = pd.read_csv(csv_file, encoding='utf-8')
                self.logger.info(f"Extraídos {len(df)} registros de {source_name}.csv")
                return df
            
            # Buscar en datos de API simulados
            if source_name == 'categorias':
                return self._extract_api_data().get('categorias')
            elif source_name == 'inventario':
                return self._extract_api_data().get('inventario')
            
            # Buscar en base de datos
            db_path = Path(self.config.get('database.path'))
            if db_path.exists():
                with sqlite3.connect(db_path) as conn:
                    df = pd.read_sql_query(f"SELECT * FROM {source_name}", conn)
                    if not df.empty:
                        self.logger.info(f"Extraídos {len(df)} registros de tabla {source_name}")
                        return df
            
            self.logger.warning(f"Fuente '{source_name}' no encontrada")
            return None
            
        except Exception as e:
            self.logger.error(f"Error al extraer fuente específica '{source_name}': {str(e)}")
            return None
    
    def validate_extracted_data(self, data: Dict[str, pd.DataFrame]) -> bool:
        """
        Validar los datos extraídos.
        
        Args:
            data: Diccionario con DataFrames extraídos
            
        Returns:
            True si los datos son válidos, False en caso contrario
        """
        try:
            self.logger.info("Validando datos extraídos")
            
            if not data:
                self.logger.error("No hay datos para validar")
                return False
            
            validation_config = self.config.get_validation_config()
            required_columns = validation_config.get('required_columns', {})
            
            for table_name, df in data.items():
                if table_name in required_columns:
                    required_cols = required_columns[table_name]
                    missing_cols = [col for col in required_cols if col not in df.columns]
                    
                    if missing_cols:
                        self.logger.error(f"Tabla '{table_name}' falta columnas requeridas: {missing_cols}")
                        return False
                    
                    self.logger.info(f"Tabla '{table_name}' validada correctamente")
            
            self.logger.info("Validación de datos completada exitosamente")
            return True
            
        except Exception as e:
            self.logger.error(f"Error en validación de datos: {str(e)}")
            return False 