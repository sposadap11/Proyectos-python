"""
Módulo principal para la transformación y limpieza de datos.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
import re

from ..utils.logger import LoggerMixin
from ..utils.config_loader import ConfigLoader


class DataTransformer(LoggerMixin):
    """Clase principal para transformar y limpiar datos."""
    
    def __init__(self, config: ConfigLoader):
        """
        Inicializar el transformador de datos.
        
        Args:
            config: Instancia de ConfigLoader con la configuración
        """
        self.config = config
        self.cleaning_config = self.config.get_cleaning_config()
        self.validation_config = self.config.get_validation_config()
        
        self.logger.info("Transformador de datos inicializado")
    
    def transform_all(self, raw_data: Dict[str, pd.DataFrame]) -> Dict[str, pd.DataFrame]:
        """
        Transformar todos los datos extraídos.
        
        Args:
            raw_data: Diccionario con DataFrames de datos sin procesar
            
        Returns:
            Diccionario con DataFrames transformados
        """
        self.logger.info("Iniciando transformación de todos los datos")
        
        transformed_data = {}
        
        try:
            for table_name, df in raw_data.items():
                self.logger.info(f"Transformando tabla: {table_name}")
                
                # Aplicar transformaciones específicas según el tipo de tabla
                if table_name == 'ventas':
                    transformed_df = self._transform_ventas(df)
                elif table_name == 'productos':
                    transformed_df = self._transform_productos(df)
                elif table_name == 'clientes':
                    transformed_df = self._transform_clientes(df)
                elif table_name == 'categorias':
                    transformed_df = self._transform_categorias(df)
                elif table_name == 'inventario':
                    transformed_df = self._transform_inventario(df)
                else:
                    # Transformación genérica para otras tablas
                    transformed_df = self._transform_generic(df, table_name)
                
                transformed_data[table_name] = transformed_df
                self.logger.info(f"Transformación completada para {table_name}: {len(transformed_df)} registros")
            
            # Crear tablas derivadas
            transformed_data.update(self._create_derived_tables(transformed_data))
            
            self.logger.info(f"Transformación completada. {len(transformed_data)} tablas procesadas")
            return transformed_data
            
        except Exception as e:
            self.logger.error(f"Error en transformación de datos: {str(e)}")
            raise
    
    def _transform_ventas(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Transformar datos de ventas.
        
        Args:
            df: DataFrame con datos de ventas
            
        Returns:
            DataFrame transformado
        """
        try:
            # Crear copia para no modificar el original
            df_transformed = df.copy()
            
            # Convertir fecha a datetime
            df_transformed['fecha'] = pd.to_datetime(df_transformed['fecha'])
            
            # Agregar columnas derivadas
            df_transformed['mes'] = df_transformed['fecha'].dt.month
            df_transformed['año'] = df_transformed['fecha'].dt.year
            df_transformed['dia_semana'] = df_transformed['fecha'].dt.day_name()
            
            # Calcular total real si no existe o está mal calculado
            if 'total' not in df_transformed.columns:
                df_transformed['total'] = df_transformed['cantidad'] * df_transformed['precio']
            else:
                # Verificar si el total está bien calculado
                df_transformed['total_calculado'] = df_transformed['cantidad'] * df_transformed['precio']
                df_transformed['total_diferencia'] = abs(df_transformed['total'] - df_transformed['total_calculado'])
                
                # Corregir totales con diferencias significativas
                threshold = 0.01
                df_transformed.loc[df_transformed['total_diferencia'] > threshold, 'total'] = \
                    df_transformed.loc[df_transformed['total_diferencia'] > threshold, 'total_calculado']
                
                # Eliminar columnas temporales
                df_transformed = df_transformed.drop(['total_calculado', 'total_diferencia'], axis=1)
            
            # Limpiar datos
            df_transformed = self._clean_dataframe(df_transformed)
            
            # Validar tipos de datos
            df_transformed = self._validate_data_types(df_transformed, 'ventas')
            
            return df_transformed
            
        except Exception as e:
            self.logger.error(f"Error al transformar ventas: {str(e)}")
            raise
    
    def _transform_productos(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Transformar datos de productos.
        
        Args:
            df: DataFrame con datos de productos
            
        Returns:
            DataFrame transformado
        """
        try:
            df_transformed = df.copy()
            
            # Limpiar nombres de productos
            df_transformed['nombre'] = df_transformed['nombre'].str.strip()
            df_transformed['nombre'] = df_transformed['nombre'].str.title()
            
            # Normalizar categorías
            df_transformed['categoria'] = df_transformed['categoria'].str.strip()
            df_transformed['categoria'] = df_transformed['categoria'].str.title()
            
            # Limpiar descripciones
            if 'descripcion' in df_transformed.columns:
                df_transformed['descripcion'] = df_transformed['descripcion'].str.strip()
                df_transformed['descripcion'] = df_transformed['descripcion'].fillna('Sin descripción')
            
            # Validar precios
            df_transformed['precio'] = pd.to_numeric(df_transformed['precio'], errors='coerce')
            df_transformed = df_transformed[df_transformed['precio'] > 0]
            
            # Limpiar datos
            df_transformed = self._clean_dataframe(df_transformed)
            
            # Validar tipos de datos
            df_transformed = self._validate_data_types(df_transformed, 'productos')
            
            return df_transformed
            
        except Exception as e:
            self.logger.error(f"Error al transformar productos: {str(e)}")
            raise
    
    def _transform_clientes(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Transformar datos de clientes.
        
        Args:
            df: DataFrame con datos de clientes
            
        Returns:
            DataFrame transformado
        """
        try:
            df_transformed = df.copy()
            
            # Limpiar nombres
            df_transformed['nombre'] = df_transformed['nombre'].str.strip()
            df_transformed['nombre'] = df_transformed['nombre'].str.title()
            
            # Validar emails
            df_transformed['email'] = df_transformed['email'].str.lower().str.strip()
            df_transformed = df_transformed[df_transformed['email'].str.contains('@', na=False)]
            
            # Limpiar ciudades
            df_transformed['ciudad'] = df_transformed['ciudad'].str.strip()
            df_transformed['ciudad'] = df_transformed['ciudad'].str.title()
            
            # Convertir fecha de registro
            if 'fecha_registro' in df_transformed.columns:
                df_transformed['fecha_registro'] = pd.to_datetime(df_transformed['fecha_registro'])
            
            # Limpiar datos
            df_transformed = self._clean_dataframe(df_transformed)
            
            # Validar tipos de datos
            df_transformed = self._validate_data_types(df_transformed, 'clientes')
            
            return df_transformed
            
        except Exception as e:
            self.logger.error(f"Error al transformar clientes: {str(e)}")
            raise
    
    def _transform_categorias(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Transformar datos de categorías.
        
        Args:
            df: DataFrame con datos de categorías
            
        Returns:
            DataFrame transformado
        """
        try:
            df_transformed = df.copy()
            
            # Limpiar nombres
            df_transformed['nombre'] = df_transformed['nombre'].str.strip()
            df_transformed['nombre'] = df_transformed['nombre'].str.title()
            
            # Limpiar descripciones
            if 'descripcion' in df_transformed.columns:
                df_transformed['descripcion'] = df_transformed['descripcion'].str.strip()
                df_transformed['descripcion'] = df_transformed['descripcion'].fillna('Sin descripción')
            
            # Limpiar datos
            df_transformed = self._clean_dataframe(df_transformed)
            
            return df_transformed
            
        except Exception as e:
            self.logger.error(f"Error al transformar categorías: {str(e)}")
            raise
    
    def _transform_inventario(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Transformar datos de inventario.
        
        Args:
            df: DataFrame con datos de inventario
            
        Returns:
            DataFrame transformado
        """
        try:
            df_transformed = df.copy()
            
            # Convertir fechas
            if 'ultima_actualizacion' in df_transformed.columns:
                df_transformed['ultima_actualizacion'] = pd.to_datetime(df_transformed['ultima_actualizacion'])
            
            # Validar stocks
            df_transformed['stock_actual'] = pd.to_numeric(df_transformed['stock_actual'], errors='coerce')
            df_transformed['stock_minimo'] = pd.to_numeric(df_transformed['stock_minimo'], errors='coerce')
            
            # Agregar indicador de stock bajo
            df_transformed['stock_bajo'] = df_transformed['stock_actual'] <= df_transformed['stock_minimo']
            
            # Limpiar datos
            df_transformed = self._clean_dataframe(df_transformed)
            
            return df_transformed
            
        except Exception as e:
            self.logger.error(f"Error al transformar inventario: {str(e)}")
            raise
    
    def _transform_generic(self, df: pd.DataFrame, table_name: str) -> pd.DataFrame:
        """
        Transformación genérica para tablas no específicas.
        
        Args:
            df: DataFrame a transformar
            table_name: Nombre de la tabla
            
        Returns:
            DataFrame transformado
        """
        try:
            df_transformed = df.copy()
            
            # Limpiar datos
            df_transformed = self._clean_dataframe(df_transformed)
            
            self.logger.info(f"Transformación genérica aplicada a {table_name}")
            
            return df_transformed
            
        except Exception as e:
            self.logger.error(f"Error en transformación genérica de {table_name}: {str(e)}")
            raise
    
    def _clean_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Limpiar DataFrame aplicando reglas de limpieza.
        
        Args:
            df: DataFrame a limpiar
            
        Returns:
            DataFrame limpio
        """
        try:
            df_cleaned = df.copy()
            
            # Eliminar duplicados si está configurado
            if self.cleaning_config.get('remove_duplicates', True):
                initial_rows = len(df_cleaned)
                df_cleaned = df_cleaned.drop_duplicates()
                removed_rows = initial_rows - len(df_cleaned)
                if removed_rows > 0:
                    self.logger.info(f"Eliminados {removed_rows} registros duplicados")
            
            # Manejar valores faltantes
            fill_config = self.cleaning_config.get('fill_missing', {})
            strategy = fill_config.get('strategy', 'forward')
            
            if strategy == 'forward':
                df_cleaned = df_cleaned.fillna(method='ffill')
            elif strategy == 'backward':
                df_cleaned = df_cleaned.fillna(method='bfill')
            else:
                # Llenar con valores específicos
                numeric_fill = fill_config.get('numeric', 0)
                categorical_fill = fill_config.get('categorical', 'Unknown')
                
                for col in df_cleaned.columns:
                    if df_cleaned[col].dtype in ['int64', 'float64']:
                        df_cleaned[col] = df_cleaned[col].fillna(numeric_fill)
                    else:
                        df_cleaned[col] = df_cleaned[col].fillna(categorical_fill)
            
            # Manejar outliers si está configurado
            outliers_config = self.cleaning_config.get('outliers', {})
            if outliers_config.get('method') == 'iqr':
                df_cleaned = self._handle_outliers_iqr(df_cleaned, outliers_config.get('threshold', 1.5))
            
            return df_cleaned
            
        except Exception as e:
            self.logger.error(f"Error al limpiar DataFrame: {str(e)}")
            raise
    
    def _handle_outliers_iqr(self, df: pd.DataFrame, threshold: float = 1.5) -> pd.DataFrame:
        """
        Manejar outliers usando el método IQR.
        
        Args:
            df: DataFrame a procesar
            threshold: Umbral para detectar outliers
            
        Returns:
            DataFrame sin outliers
        """
        try:
            df_clean = df.copy()
            
            # Solo aplicar a columnas numéricas
            numeric_columns = df_clean.select_dtypes(include=[np.number]).columns
            
            for col in numeric_columns:
                Q1 = df_clean[col].quantile(0.25)
                Q3 = df_clean[col].quantile(0.75)
                IQR = Q3 - Q1
                
                lower_bound = Q1 - threshold * IQR
                upper_bound = Q3 + threshold * IQR
                
                # Contar outliers
                outliers_count = len(df_clean[(df_clean[col] < lower_bound) | (df_clean[col] > upper_bound)])
                
                if outliers_count > 0:
                    self.logger.info(f"Encontrados {outliers_count} outliers en columna {col}")
                    
                    # Reemplazar outliers con los límites
                    df_clean.loc[df_clean[col] < lower_bound, col] = lower_bound
                    df_clean.loc[df_clean[col] > upper_bound, col] = upper_bound
            
            return df_clean
            
        except Exception as e:
            self.logger.error(f"Error al manejar outliers: {str(e)}")
            return df
    
    def _validate_data_types(self, df: pd.DataFrame, table_name: str) -> pd.DataFrame:
        """
        Validar y convertir tipos de datos según la configuración.
        
        Args:
            df: DataFrame a validar
            table_name: Nombre de la tabla
            
        Returns:
            DataFrame con tipos de datos corregidos
        """
        try:
            df_validated = df.copy()
            
            data_types = self.validation_config.get('data_types', {}).get(table_name, {})
            
            for column, expected_type in data_types.items():
                if column in df_validated.columns:
                    try:
                        if expected_type == 'int':
                            df_validated[column] = pd.to_numeric(df_validated[column], errors='coerce').astype('Int64')
                        elif expected_type == 'float':
                            df_validated[column] = pd.to_numeric(df_validated[column], errors='coerce')
                        elif expected_type == 'datetime':
                            df_validated[column] = pd.to_datetime(df_validated[column], errors='coerce')
                        elif expected_type == 'str':
                            df_validated[column] = df_validated[column].astype(str)
                        
                        self.logger.debug(f"Tipo de dato validado para {table_name}.{column}: {expected_type}")
                        
                    except Exception as e:
                        self.logger.warning(f"Error al validar tipo de dato para {table_name}.{column}: {str(e)}")
            
            return df_validated
            
        except Exception as e:
            self.logger.error(f"Error en validación de tipos de datos: {str(e)}")
            return df
    
    def _create_derived_tables(self, transformed_data: Dict[str, pd.DataFrame]) -> Dict[str, pd.DataFrame]:
        """
        Crear tablas derivadas a partir de los datos transformados.
        
        Args:
            transformed_data: Diccionario con DataFrames transformados
            
        Returns:
            Diccionario con tablas derivadas
        """
        derived_tables = {}
        
        try:
            # Crear tabla de resumen de ventas por producto
            if 'ventas' in transformed_data and 'productos' in transformed_data:
                ventas = transformed_data['ventas']
                productos = transformed_data['productos']
                
                # Resumen de ventas por producto
                ventas_por_producto = ventas.groupby('producto_id').agg({
                    'cantidad': 'sum',
                    'total': 'sum',
                    'id': 'count'
                }).rename(columns={'id': 'num_ventas'})
                
                # Agregar información del producto
                ventas_por_producto = ventas_por_producto.merge(
                    productos[['id', 'nombre', 'categoria']], 
                    left_index=True, 
                    right_on='id'
                )
                
                derived_tables['ventas_por_producto'] = ventas_por_producto
                self.logger.info("Tabla derivada 'ventas_por_producto' creada")
            
            # Crear tabla de resumen de ventas por cliente
            if 'ventas' in transformed_data and 'clientes' in transformed_data:
                ventas = transformed_data['ventas']
                clientes = transformed_data['clientes']
                
                # Resumen de ventas por cliente
                ventas_por_cliente = ventas.groupby('cliente_id').agg({
                    'cantidad': 'sum',
                    'total': 'sum',
                    'id': 'count'
                }).rename(columns={'id': 'num_compras'})
                
                # Agregar información del cliente
                ventas_por_cliente = ventas_por_cliente.merge(
                    clientes[['id', 'nombre', 'ciudad']], 
                    left_index=True, 
                    right_on='id'
                )
                
                derived_tables['ventas_por_cliente'] = ventas_por_cliente
                self.logger.info("Tabla derivada 'ventas_por_cliente' creada")
            
            # Crear tabla de resumen de ventas por categoría
            if 'ventas' in transformed_data and 'productos' in transformed_data:
                ventas = transformed_data['ventas']
                productos = transformed_data['productos']
                
                # Unir ventas con productos para obtener categoría
                ventas_con_categoria = ventas.merge(
                    productos[['id', 'categoria']], 
                    left_on='producto_id', 
                    right_on='id', 
                    suffixes=('', '_producto')
                )
                
                # Resumen por categoría
                ventas_por_categoria = ventas_con_categoria.groupby('categoria').agg({
                    'cantidad': 'sum',
                    'total': 'sum',
                    'id': 'count'
                }).rename(columns={'id': 'num_ventas'})
                
                derived_tables['ventas_por_categoria'] = ventas_por_categoria
                self.logger.info("Tabla derivada 'ventas_por_categoria' creada")
            
            return derived_tables
            
        except Exception as e:
            self.logger.error(f"Error al crear tablas derivadas: {str(e)}")
            return derived_tables 