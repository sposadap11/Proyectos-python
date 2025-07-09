"""
Scraper Manager Module - Competitive Price Intelligence Platform
Gestor centralizado de todos los scrapers de competidores
"""

import asyncio
import concurrent.futures
from typing import Dict, List, Any, Optional
from datetime import datetime
import json
from pathlib import Path

from .base_scraper import BaseScraper, MockScraper
from .amazon_scraper import AmazonScraper
from .mercadolibre_scraper import MercadoLibreScraper


class ScraperManager:
    """Gestor centralizado de scrapers de competidores."""
    
    def __init__(self, config):
        """Inicializar gestor de scrapers."""
        self.config = config
        self.scrapers = {}
        self.logger = self._setup_logger()
        
        # Inicializar scrapers
        self._initialize_scrapers()
    
    def _setup_logger(self):
        """Configurar logger para el gestor."""
        import logging
        logger = logging.getLogger("scraper_manager")
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - ScraperManager - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        
        return logger
    
    def _initialize_scrapers(self):
        """Inicializar todos los scrapers configurados."""
        competitors_config = self.config.get('scraping', {}).get('competitors', {})
        
        for competitor_name, competitor_config in competitors_config.items():
            if competitor_config.get('enabled', False):
                try:
                    scraper = self._create_scraper(competitor_name, competitor_config)
                    if scraper:
                        self.scrapers[competitor_name] = scraper
                        self.logger.info(f"✅ Scraper inicializado: {competitor_name}")
                except Exception as e:
                    self.logger.error(f"❌ Error inicializando scraper {competitor_name}: {e}")
        
        # Agregar scraper de prueba si está en modo desarrollo
        if self.config.get('development', {}).get('debug_mode', False):
            self.scrapers['mock'] = MockScraper(self.config, 'mock')
            self.logger.info("🔧 Scraper de prueba agregado")
    
    def _create_scraper(self, competitor_name: str, competitor_config: Dict[str, Any]) -> Optional[BaseScraper]:
        """Crear scraper específico según el competidor."""
        scraper_map = {
            'amazon': AmazonScraper,
            'mercadolibre': MercadoLibreScraper,
            'mock': MockScraper
        }
        
        scraper_class = scraper_map.get(competitor_name)
        if scraper_class:
            return scraper_class(self.config, competitor_name)
        else:
            self.logger.warning(f"Scraper no implementado para: {competitor_name}")
            return None
    
    def scrape_all_competitors(self) -> Dict[str, List[Dict[str, Any]]]:
        """Ejecutar scraping de todos los competidores habilitados."""
        self.logger.info("🚀 Iniciando scraping de todos los competidores")
        
        results = {}
        start_time = datetime.now()
        
        # Ejecutar scrapers en paralelo
        with concurrent.futures.ThreadPoolExecutor(max_workers=len(self.scrapers)) as executor:
            future_to_competitor = {
                executor.submit(self._scrape_competitor, competitor_name): competitor_name
                for competitor_name in self.scrapers.keys()
            }
            
            for future in concurrent.futures.as_completed(future_to_competitor):
                competitor_name = future_to_competitor[future]
                try:
                    products = future.result()
                    results[competitor_name] = products
                    self.logger.info(f"✅ {competitor_name}: {len(products)} productos extraídos")
                except Exception as e:
                    self.logger.error(f"❌ Error en {competitor_name}: {e}")
                    results[competitor_name] = []
        
        # Guardar resultados consolidados
        self._save_consolidated_results(results)
        
        end_time = datetime.now()
        total_products = sum(len(products) for products in results.values())
        
        self.logger.info(f"🎯 Scraping completado: {total_products} productos totales")
        self.logger.info(f"⏱️ Tiempo total: {(end_time - start_time).total_seconds():.2f} segundos")
        
        return results
    
    def scrape_competitor(self, competitor_name: str) -> Optional[List[Dict[str, Any]]]:
        """Ejecutar scraping de un competidor específico."""
        if competitor_name not in self.scrapers:
            self.logger.error(f"Scraper no encontrado: {competitor_name}")
            return None
        
        try:
            return self._scrape_competitor(competitor_name)
        except Exception as e:
            self.logger.error(f"Error scraping {competitor_name}: {e}")
            return None
    
    def _scrape_competitor(self, competitor_name: str) -> List[Dict[str, Any]]:
        """Ejecutar scraping de un competidor específico."""
        scraper = self.scrapers[competitor_name]
        
        try:
            products = scraper.start_scraping()
            
            # Agregar metadatos
            for product in products:
                product['scraped_by'] = competitor_name
                product['scraped_at'] = datetime.now().isoformat()
            
            return products
            
        except Exception as e:
            self.logger.error(f"Error en scraper {competitor_name}: {e}")
            return []
    
    def _save_consolidated_results(self, results: Dict[str, List[Dict[str, Any]]]):
        """Guardar resultados consolidados de todos los scrapers."""
        try:
            # Crear directorio si no existe
            raw_data_dir = Path("data/raw")
            raw_data_dir.mkdir(parents=True, exist_ok=True)
            
            # Generar nombre de archivo
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"consolidated_scraping_{timestamp}.json"
            filepath = raw_data_dir / filename
            
            # Preparar datos consolidados
            consolidated_data = {
                'metadata': {
                    'timestamp': datetime.now().isoformat(),
                    'total_competitors': len(results),
                    'total_products': sum(len(products) for products in results.values()),
                    'competitors': list(results.keys())
                },
                'results': results
            }
            
            # Guardar datos
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(consolidated_data, f, ensure_ascii=False, indent=2)
            
            self.logger.info(f"📁 Resultados consolidados guardados en: {filepath}")
            
        except Exception as e:
            self.logger.error(f"Error guardando resultados consolidados: {e}")
    
    def get_scraper_status(self, competitor_name: str) -> Optional[Dict[str, Any]]:
        """Obtener estado de un scraper específico."""
        if competitor_name not in self.scrapers:
            return None
        
        return self.scrapers[competitor_name].get_status()
    
    def get_all_scrapers_status(self) -> Dict[str, Dict[str, Any]]:
        """Obtener estado de todos los scrapers."""
        return {
            competitor_name: scraper.get_status()
            for competitor_name, scraper in self.scrapers.items()
        }
    
    def enable_scraper(self, competitor_name: str) -> bool:
        """Habilitar un scraper específico."""
        if competitor_name in self.scrapers:
            self.logger.info(f"Scraper {competitor_name} ya está habilitado")
            return True
        
        competitors_config = self.config.get('scraping', {}).get('competitors', {})
        competitor_config = competitors_config.get(competitor_name, {})
        
        if not competitor_config:
            self.logger.error(f"Configuración no encontrada para: {competitor_name}")
            return False
        
        try:
            scraper = self._create_scraper(competitor_name, competitor_config)
            if scraper:
                self.scrapers[competitor_name] = scraper
                self.logger.info(f"✅ Scraper habilitado: {competitor_name}")
                return True
            else:
                return False
        except Exception as e:
            self.logger.error(f"Error habilitando scraper {competitor_name}: {e}")
            return False
    
    def disable_scraper(self, competitor_name: str) -> bool:
        """Deshabilitar un scraper específico."""
        if competitor_name not in self.scrapers:
            self.logger.warning(f"Scraper {competitor_name} no está habilitado")
            return False
        
        try:
            # Limpiar recursos del scraper
            self.scrapers[competitor_name]._cleanup()
            del self.scrapers[competitor_name]
            
            self.logger.info(f"✅ Scraper deshabilitado: {competitor_name}")
            return True
        except Exception as e:
            self.logger.error(f"Error deshabilitando scraper {competitor_name}: {e}")
            return False
    
    def reload_scrapers(self):
        """Recargar todos los scrapers desde la configuración."""
        self.logger.info("🔄 Recargando scrapers")
        
        # Limpiar scrapers existentes
        for scraper in self.scrapers.values():
            try:
                scraper._cleanup()
            except:
                pass
        
        self.scrapers.clear()
        
        # Reinicializar scrapers
        self._initialize_scrapers()
        
        self.logger.info(f"✅ Scrapers recargados: {len(self.scrapers)} activos")
    
    def get_available_competitors(self) -> List[str]:
        """Obtener lista de competidores disponibles."""
        return list(self.scrapers.keys())
    
    def get_enabled_competitors(self) -> List[str]:
        """Obtener lista de competidores habilitados."""
        return [
            name for name, scraper in self.scrapers.items()
            if name != 'mock'  # Excluir scraper de prueba
        ]
    
    def validate_scraper_config(self, competitor_name: str) -> bool:
        """Validar configuración de un scraper."""
        competitors_config = self.config.get('scraping', {}).get('competitors', {})
        competitor_config = competitors_config.get(competitor_name, {})
        
        required_fields = ['base_url', 'categories', 'max_pages', 'products_per_page']
        
        for field in required_fields:
            if field not in competitor_config:
                self.logger.error(f"Campo requerido faltante en {competitor_name}: {field}")
                return False
        
        return True
    
    def run_test_scraping(self, competitor_name: str = None) -> Dict[str, Any]:
        """Ejecutar scraping de prueba."""
        if competitor_name:
            # Prueba de un competidor específico
            if competitor_name not in self.scrapers:
                return {'error': f'Scraper no encontrado: {competitor_name}'}
            
            products = self.scrape_competitor(competitor_name)
            return {
                'competitor': competitor_name,
                'products_count': len(products) if products else 0,
                'success': products is not None
            }
        else:
            # Prueba de todos los competidores
            results = self.scrape_all_competitors()
            return {
                'total_competitors': len(results),
                'total_products': sum(len(products) for products in results.values()),
                'results': {
                    name: len(products) for name, products in results.items()
                }
            }
    
    def get_scraping_metrics(self) -> Dict[str, Any]:
        """Obtener métricas de scraping."""
        metrics = {
            'total_scrapers': len(self.scrapers),
            'enabled_scrapers': len(self.get_enabled_competitors()),
            'scrapers_status': self.get_all_scrapers_status(),
            'last_scraping': self._get_last_scraping_info()
        }
        
        return metrics
    
    def _get_last_scraping_info(self) -> Dict[str, Any]:
        """Obtener información del último scraping."""
        try:
            # Buscar archivo de scraping más reciente
            raw_data_dir = Path("data/raw")
            if not raw_data_dir.exists():
                return {'status': 'No scraping data found'}
            
            json_files = list(raw_data_dir.glob("consolidated_scraping_*.json"))
            if not json_files:
                return {'status': 'No consolidated scraping data found'}
            
            # Obtener archivo más reciente
            latest_file = max(json_files, key=lambda x: x.stat().st_mtime)
            
            with open(latest_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            return {
                'file': str(latest_file),
                'timestamp': data.get('metadata', {}).get('timestamp'),
                'total_products': data.get('metadata', {}).get('total_products', 0),
                'competitors': data.get('metadata', {}).get('competitors', [])
            }
            
        except Exception as e:
            return {'error': str(e)} 