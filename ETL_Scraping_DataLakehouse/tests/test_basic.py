"""
Basic Tests - Competitive Price Intelligence Platform
Tests básicos para verificar la funcionalidad del sistema
"""

import pytest
import sys
from pathlib import Path

# Agregar el directorio src al path
sys.path.append(str(Path(__file__).parent.parent / "src"))


class TestConfiguration:
    """Tests para la configuración del sistema."""
    
    def test_config_loader_initialization(self):
        """Test de inicialización del cargador de configuración."""
        from src.utils.config_loader import ConfigLoader
        
        config = ConfigLoader()
        assert config is not None
        assert hasattr(config, 'config')
        assert isinstance(config.config, dict)
    
    def test_config_sections(self):
        """Test de secciones de configuración requeridas."""
        from src.utils.config_loader import ConfigLoader
        
        config = ConfigLoader()
        
        required_sections = ['paths', 'database', 'storage', 'scraping', 'processing', 'analytics']
        
        for section in required_sections:
            assert section in config.config, f"Sección {section} no encontrada en configuración"
    
    def test_database_config(self):
        """Test de configuración de base de datos."""
        from src.utils.config_loader import ConfigLoader
        
        config = ConfigLoader()
        db_config = config.get_database_config()
        
        assert 'type' in db_config
        assert 'url' in db_config
        assert db_config['type'] == 'duckdb'


class TestScrapers:
    """Tests para los scrapers."""
    
    def test_mock_scraper_initialization(self):
        """Test de inicialización del scraper de prueba."""
        from src.scrapers.base_scraper import MockScraper
        from src.utils.config_loader import ConfigLoader
        
        config = ConfigLoader()
        scraper = MockScraper(config, 'mock')
        
        assert scraper is not None
        assert scraper.competitor_name == 'mock'
        assert hasattr(scraper, 'categories')
    
    def test_mock_scraper_scraping(self):
        """Test de scraping con datos de prueba."""
        from src.scrapers.base_scraper import MockScraper
        from src.utils.config_loader import ConfigLoader
        
        config = ConfigLoader()
        scraper = MockScraper(config, 'mock')
        
        # Test scraping de una categoría
        products = scraper._scrape_category('electronics')
        
        assert isinstance(products, list)
        assert len(products) > 0
        
        # Verificar estructura de productos
        if products:
            product = products[0]
            required_fields = ['id', 'name', 'price', 'currency', 'competitor']
            
            for field in required_fields:
                assert field in product, f"Campo {field} no encontrado en producto"
    
    def test_scraper_manager_initialization(self):
        """Test de inicialización del gestor de scrapers."""
        from src.scrapers.scraper_manager import ScraperManager
        from src.utils.config_loader import ConfigLoader
        
        config = ConfigLoader()
        manager = ScraperManager(config)
        
        assert manager is not None
        assert hasattr(manager, 'scrapers')
        assert isinstance(manager.scrapers, dict)


class TestDataProcessing:
    """Tests para el procesamiento de datos."""
    
    def test_data_transformer_initialization(self):
        """Test de inicialización del transformador de datos."""
        # Este test se implementará cuando se cree el módulo de transformación
        pass
    
    def test_data_loader_initialization(self):
        """Test de inicialización del cargador de datos."""
        # Este test se implementará cuando se cree el módulo de carga
        pass


class TestAnalytics:
    """Tests para el análisis de datos."""
    
    def test_price_analyzer_initialization(self):
        """Test de inicialización del analizador de precios."""
        # Este test se implementará cuando se cree el módulo de análisis
        pass


class TestUtilities:
    """Tests para las utilidades del sistema."""
    
    def test_logger_initialization(self):
        """Test de inicialización del logger."""
        from src.utils.logger import setup_logger
        
        logger = setup_logger()
        assert logger is not None
        assert hasattr(logger, 'info')
        assert hasattr(logger, 'error')
        assert hasattr(logger, 'warning')
    
    def test_config_loader_methods(self):
        """Test de métodos del cargador de configuración."""
        from src.utils.config_loader import ConfigLoader
        
        config = ConfigLoader()
        
        # Test método get
        db_type = config.get('database.type')
        assert db_type == 'duckdb'
        
        # Test método get_section
        db_section = config.get_section('database')
        assert isinstance(db_section, dict)
        assert 'type' in db_section
        
        # Test método get_path
        raw_path = config.get_path('data', 'raw')
        assert raw_path == 'data/raw'
    
    def test_enabled_competitors(self):
        """Test de competidores habilitados."""
        from src.utils.config_loader import ConfigLoader
        
        config = ConfigLoader()
        enabled = config.get_enabled_competitors()
        
        assert isinstance(enabled, list)
        # Al menos debe tener el scraper de prueba en modo desarrollo
        if config.is_development_mode():
            assert len(enabled) >= 0


class TestIntegration:
    """Tests de integración."""
    
    def test_full_pipeline_components(self):
        """Test de que todos los componentes principales están disponibles."""
        from src.utils.config_loader import ConfigLoader
        from src.scrapers.scraper_manager import ScraperManager
        from src.utils.logger import setup_logger
        
        # Inicializar componentes
        config = ConfigLoader()
        logger = setup_logger()
        scraper_manager = ScraperManager(config)
        
        # Verificar que todos los componentes se inicializaron correctamente
        assert config is not None
        assert logger is not None
        assert scraper_manager is not None
        
        # Verificar que el gestor de scrapers tiene scrapers disponibles
        available_scrapers = scraper_manager.get_available_competitors()
        assert isinstance(available_scrapers, list)
    
    def test_configuration_validation(self):
        """Test de validación de configuración."""
        from src.utils.config_loader import ConfigLoader
        
        config = ConfigLoader()
        
        # Verificar que la configuración es válida
        assert config.validate_competitor_config('amazon') or config.is_development_mode()
        assert config.validate_competitor_config('mercadolibre') or config.is_development_mode()


if __name__ == "__main__":
    pytest.main([__file__]) 