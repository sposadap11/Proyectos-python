"""
Logger Module - Competitive Price Intelligence Platform
Sistema de logging centralizado y estructurado
"""

import logging
import logging.handlers
import json
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional
import structlog
from colorama import Fore, Style, init

# Inicializar colorama para colores en terminal
init(autoreset=True)


class StructuredLogger:
    """Logger estructurado con soporte para JSON y colores."""
    
    def __init__(self, name: str, config: Dict[str, Any]):
        """Inicializar logger estructurado."""
        self.name = name
        self.config = config
        self.logger = self._setup_logger()
    
    def _setup_logger(self) -> structlog.BoundLogger:
        """Configurar logger con procesadores estructurados."""
        # Configurar procesadores
        processors = [
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
        ]
        
        # Agregar procesador JSON si está configurado
        if self.config.get('format') == 'json':
            processors.append(structlog.processors.JSONRenderer())
        else:
            processors.append(structlog.dev.ConsoleRenderer(colors=True))
        
        # Configurar structlog
        structlog.configure(
            processors=processors,
            context_class=dict,
            logger_factory=structlog.stdlib.LoggerFactory(),
            wrapper_class=structlog.stdlib.BoundLogger,
            cache_logger_on_first_use=True,
        )
        
        return structlog.get_logger(self.name)
    
    def info(self, message: str, **kwargs):
        """Log de información."""
        self.logger.info(message, **kwargs)
    
    def error(self, message: str, **kwargs):
        """Log de error."""
        self.logger.error(message, **kwargs)
    
    def warning(self, message: str, **kwargs):
        """Log de advertencia."""
        self.logger.warning(message, **kwargs)
    
    def debug(self, message: str, **kwargs):
        """Log de debug."""
        self.logger.debug(message, **kwargs)
    
    def critical(self, message: str, **kwargs):
        """Log crítico."""
        self.logger.critical(message, **kwargs)


class ColoredConsoleHandler(logging.StreamHandler):
    """Handler de consola con colores."""
    
    COLORS = {
        'DEBUG': Fore.BLUE,
        'INFO': Fore.GREEN,
        'WARNING': Fore.YELLOW,
        'ERROR': Fore.RED,
        'CRITICAL': Fore.MAGENTA + Style.BRIGHT,
    }
    
    def emit(self, record):
        """Emitir log con colores."""
        try:
            # Agregar color al mensaje
            color = self.COLORS.get(record.levelname, '')
            record.msg = f"{color}{record.msg}{Style.RESET_ALL}"
            
            # Agregar emoji según el nivel
            emoji = self._get_emoji(record.levelname)
            if emoji:
                record.msg = f"{emoji} {record.msg}"
            
            super().emit(record)
        except Exception:
            self.handleError(record)
    
    def _get_emoji(self, levelname: str) -> str:
        """Obtener emoji según el nivel de log."""
        emojis = {
            'DEBUG': '🔍',
            'INFO': 'ℹ️',
            'WARNING': '⚠️',
            'ERROR': '❌',
            'CRITICAL': '🚨',
        }
        return emojis.get(levelname, '')


class JsonFileHandler(logging.handlers.RotatingFileHandler):
    """Handler de archivo con formato JSON."""
    
    def __init__(self, filename: str, max_bytes: int = 10485760, backup_count: int = 5):
        """Inicializar handler de archivo JSON."""
        super().__init__(filename, maxBytes=max_bytes, backupCount=backup_count)
        self.setFormatter(logging.Formatter('%(message)s'))
    
    def emit(self, record):
        """Emitir log en formato JSON."""
        try:
            # Crear estructura JSON
            log_entry = {
                'timestamp': datetime.fromtimestamp(record.created).isoformat(),
                'level': record.levelname,
                'logger': record.name,
                'message': record.getMessage(),
                'module': record.module,
                'function': record.funcName,
                'line': record.lineno,
            }
            
            # Agregar excepción si existe
            if record.exc_info:
                log_entry['exception'] = self.formatException(record.exc_info)
            
            # Agregar campos extra si existen
            if hasattr(record, 'extra_fields'):
                log_entry.update(record.extra_fields)
            
            # Escribir JSON
            self.stream.write(json.dumps(log_entry) + '\n')
            self.flush()
            
        except Exception:
            self.handleError(record)


