"""
Módulo para cargar y manejar la configuración del proyecto.
"""

import yaml
import os
from pathlib import Path
from typing import Dict, Any, Optional
from .logger import LoggerMixin


class ConfigLoader(LoggerMixin):
    """Clase para cargar y manejar la configuración del proyecto."""
    
    def __init__(self, config_path: str = "config/config.yaml"):
        """
        Inicializar el cargador de configuración.
        
        Args:
            config_path: Ruta al archivo de configuración YAML
        """
        self.config_path = Path(config_path)
        self.config = self._load_config()
        self.logger.info(f"Configuración cargada desde: {self.config_path}")
    
    def _load_config(self) -> Dict[str, Any]:
        """
        Cargar configuración desde archivo YAML.
        
        Returns:
            Diccionario con la configuración
            
        Raises:
            FileNotFoundError: Si no se encuentra el archivo de configuración
            yaml.YAMLError: Si hay error en el formato YAML
        """
        if not self.config_path.exists():
            raise FileNotFoundError(f"Archivo de configuración no encontrado: {self.config_path}")
        
        try:
            with open(self.config_path, 'r', encoding='utf-8') as file:
                config = yaml.safe_load(file)
                self.logger.debug("Configuración cargada exitosamente")
                return config
        except yaml.YAMLError as e:
            self.logger.error(f"Error al parsear archivo YAML: {e}")
            raise
        except Exception as e:
            self.logger.error(f"Error inesperado al cargar configuración: {e}")
            raise
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Obtener valor de configuración por clave.
        
        Args:
            key: Clave de configuración (puede usar notación de punto: 'database.path')
            default: Valor por defecto si no se encuentra la clave
            
        Returns:
            Valor de configuración
        """
        keys = key.split('.')
        value = self.config
        
        try:
            for k in keys:
                value = value[k]
            return value
        except (KeyError, TypeError):
            self.logger.debug(f"Clave '{key}' no encontrada, usando valor por defecto: {default}")
            return default
    
    def get_path(self, key: str) -> Optional[Path]:
        """
        Obtener ruta de configuración como objeto Path.
        
        Args:
            key: Clave de configuración para la ruta
            
        Returns:
            Objeto Path o None si no se encuentra
        """
        path_str = self.get(key)
        if path_str:
            return Path(path_str)
        return None
    
    def get_database_config(self) -> Dict[str, Any]:
        """
        Obtener configuración de base de datos.
        
        Returns:
            Diccionario con configuración de base de datos
        """
        return self.get('database', {})
    
    def get_logging_config(self) -> Dict[str, Any]:
        """
        Obtener configuración de logging.
        
        Returns:
            Diccionario con configuración de logging
        """
        return self.get('logging', {})
    
    def get_api_config(self) -> Dict[str, Any]:
        """
        Obtener configuración de API.
        
        Returns:
            Diccionario con configuración de API
        """
        return self.get('api', {})
    
    def get_processing_config(self) -> Dict[str, Any]:
        """
        Obtener configuración de procesamiento.
        
        Returns:
            Diccionario con configuración de procesamiento
        """
        return self.get('processing', {})
    
    def get_validation_config(self) -> Dict[str, Any]:
        """
        Obtener configuración de validación.
        
        Returns:
            Diccionario con configuración de validación
        """
        return self.get('validation', {})
    
    def get_cleaning_config(self) -> Dict[str, Any]:
        """
        Obtener configuración de limpieza.
        
        Returns:
            Diccionario con configuración de limpieza
        """
        return self.get('cleaning', {})
    
    def validate_config(self) -> bool:
        """
        Validar que la configuración tenga todos los campos requeridos.
        
        Returns:
            True si la configuración es válida, False en caso contrario
        """
        required_sections = ['paths', 'database', 'logging']
        
        for section in required_sections:
            if section not in self.config:
                self.logger.error(f"Sección requerida '{section}' no encontrada en configuración")
                return False
        
        self.logger.info("Configuración validada exitosamente")
        return True
    
    def reload_config(self) -> bool:
        """
        Recargar configuración desde archivo.
        
        Returns:
            True si se recargó exitosamente, False en caso contrario
        """
        try:
            self.config = self._load_config()
            self.logger.info("Configuración recargada exitosamente")
            return True
        except Exception as e:
            self.logger.error(f"Error al recargar configuración: {e}")
            return False
    
    def __getitem__(self, key: str) -> Any:
        """Permitir acceso directo a configuración como diccionario."""
        return self.get(key)
    
    def __contains__(self, key: str) -> bool:
        """Verificar si una clave existe en la configuración."""
        return self.get(key) is not None 