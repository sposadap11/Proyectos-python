"""
Base Scraper Module - Competitive Price Intelligence Platform
Clase base para todos los scrapers de competidores
"""

import time
import random
import requests
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional, Union
from datetime import datetime
from pathlib import Path
import json
import logging
from fake_useragent import UserAgent
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
import undetected_chromedriver as uc


class BaseScraper(ABC):
    """Clase base para todos los scrapers de competidores."""
    
    def __init__(self, config: Dict[str, Any], competitor_name: str):
        """Inicializar scraper base."""
        self.config = config
        self.competitor_name = competitor_name
        self.competitor_config = config.get('scraping', {}).get('competitors', {}).get(competitor_name, {})
        
        # Configuración de scraping
        self.delay = config.get('scraping', {}).get('delay', 2)
        self.timeout = config.get('scraping', {}).get('timeout', 30)
        self.retries = config.get('scraping', {}).get('retries', 3)
        self.user_agent_rotation = config.get('scraping', {}).get('user_agent_rotation', True)
        self.use_proxies = config.get('scraping', {}).get('use_proxies', False)
        self.respect_robots_txt = config.get('scraping', {}).get('respect_robots_txt', True)
        
        # Configuración específica del competidor
        self.base_url = self.competitor_config.get('base_url', '')
        self.categories = self.competitor_config.get('categories', [])
        self.max_pages = self.competitor_config.get('max_pages', 10)
        self.products_per_page = self.competitor_config.get('products_per_page', 50)
        
        # Inicializar componentes
        self.session = None
        self.driver = None
        self.user_agent = UserAgent()
        self.logger = self._setup_logger()
        
        # Estadísticas
        self.stats = {
            'start_time': None,
            'end_time': None,
            'products_scraped': 0,
            'pages_scraped': 0,
            'errors': 0,
            'success_rate': 0.0
        }
    
    def _setup_logger(self) -> logging.Logger:
        """Configurar logger específico para el scraper."""
        logger = logging.getLogger(f"scraper.{self.competitor_name}")
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                f'%(asctime)s - {self.competitor_name} - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        
        return logger
    
    def _get_user_agent(self) -> str:
        """Obtener User-Agent aleatorio."""
        if self.user_agent_rotation:
            return self.user_agent.random
        else:
            return self.user_agent.chrome
    
    def _setup_session(self) -> requests.Session:
        """Configurar sesión de requests."""
        session = requests.Session()
        
        # Configurar headers
        session.headers.update({
            'User-Agent': self._get_user_agent(),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
        
        # Configurar proxies si están habilitados
        if self.use_proxies:
            # Aquí se configurarían los proxies
            pass
        
        return session
    
    def _setup_selenium_driver(self, headless: bool = True) -> webdriver.Chrome:
        """Configurar driver de Selenium."""
        try:
            # Usar undetected-chromedriver para evitar detección
            options = uc.ChromeOptions()
            
            if headless:
                options.add_argument('--headless')
            
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--disable-gpu')
            options.add_argument('--window-size=1920,1080')
            options.add_argument('--user-agent=' + self._get_user_agent())
            options.add_argument('--disable-blink-features=AutomationControlled')
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            options.add_experimental_option('useAutomationExtension', False)
            
            driver = uc.Chrome(options=options)
            driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            return driver
            
        except Exception as e:
            self.logger.error(f"Error configurando Selenium driver: {e}")
            # Fallback a driver estándar
            options = Options()
            if headless:
                options.add_argument('--headless')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--user-agent=' + self._get_user_agent())
            
            return webdriver.Chrome(options=options)
    
    def _respect_robots_txt(self, url: str) -> bool:
        """Verificar robots.txt si está habilitado."""
        if not self.respect_robots_txt:
            return True
        
        try:
            robots_url = f"{self.base_url}/robots.txt"
            response = self.session.get(robots_url, timeout=self.timeout)
            
            if response.status_code == 200:
                robots_content = response.text
                # Aquí se implementaría la lógica para verificar robots.txt
                # Por simplicidad, asumimos que está permitido
                return True
            
            return True
            
        except Exception as e:
            self.logger.warning(f"Error verificando robots.txt: {e}")
            return True
    
    def _make_request(self, url: str, method: str = 'GET', **kwargs) -> Optional[requests.Response]:
        """Realizar request con manejo de errores y reintentos."""
        for attempt in range(self.retries):
            try:
                # Verificar robots.txt
                if not self._respect_robots_txt(url):
                    self.logger.warning(f"URL no permitida por robots.txt: {url}")
                    return None
                
                # Realizar request
                if method.upper() == 'GET':
                    response = self.session.get(url, timeout=self.timeout, **kwargs)
                elif method.upper() == 'POST':
                    response = self.session.post(url, timeout=self.timeout, **kwargs)
                else:
                    raise ValueError(f"Método HTTP no soportado: {method}")
                
                # Verificar respuesta
                response.raise_for_status()
                
                # Delay aleatorio
                time.sleep(random.uniform(self.delay * 0.5, self.delay * 1.5))
                
                return response
                
            except requests.exceptions.RequestException as e:
                self.logger.warning(f"Intento {attempt + 1} fallido para {url}: {e}")
                self.stats['errors'] += 1
                
                if attempt < self.retries - 1:
                    # Esperar antes del siguiente intento
                    time.sleep(random.uniform(2, 5))
                else:
                    self.logger.error(f"Todos los intentos fallaron para {url}")
                    return None
        
        return None
    
    def _extract_with_selenium(self, url: str, selectors: Dict[str, str]) -> Dict[str, Any]:
        """Extraer datos usando Selenium."""
        if not self.driver:
            self.driver = self._setup_selenium_driver()
        
        try:
            self.driver.get(url)
            
            # Esperar a que la página cargue
            WebDriverWait(self.driver, self.timeout).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            # Extraer datos según selectores
            extracted_data = {}
            for key, selector in selectors.items():
                try:
                    if selector.startswith('css:'):
                        css_selector = selector[4:]
                        elements = self.driver.find_elements(By.CSS_SELECTOR, css_selector)
                    elif selector.startswith('xpath:'):
                        xpath_selector = selector[6:]
                        elements = self.driver.find_elements(By.XPATH, xpath_selector)
                    else:
                        # Por defecto usar CSS selector
                        elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    
                    if elements:
                        if len(elements) == 1:
                            extracted_data[key] = elements[0].text.strip()
                        else:
                            extracted_data[key] = [elem.text.strip() for elem in elements]
                    else:
                        extracted_data[key] = None
                        
                except Exception as e:
                    self.logger.warning(f"Error extrayendo {key}: {e}")
                    extracted_data[key] = None
            
            return extracted_data
            
        except TimeoutException:
            self.logger.error(f"Timeout esperando página: {url}")
            return {}
        except WebDriverException as e:
            self.logger.error(f"Error de WebDriver: {e}")
            return {}
        except Exception as e:
            self.logger.error(f"Error inesperado en Selenium: {e}")
            return {}
    
    def _clean_text(self, text: str) -> str:
        """Limpiar texto extraído."""
        if not text:
            return ""
        
        # Remover espacios extra y caracteres especiales
        text = text.strip()
        text = ' '.join(text.split())  # Normalizar espacios
        
        return text
    
    def _extract_price(self, price_text: str) -> Optional[float]:
        """Extraer precio numérico de texto."""
        if not price_text:
            return None
        
        try:
            # Remover símbolos de moneda y caracteres no numéricos
            import re
            price_match = re.search(r'[\d,]+\.?\d*', price_text.replace(',', ''))
            
            if price_match:
                price_str = price_match.group()
                return float(price_str)
            
            return None
            
        except (ValueError, AttributeError):
            return None
    
    def _save_raw_data(self, data: List[Dict[str, Any]], category: str):
        """Guardar datos raw en archivo."""
        try:
            # Crear directorio si no existe
            raw_data_dir = Path("data/raw")
            raw_data_dir.mkdir(parents=True, exist_ok=True)
            
            # Generar nombre de archivo
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{self.competitor_name}_{category}_{timestamp}.json"
            filepath = raw_data_dir / filename
            
            # Guardar datos
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            self.logger.info(f"Datos guardados en: {filepath}")
            
        except Exception as e:
            self.logger.error(f"Error guardando datos raw: {e}")
    
    def start_scraping(self):
        """Iniciar proceso de scraping."""
        self.stats['start_time'] = datetime.now()
        self.logger.info(f"🚀 Iniciando scraping de {self.competitor_name}")
        
        try:
            # Configurar sesión
            self.session = self._setup_session()
            
            # Scraping por categoría
            all_products = []
            
            for category in self.categories:
                self.logger.info(f"📂 Procesando categoría: {category}")
                category_products = self._scrape_category(category)
                all_products.extend(category_products)
                
                # Guardar datos de la categoría
                if category_products:
                    self._save_raw_data(category_products, category)
            
            # Finalizar estadísticas
            self.stats['end_time'] = datetime.now()
            self.stats['products_scraped'] = len(all_products)
            
            if self.stats['products_scraped'] > 0:
                self.stats['success_rate'] = (
                    (self.stats['products_scraped'] - self.stats['errors']) / 
                    self.stats['products_scraped']
                ) * 100
            
            self.logger.info(f"✅ Scraping completado: {self.stats['products_scraped']} productos")
            self.logger.info(f"📊 Estadísticas: {self.stats}")
            
            return all_products
            
        except Exception as e:
            self.logger.error(f"❌ Error en scraping: {e}")
            return []
        
        finally:
            # Limpiar recursos
            self._cleanup()
    
    def _cleanup(self):
        """Limpiar recursos utilizados."""
        if self.session:
            self.session.close()
        
        if self.driver:
            try:
                self.driver.quit()
            except:
                pass
    
    @abstractmethod
    def _scrape_category(self, category: str) -> List[Dict[str, Any]]:
        """Scraping específico de una categoría. Debe ser implementado por subclases."""
        pass
    
    @abstractmethod
    def _extract_product_data(self, product_element: Any) -> Dict[str, Any]:
        """Extraer datos de un producto específico. Debe ser implementado por subclases."""
        pass
    
    def get_status(self) -> Dict[str, Any]:
        """Obtener estado del scraper."""
        return {
            'competitor': self.competitor_name,
            'status': 'active' if self.session else 'inactive',
            'stats': self.stats.copy(),
            'config': {
                'base_url': self.base_url,
                'categories': self.categories,
                'max_pages': self.max_pages,
                'products_per_page': self.products_per_page
            }
        }


class MockScraper(BaseScraper):
    """Scraper de prueba para desarrollo y testing."""
    
    def __init__(self, config: Dict[str, Any], competitor_name: str = "mock"):
        """Inicializar scraper de prueba."""
        super().__init__(config, competitor_name)
    
    def _scrape_category(self, category: str) -> List[Dict[str, Any]]:
        """Generar datos de prueba para una categoría."""
        self.logger.info(f"🔧 Generando datos de prueba para categoría: {category}")
        
        products = []
        for i in range(random.randint(10, 50)):
            product = {
                'id': f"mock_{category}_{i}",
                'name': f"Producto de prueba {i} - {category}",
                'price': round(random.uniform(10.0, 1000.0), 2),
                'original_price': round(random.uniform(15.0, 1200.0), 2),
                'currency': 'USD',
                'category': category,
                'brand': f"Brand {random.randint(1, 10)}",
                'rating': round(random.uniform(1.0, 5.0), 1),
                'reviews_count': random.randint(0, 1000),
                'availability': random.choice([True, False]),
                'url': f"https://mock.com/product/{i}",
                'image_url': f"https://mock.com/images/product_{i}.jpg",
                'scraped_at': datetime.now().isoformat(),
                'competitor': self.competitor_name
            }
            products.append(product)
        
        return products
    
    def _extract_product_data(self, product_element: Any) -> Dict[str, Any]:
        """Extraer datos de producto (no usado en mock)."""
        return {} 