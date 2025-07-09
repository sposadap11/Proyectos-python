"""
Módulo de logging personalizado para el proyecto ETL
"""

import logging
import os
from pathlib import Path
from datetime import datetime
from colorama import init, Fore, Style

# Inicializar colorama para colores en Windows
init(autoreset=True)


class ColoredFormatter(logging.Formatter):
    """Formateador personalizado con colores para los logs."""
    
    COLORS = {
        'DEBUG': Fore.CYAN,
        'INFO': Fore.GREEN,
        'WARNING': Fore.YELLOW,
        'ERROR': Fore.RED,
        'CRITICAL': Fore.MAGENTA + Style.BRIGHT
    }
    
    def format(self, record):
        # Agregar color al nivel de log
        levelname = record.levelname
        if levelname in self.COLORS:
            record.levelname = f"{self.COLORS[levelname]}{levelname}{Style.RESET_ALL}"
        
        return super().format(record)


def setup_logger(name: str = "ETL_Pipeline", level: str = "INFO") -> logging.Logger:
    """
    Configurar el logger principal del proyecto.
    
    Args:
        name: Nombre del logger
        level: Nivel de logging (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    
    Returns:
        Logger configurado
    """
    # Crear directorio de logs si no existe
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    # Crear logger
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level.upper()))
    
    # Evitar duplicar handlers
    if logger.handlers:
        return logger
    
    # Formato para archivos
    file_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Formato para consola con colores
    console_formatter = ColoredFormatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%H:%M:%S'
    )
    
    # Handler para consola
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)
    
    # Handler para archivo de info
    info_handler = logging.FileHandler(log_dir / "info.log", encoding='utf-8')
    info_handler.setLevel(logging.INFO)
    info_handler.setFormatter(file_formatter)
    logger.addHandler(info_handler)
    
    # Handler para archivo de errores
    error_handler = logging.FileHandler(log_dir / "error.log", encoding='utf-8')
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(file_formatter)
    logger.addHandler(error_handler)
    
    # Handler para archivo de debug
    debug_handler = logging.FileHandler(log_dir / "debug.log", encoding='utf-8')
    debug_handler.setLevel(logging.DEBUG)
    debug_handler.setFormatter(file_formatter)
    logger.addHandler(debug_handler)
    
    return logger


def get_logger(name: str = "ETL_Pipeline") -> logging.Logger:
    """
    Obtener un logger específico.
    
    Args:
        name: Nombre del logger (opcional)
    
    Returns:
        Logger configurado
    """
    return logging.getLogger(name)


class LoggerMixin:
    """Mixin para agregar logging a cualquier clase."""
    
    @property
    def logger(self):
        """Obtener logger para la clase."""
        return logging.getLogger(self.__class__.__name__) 