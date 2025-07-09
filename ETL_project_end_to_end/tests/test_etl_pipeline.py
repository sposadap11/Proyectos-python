"""
Tests unitarios para el pipeline ETL completo.
"""

import pytest
import pandas as pd
import tempfile
import shutil
from pathlib import Path
import sys
import os

# Agregar el directorio src al path
sys.path.append(str(Path(__file__).parent.parent / "src"))

from src.utils.config_loader import ConfigLoader
from src.extractors.data_extractor import DataExtractor
from src.transformers.data_transformer import DataTransformer
from src.loaders.data_loader import DataLoader


class TestETLPipeline:
    """Clase de tests para el pipeline ETL."""
    
    @pytest.fixture
    def temp_dir(self):
        """Crear directorio temporal para tests."""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)
    
    @pytest.fixture
    def sample_data(self):
        """Crear datos de ejemplo para tests."""
        return {
            'ventas': pd.DataFrame({
                'id': [1, 2, 3],
                'fecha': ['2024-01-15', '2024-01-16', '2024-01-17'],
                'producto_id': [101, 102, 103],
                'cliente_id': [1001, 1002, 1003],
                'cantidad': [2, 1, 3],
                'precio': [29.99, 49.99, 19.99],
                'total': [59.98, 49.99, 59.97]
            }),
            'productos': pd.DataFrame({
                'id': [101, 102, 103],
                'nombre': ['Laptop HP', 'Smartphone Samsung', 'Auriculares'],
                'categoria': ['Electrónicos', 'Electrónicos', 'Accesorios'],
                'precio': [29.99, 49.99, 19.99],
                'stock': [50, 30, 100],
                'descripcion': ['Laptop de 15 pulgadas', 'Teléfono inteligente', 'Auriculares inalámbricos']
            }),
            'clientes': pd.DataFrame({
                'id': [1001, 1002, 1003],
                'nombre': ['Juan Pérez', 'María García', 'Carlos López'],
                'email': ['juan@email.com', 'maria@email.com', 'carlos@email.com'],
                'ciudad': ['Madrid', 'Barcelona', 'Valencia'],
                'telefono': ['+34 600 123 456', '+34 600 234 567', '+34 600 345 678'],
                'fecha_registro': ['2023-01-15', '2023-02-20', '2023-03-10']
            })
        }
    
    @pytest.fixture
    def config(self, temp_dir):
        """Crear configuración temporal para tests."""
        config_data = {
            'project': {
                'name': 'Test ETL Project',
                'version': '1.0.0'
            },
            'paths': {
                'data_raw': str(Path(temp_dir) / 'raw'),
                'data_processed': str(Path(temp_dir) / 'processed'),
                'data_reports': str(Path(temp_dir) / 'reports'),
                'logs': str(Path(temp_dir) / 'logs')
            },
            'database': {
                'type': 'sqlite',
                'path': str(Path(temp_dir) / 'processed' / 'test.db'),
                'tables': ['ventas', 'productos', 'clientes']
            },
            'logging': {
                'level': 'INFO',
                'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            },
            'validation': {
                'required_columns': {
                    'ventas': ['id', 'fecha', 'producto_id', 'cliente_id', 'cantidad', 'precio'],
                    'productos': ['id', 'nombre', 'categoria', 'precio'],
                    'clientes': ['id', 'nombre', 'email', 'ciudad']
                },
                'data_types': {
                    'ventas': {
                        'id': 'int',
                        'fecha': 'datetime',
                        'producto_id': 'int',
                        'cliente_id': 'int',
                        'cantidad': 'int',
                        'precio': 'float'
                    },
                    'productos': {
                        'id': 'int',
                        'nombre': 'str',
                        'categoria': 'str',
                        'precio': 'float'
                    },
                    'clientes': {
                        'id': 'int',
                        'nombre': 'str',
                        'email': 'str',
                        'ciudad': 'str'
                    }
                }
            },
            'cleaning': {
                'remove_duplicates': True,
                'fill_missing': {
                    'strategy': 'forward',
                    'numeric': 0,
                    'categorical': 'Unknown'
                },
                'outliers': {
                    'method': 'iqr',
                    'threshold': 1.5
                }
            }
        }
        
        # Crear archivo de configuración temporal
        import yaml
        config_file = Path(temp_dir) / 'test_config.yaml'
        with open(config_file, 'w', encoding='utf-8') as f:
            yaml.dump(config_data, f, default_flow_style=False)
        
        return ConfigLoader(str(config_file))
    
    def test_config_loader(self, config):
        """Test del cargador de configuración."""
        assert config.get('project.name') == 'Test ETL Project'
        assert config.get('project.version') == '1.0.0'
        assert config.validate_config() is True
    
    def test_data_extractor(self, config, sample_data, temp_dir):
        """Test del extractor de datos."""
        # Crear archivos CSV de prueba
        raw_dir = Path(temp_dir) / 'raw'
        raw_dir.mkdir(parents=True, exist_ok=True)
        
        for table_name, df in sample_data.items():
            df.to_csv(raw_dir / f'{table_name}.csv', index=False)
        
        # Probar extractor
        extractor = DataExtractor(config)
        extracted_data = extractor.extract_csv_files()
        
        assert 'ventas' in extracted_data
        assert 'productos' in extracted_data
        assert 'clientes' in extracted_data
        assert len(extracted_data['ventas']) == 3
        assert len(extracted_data['productos']) == 3
        assert len(extracted_data['clientes']) == 3
    
    def test_data_transformer(self, config, sample_data):
        """Test del transformador de datos."""
        transformer = DataTransformer(config)
        transformed_data = transformer.transform_all(sample_data)
        
        assert 'ventas' in transformed_data
        assert 'productos' in transformed_data
        assert 'clientes' in transformed_data
        
        # Verificar transformaciones específicas
        ventas_transformed = transformed_data['ventas']
        assert 'mes' in ventas_transformed.columns
        assert 'año' in ventas_transformed.columns
        assert 'dia_semana' in ventas_transformed.columns
        
        # Verificar que las fechas se convirtieron correctamente
        assert pd.api.types.is_datetime64_any_dtype(ventas_transformed['fecha'])
    
    def test_data_loader(self, config, sample_data):
        """Test del cargador de datos."""
        # Transformar datos primero
        transformer = DataTransformer(config)
        transformed_data = transformer.transform_all(sample_data)
        
        # Cargar datos
        loader = DataLoader(config)
        success = loader.load_all(transformed_data)
        
        assert success is True
        
        # Verificar que la base de datos se creó
        db_path = Path(config.get('database.path'))
        assert db_path.exists()
        
        # Verificar que las tablas se crearon
        import sqlite3
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [row[0] for row in cursor.fetchall()]
            
            assert 'ventas' in tables
            assert 'productos' in tables
            assert 'clientes' in tables
    
    def test_full_pipeline(self, config, sample_data, temp_dir):
        """Test del pipeline ETL completo."""
        # Crear archivos CSV de prueba
        raw_dir = Path(temp_dir) / 'raw'
        raw_dir.mkdir(parents=True, exist_ok=True)
        
        for table_name, df in sample_data.items():
            df.to_csv(raw_dir / f'{table_name}.csv', index=False)
        
        # Ejecutar pipeline completo
        extractor = DataExtractor(config)
        transformer = DataTransformer(config)
        loader = DataLoader(config)
        
        # Extraer
        raw_data = extractor.extract_all()
        assert len(raw_data) >= 3  # Al menos ventas, productos, clientes
        
        # Transformar
        transformed_data = transformer.transform_all(raw_data)
        assert len(transformed_data) >= 3
        
        # Cargar
        success = loader.load_all(transformed_data)
        assert success is True
        
        # Verificar resultados
        db_path = Path(config.get('database.path'))
        assert db_path.exists()
        
        # Verificar datos en la base de datos
        import sqlite3
        with sqlite3.connect(db_path) as conn:
            # Verificar ventas
            df_ventas = pd.read_sql_query("SELECT * FROM ventas", conn)
            assert len(df_ventas) == 3
            
            # Verificar productos
            df_productos = pd.read_sql_query("SELECT * FROM productos", conn)
            assert len(df_productos) == 3
            
            # Verificar clientes
            df_clientes = pd.read_sql_query("SELECT * FROM clientes", conn)
            assert len(df_clientes) == 3
    
    def test_data_validation(self, config, sample_data):
        """Test de validación de datos."""
        extractor = DataExtractor(config)
        
        # Los datos de ejemplo deberían ser válidos
        assert extractor.validate_extracted_data(sample_data) is True
        
        # Probar con datos inválidos
        invalid_data = {
            'ventas': pd.DataFrame({
                'id': [1, 2],
                'fecha': ['2024-01-15', '2024-01-16']
                # Falta columnas requeridas
            })
        }
        
        assert extractor.validate_extracted_data(invalid_data) is False
    
    def test_data_cleaning(self, config):
        """Test de limpieza de datos."""
        transformer = DataTransformer(config)
        
        # Crear datos con problemas
        dirty_data = pd.DataFrame({
            'id': [1, 2, 2, 3, None],  # Duplicado y valor nulo
            'nombre': ['Juan', 'María', 'María', 'Carlos', 'Ana'],
            'precio': [10.0, 20.0, 20.0, 30.0, 40.0]
        })
        
        # Aplicar limpieza
        cleaned_data = transformer._clean_dataframe(dirty_data)
        
        # Verificar que se eliminaron duplicados
        assert len(cleaned_data) < len(dirty_data)
        
        # Verificar que se llenaron valores nulos
        assert cleaned_data['id'].isna().sum() == 0
    
    def test_error_handling(self, config):
        """Test de manejo de errores."""
        # Probar con configuración inválida
        invalid_config_data = {
            'paths': {
                'data_raw': '/path/that/does/not/exist'
            }
        }
        
        import yaml
        import tempfile
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump(invalid_config_data, f)
            temp_config_file = f.name
        
        try:
            invalid_config = ConfigLoader(temp_config_file)
            extractor = DataExtractor(invalid_config)
            
            # Debería manejar el error graciosamente
            extracted_data = extractor.extract_csv_files()
            assert isinstance(extracted_data, dict)
            
        finally:
            os.unlink(temp_config_file)


if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 