"""
Config Loader Module - Competitive Price Intelligence Platform
Cargador de configuración centralizado
"""

import os
import yaml
import json
from pathlib import Path
from typing import Dict, Any, Optional, Union
from dotenv import load_dotenv


class ConfigLoader:
    """Cargador de configuración con soporte para múltiples formatos."""
    
    def __init__(self, config_path: str = "config/config.yaml"):
        """Inicializar cargador de configuración."""
        self.config_path = Path(config_path)
        self.config = {}
        self.env_vars = {}
        
        # Cargar variables de entorno
        self._load_environment_variables()
        
        # Cargar configuración
        self._load_configuration()
        
        # Validar configuración
        self._validate_configuration()
    
    def _load_environment_variables(self):
        """Cargar variables de entorno desde archivo .env."""
        # Buscar archivo .env en diferentes ubicaciones
        env_files = [
            ".env",
            "env.example",
            "../.env",
            "../../.env"
        ]
        
        for env_file in env_files:
            env_path = Path(env_file)
            if env_path.exists():
                load_dotenv(env_path)
                break
        
        # Cargar variables de entorno relevantes
        self.env_vars = {
            'SCRAPER_DELAY': os.getenv('SCRAPER_DELAY'),
            'SCRAPER_TIMEOUT': os.getenv('SCRAPER_TIMEOUT'),
            'DATABASE_URL': os.getenv('DATABASE_URL'),
            'MINIO_ENDPOINT': os.getenv('MINIO_ENDPOINT'),
            'MINIO_ACCESS_KEY': os.getenv('MINIO_ACCESS_KEY'),
            'MINIO_SECRET_KEY': os.getenv('MINIO_SECRET_KEY'),
            'LOG_LEVEL': os.getenv('LOG_LEVEL'),
            'DEBUG': os.getenv('DEBUG'),
        }
    
    def _load_configuration(self):
        """Cargar configuración desde archivo."""
        try:
            if self.config_path.exists():
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    self.config = yaml.safe_load(f)
            else:
                # Crear configuración por defecto
                self.config = self._get_default_config()
                
                # Guardar configuración por defecto
                self.config_path.parent.mkdir(parents=True, exist_ok=True)
                with open(self.config_path, 'w', encoding='utf-8') as f:
                    yaml.dump(self.config, f, default_flow_style=False, indent=2)
        
        except Exception as e:
            print(f"Error cargando configuración: {e}")
            self.config = self._get_default_config()
        
        # Sobrescribir con variables de entorno
        self._override_with_env_vars()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Obtener configuración por defecto."""
        return {
            'paths': {
                'data': {
                    'raw': 'data/raw',
                    'processed': 'data/processed',
                    'reports': 'data/reports',
                    'warehouse': 'data/warehouse.db'
                },
                'logs': 'logs',
                'dbt_project': 'dbt_project',
                'config': 'config'
            },
            'database': {
                'type': 'duckdb',
                'url': 'duckdb:///data/warehouse.db',
                'pool_size': 10,
                'max_overflow': 20,
                'pool_timeout': 30,
                'echo': False
            },
            'storage': {
                'type': 'minio',
                'endpoint': 'localhost:9000',
                'access_key': 'minioadmin',
                'secret_key': 'minioadmin',
                'bucket_name': 'price-intelligence',
                'secure': False,
                'region': 'us-east-1'
            },
            'scraping': {
                'delay': 2,
                'timeout': 30,
                'retries': 3,
                'user_agent_rotation': True,
                'use_proxies': False,
                'max_concurrent_requests': 16,
                'download_delay': 1,
                'respect_robots_txt': True,
                'competitors': {
                    'amazon': {
                        'enabled': True,
                        'base_url': 'https://www.amazon.com',
                        'categories': ['electronics', 'books', 'home'],
                        'max_pages': 10,
                        'products_per_page': 48
                    },
                    'mercadolibre': {
                        'enabled': True,
                        'base_url': 'https://www.mercadolibre.com',
                        'categories': ['computacion', 'libros', 'hogar'],
                        'max_pages': 10,
                        'products_per_page': 50
                    }
                }
            },
            'processing': {
                'batch_size': 1000,
                'chunk_size': 100,
                'parallel_workers': 4,
                'cleaning': {
                    'remove_duplicates': True,
                    'fill_missing_values': True,
                    'validate_prices': True,
                    'normalize_text': True
                },
                'transformation': {
                    'currency_conversion': True,
                    'price_normalization': True,
                    'category_mapping': True,
                    'brand_extraction': True
                }
            },
            'analytics': {
                'competitiveness': {
                    'price_threshold': 0.10,
                    'market_share_calculation': True,
                    'price_elasticity_analysis': True
                },
                'alerts': {
                    'price_drop_threshold': 0.15,
                    'price_increase_threshold': 0.20,
                    'new_competitor_threshold': 0.05
                },
                'reports': {
                    'daily_summary': True,
                    'weekly_analysis': True,
                    'monthly_trends': True,
                    'competitor_comparison': True
                }
            },
            'monitoring': {
                'check_interval_minutes': 30,
                'alert_channels': ['email', 'slack', 'webhook'],
                'metrics': ['price_changes', 'competitor_activity', 'data_quality', 'system_performance'],
                'dashboards': {
                    'grafana_url': 'http://localhost:3000',
                    'prometheus_url': 'http://localhost:9090'
                }
            },
            'logging': {
                'level': 'INFO',
                'format': 'json',
                'file': 'logs/app.log',
                'max_size': '100MB',
                'backup_count': 5,
                'modules': {
                    'scrapers': 'INFO',
                    'transformers': 'INFO',
                    'loaders': 'INFO',
                    'analytics': 'INFO',
                    'orchestration': 'INFO'
                }
            },
            'development': {
                'debug_mode': False,
                'test_data_enabled': True,
                'mock_scraping': False,
                'local_storage': True,
                'testing': {
                    'unit_tests': True,
                    'integration_tests': True,
                    'data_quality_tests': True,
                    'performance_tests': True
                }
            }
        }
    
    def _override_with_env_vars(self):
        """Sobrescribir configuración con variables de entorno."""
        # Sobrescribir valores específicos
        if self.env_vars.get('SCRAPER_DELAY'):
            self.config['scraping']['delay'] = int(self.env_vars['SCRAPER_DELAY'])
        
        if self.env_vars.get('SCRAPER_TIMEOUT'):
            self.config['scraping']['timeout'] = int(self.env_vars['SCRAPER_TIMEOUT'])
        
        if self.env_vars.get('DATABASE_URL'):
            self.config['database']['url'] = self.env_vars['DATABASE_URL']
        
        if self.env_vars.get('MINIO_ENDPOINT'):
            self.config['storage']['endpoint'] = self.env_vars['MINIO_ENDPOINT']
        
        if self.env_vars.get('MINIO_ACCESS_KEY'):
            self.config['storage']['access_key'] = self.env_vars['MINIO_ACCESS_KEY']
        
        if self.env_vars.get('MINIO_SECRET_KEY'):
            self.config['storage']['secret_key'] = self.env_vars['MINIO_SECRET_KEY']
        
        if self.env_vars.get('LOG_LEVEL'):
            self.config['logging']['level'] = self.env_vars['LOG_LEVEL']
        
        if self.env_vars.get('DEBUG'):
            self.config['development']['debug_mode'] = self.env_vars['DEBUG'].lower() == 'true'
    
    def _validate_configuration(self):
        """Validar configuración cargada."""
        required_sections = ['paths', 'database', 'storage', 'scraping', 'processing', 'analytics']
        
        for section in required_sections:
            if section not in self.config:
                raise ValueError(f"Sección requerida '{section}' no encontrada en configuración")
        
        # Validar rutas
        paths = self.config['paths']
        for path_type, path_value in paths.items():
            if isinstance(path_value, dict):
                for sub_path, sub_value in path_value.items():
                    if not isinstance(sub_value, str):
                        raise ValueError(f"Ruta inválida en {path_type}.{sub_path}")
            elif not isinstance(path_value, str):
                raise ValueError(f"Ruta inválida en {path_type}")
    
    def get(self, key: str, default: Any = None) -> Any:
        """Obtener valor de configuración usando notación de puntos."""
        keys = key.split('.')
        value = self.config
        
        try:
            for k in keys:
                value = value[k]
            return value
        except (KeyError, TypeError):
            return default
    
    def set(self, key: str, value: Any):
        """Establecer valor de configuración usando notación de puntos."""
        keys = key.split('.')
        config = self.config
        
        # Navegar hasta el penúltimo nivel
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        # Establecer valor
        config[keys[-1]] = value
    
    def get_section(self, section: str) -> Dict[str, Any]:
        """Obtener sección completa de configuración."""
        return self.config.get(section, {})
    
    def get_database_config(self) -> Dict[str, Any]:
        """Obtener configuración de base de datos."""
        return self.config.get('database', {})
    
    def get_storage_config(self) -> Dict[str, Any]:
        """Obtener configuración de almacenamiento."""
        return self.config.get('storage', {})
    
    def get_scraping_config(self) -> Dict[str, Any]:
        """Obtener configuración de scraping."""
        return self.config.get('scraping', {})
    
    def get_processing_config(self) -> Dict[str, Any]:
        """Obtener configuración de procesamiento."""
        return self.config.get('processing', {})
    
    def get_analytics_config(self) -> Dict[str, Any]:
        """Obtener configuración de análisis."""
        return self.config.get('analytics', {})
    
    def get_monitoring_config(self) -> Dict[str, Any]:
        """Obtener configuración de monitoreo."""
        return self.config.get('monitoring', {})
    
    def get_logging_config(self) -> Dict[str, Any]:
        """Obtener configuración de logging."""
        return self.config.get('logging', {})
    
    def get_development_config(self) -> Dict[str, Any]:
        """Obtener configuración de desarrollo."""
        return self.config.get('development', {})
    
    def get_path(self, path_type: str, sub_path: Optional[str] = None) -> str:
        """Obtener ruta específica."""
        paths = self.config.get('paths', {})
        
        if sub_path:
            return paths.get(path_type, {}).get(sub_path, '')
        else:
            return paths.get(path_type, '')
    
    def is_development_mode(self) -> bool:
        """Verificar si está en modo desarrollo."""
        return self.config.get('development', {}).get('debug_mode', False)
    
    def is_testing_enabled(self) -> bool:
        """Verificar si las pruebas están habilitadas."""
        return self.config.get('development', {}).get('testing', {}).get('unit_tests', True)
    
    def get_competitor_config(self, competitor: str) -> Dict[str, Any]:
        """Obtener configuración específica de un competidor."""
        competitors = self.config.get('scraping', {}).get('competitors', {})
        return competitors.get(competitor, {})
    
    def get_enabled_competitors(self) -> list:
        """Obtener lista de competidores habilitados."""
        competitors = self.config.get('scraping', {}).get('competitors', {})
        return [
            name for name, config in competitors.items()
            if config.get('enabled', False)
        ]
    
    def save_config(self, file_path: Optional[str] = None):
        """Guardar configuración en archivo."""
        if file_path is None:
            file_path = self.config_path
        
        with open(file_path, 'w', encoding='utf-8') as f:
            yaml.dump(self.config, f, default_flow_style=False, indent=2)
    
    def export_config(self, format: str = 'yaml') -> str:
        """Exportar configuración en formato específico."""
        if format.lower() == 'json':
            return json.dumps(self.config, indent=2)
        elif format.lower() == 'yaml':
            return yaml.dump(self.config, default_flow_style=False, indent=2)
        else:
            raise ValueError(f"Formato no soportado: {format}")
    
    def reload_config(self):
        """Recargar configuración desde archivo."""
        self._load_configuration()
    
    def get_all_config(self) -> Dict[str, Any]:
        """Obtener toda la configuración."""
        return self.config.copy()
    
    def validate_competitor_config(self, competitor: str) -> bool:
        """Validar configuración de un competidor específico."""
        config = self.get_competitor_config(competitor)
        
        required_fields = ['base_url', 'categories', 'max_pages', 'products_per_page']
        
        for field in required_fields:
            if field not in config:
                return False
        
        return True


# Función de conveniencia para obtener instancia de configuración
def get_config(config_path: str = "config/config.yaml") -> ConfigLoader:
    """Obtener instancia de configuración."""
    return ConfigLoader(config_path)


# Función para crear configuración desde plantilla
def create_config_from_template(template_path: str, output_path: str, **kwargs):
    """Crear configuración desde plantilla con valores personalizados."""
    try:
        # Cargar plantilla
        with open(template_path, 'r', encoding='utf-8') as f:
            template_content = f.read()
        
        # Reemplazar placeholders
        for key, value in kwargs.items():
            template_content = template_content.replace(f"{{{{{key}}}}}", str(value))
        
        # Guardar configuración
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(template_content)
        
        return True
        
    except Exception as e:
        print(f"Error creando configuración desde plantilla: {e}")
        return False 