def setup_logger(name: str = "competitive_pricing", config: Optional[Dict[str, Any]] = None) -> StructuredLogger:
    """Configurar logger principal del sistema."""
    
    # Configuración por defecto
    default_config = {
        'level': 'INFO',
        'format': 'json',
        'file': 'logs/app.log',
        'max_size': '100MB',
        'backup_count': 5,
        'console_output': True,
        'file_output': True,
    }
    
    # Combinar con configuración proporcionada
    if config:
        default_config.update(config)
    
    # Crear directorio de logs si no existe
    log_file = Path(default_config['file'])
    log_file.parent.mkdir(parents=True, exist_ok=True)
    
    # Configurar logger estándar
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, default_config['level'].upper()))
    
    # Limpiar handlers existentes
    logger.handlers.clear()
    
    # Handler de consola
    if default_config.get('console_output', True):
        console_handler = ColoredConsoleHandler(sys.stdout)
        console_handler.setLevel(getattr(logging, default_config['level'].upper()))
        logger.addHandler(console_handler)
    
    # Handler de archivo
    if default_config.get('file_output', True):
        # Convertir tamaño máximo a bytes
        max_size_str = default_config['max_size']
        if isinstance(max_size_str, str):
            if 'MB' in max_size_str:
                max_bytes = int(max_size_str.replace('MB', '')) * 1024 * 1024
            elif 'GB' in max_size_str:
                max_bytes = int(max_size_str.replace('GB', '')) * 1024 * 1024 * 1024
            else:
                max_bytes = int(max_size_str)
        else:
            max_bytes = max_size_str
        
        file_handler = JsonFileHandler(
            filename=default_config['file'],
            max_bytes=max_bytes,
            backup_count=default_config['backup_count']
        )
        file_handler.setLevel(getattr(logging, default_config['level'].upper()))
        logger.addHandler(file_handler)
    
    # Crear logger estructurado
    structured_logger = StructuredLogger(name, default_config)
    
    # Log inicial
    structured_logger.info(
        "🚀 Logger inicializado",
        logger_name=name,
        config=default_config,
        timestamp=datetime.now().isoformat()
    )
    
    return structured_logger


def get_module_logger(module_name: str, config: Optional[Dict[str, Any]] = None) -> StructuredLogger:
    """Obtener logger específico para un módulo."""
    module_config = config or {}
    
    # Obtener configuración específica del módulo
    if 'modules' in module_config:
        module_level = module_config['modules'].get(module_name, 'INFO')
        module_config['level'] = module_level
    
    return setup_logger(f"competitive_pricing.{module_name}", module_config)


class PerformanceLogger:
    """Logger especializado para métricas de rendimiento."""
    
    def __init__(self, logger: StructuredLogger):
        """Inicializar logger de rendimiento."""
        self.logger = logger
        self.metrics = {}
    
    def start_timer(self, operation: str):
        """Iniciar timer para una operación."""
        self.metrics[operation] = {
            'start_time': datetime.now(),
            'status': 'running'
        }
    
    def end_timer(self, operation: str, success: bool = True, extra_data: Optional[Dict[str, Any]] = None):
        """Finalizar timer y registrar métrica."""
        if operation not in self.metrics:
            self.logger.warning(f"Timer no encontrado para operación: {operation}")
            return
        
        start_time = self.metrics[operation]['start_time']
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        metric_data = {
            'operation': operation,
            'duration_seconds': duration,
            'success': success,
            'start_time': start_time.isoformat(),
            'end_time': end_time.isoformat(),
        }
        
        if extra_data:
            metric_data.update(extra_data)
        
        if success:
            self.logger.info(
                f"⏱️ Operación completada: {operation}",
                **metric_data
            )
        else:
            self.logger.error(
                f"⏱️ Operación fallida: {operation}",
                **metric_data
            )
        
        # Limpiar métrica
        del self.metrics[operation]


class DataQualityLogger:
    """Logger especializado para calidad de datos."""
    
    def __init__(self, logger: StructuredLogger):
        """Inicializar logger de calidad de datos."""
        self.logger = logger
    
    def log_data_quality_check(self, check_name: str, result: Dict[str, Any]):
        """Registrar resultado de verificación de calidad."""
        self.logger.info(
            f"🔍 Verificación de calidad: {check_name}",
            check_name=check_name,
            **result
        )
    
    def log_data_issue(self, issue_type: str, details: Dict[str, Any]):
        """Registrar problema de calidad de datos."""
        self.logger.warning(
            f"⚠️ Problema de calidad de datos: {issue_type}",
            issue_type=issue_type,
            **details
        )
    
    def log_data_validation(self, validation_name: str, passed: bool, details: Dict[str, Any]):
        """Registrar validación de datos."""
        if passed:
            self.logger.info(
                f"✅ Validación exitosa: {validation_name}",
                validation_name=validation_name,
                **details
            )
        else:
            self.logger.error(
                f"❌ Validación fallida: {validation_name}",
                validation_name=validation_name,
                **details
            )


# Función de conveniencia para obtener logger principal
def get_logger() -> StructuredLogger:
    """Obtener logger principal del sistema."""
    return setup_logger()


# Función para configurar logging desde archivo de configuración
def setup_logging_from_config(config_path: str = "config/config.yaml") -> StructuredLogger:
    """Configurar logging desde archivo de configuración."""
    try:
        import yaml
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        
        logging_config = config.get('logging', {})
        return setup_logger(config=logging_config)
        
    except Exception as e:
        # Fallback a configuración por defecto
        print(f"Error cargando configuración de logging: {e}")
        return setup_logger() 