"""
Competitive Price Intelligence Platform - Source Package
Módulo principal del sistema de inteligencia de precios competitivos
"""

__version__ = "1.0.0"
__author__ = "Senior Data Engineer"
__description__ = "Sistema completo de scraping, procesamiento y análisis de precios de competencia"

# Importar componentes principales para facilitar el acceso
try:
    from .utils.logger import setup_logger
    from .utils.config_loader import ConfigLoader
    from .scrapers.scraper_manager import ScraperManager
    from .transformers.data_transformer import DataTransformer
    from .loaders.data_loader import DataLoader
    from .analytics.price_analyzer import PriceAnalyzer
    from .utils.report_generator import ReportGenerator
    from .orchestration.workflow_manager import WorkflowManager
except ImportError:
    # Los módulos pueden no estar disponibles durante el desarrollo
    pass

__all__ = [
    'setup_logger',
    'ConfigLoader',
    'ScraperManager',
    'DataTransformer',
    'DataLoader',
    'PriceAnalyzer',
    'ReportGenerator',
    'WorkflowManager'
] 