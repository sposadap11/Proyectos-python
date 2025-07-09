"""
Amazon Scraper Module - Competitive Price Intelligence Platform
Scraper específico para Amazon
"""

import re
from typing import Dict, List, Any, Optional
from datetime import datetime
from urllib.parse import urljoin, urlparse, parse_qs

from .base_scraper import BaseScraper


class AmazonScraper(BaseScraper):
    """Scraper específico para Amazon."""
    
    def __init__(self, config: Dict[str, Any], competitor_name: str = "amazon"):
        """Inicializar scraper de Amazon."""
        super().__init__(config, competitor_name)
        
        # Configuración específica de Amazon
        self.selectors = {
            'product_container': 'div[data-component-type="s-search-result"]',
            'product_title': 'h2 a span',
            'product_price': 'span.a-price-whole, span.a-price-fraction',
            'product_original_price': 'span.a-text-strike',
            'product_rating': 'span[aria-label*="stars"]',
            'product_reviews': 'span[aria-label*="reviews"]',
            'product_image': 'img.s-image',
            'product_url': 'h2 a',
            'product_availability': 'span.a-color-success',
            'product_brand': 'span.a-size-base-plus',
            'product_category': 'span.a-size-base',
            'next_page': 'a.s-pagination-next'
        }
        
        # Headers específicos para Amazon
        self.session_headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Cache-Control': 'max-age=0'
        }
    
    def _scrape_category(self, category: str) -> List[Dict[str, Any]]:
        """Scraping específico de una categoría en Amazon."""
        self.logger.info(f"📂 Scraping categoría Amazon: {category}")
        
        all_products = []
        page = 1
        
        while page <= self.max_pages:
            try:
                # Construir URL de búsqueda
                search_url = self._build_search_url(category, page)
                self.logger.info(f"🔍 Página {page}: {search_url}")
                
                # Realizar request
                response = self._make_request(search_url)
                if not response:
                    self.logger.warning(f"Error obteniendo página {page}")
                    break
                
                # Extraer productos de la página
                products = self._extract_products_from_page(response.text)
                
                if not products:
                    self.logger.info(f"No se encontraron productos en página {page}")
                    break
                
                all_products.extend(products)
                self.logger.info(f"✅ Página {page}: {len(products)} productos extraídos")
                
                # Verificar si hay siguiente página
                if not self._has_next_page(response.text):
                    self.logger.info("Última página alcanzada")
                    break
                
                page += 1
                
            except Exception as e:
                self.logger.error(f"Error en página {page}: {e}")
                break
        
        self.logger.info(f"🎯 Categoría {category}: {len(all_products)} productos totales")
        return all_products
    
    def _build_search_url(self, category: str, page: int) -> str:
        """Construir URL de búsqueda para Amazon."""
        # Mapeo de categorías a departamentos de Amazon
        category_mapping = {
            'electronics': 'electronics',
            'books': 'books',
            'home': 'home-garden',
            'computacion': 'computers',
            'libros': 'books',
            'hogar': 'home-garden'
        }
        
        mapped_category = category_mapping.get(category, category)
        
        # Construir URL base
        base_url = f"{self.base_url}/s"
        
        # Parámetros de búsqueda
        params = {
            'k': category,
            'ref': 'sr_pg_' + str(page),
            'page': str(page)
        }
        
        # Agregar departamento si está mapeado
        if mapped_category != category:
            params['i'] = mapped_category
        
        # Construir URL completa
        query_string = '&'.join([f"{k}={v}" for k, v in params.items()])
        return f"{base_url}?{query_string}"
    
    def _extract_products_from_page(self, html_content: str) -> List[Dict[str, Any]]:
        """Extraer productos de una página HTML."""
        from bs4 import BeautifulSoup
        
        products = []
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Encontrar contenedores de productos
        product_containers = soup.select(self.selectors['product_container'])
        
        for container in product_containers:
            try:
                product_data = self._extract_product_data(container)
                if product_data:
                    products.append(product_data)
            except Exception as e:
                self.logger.warning(f"Error extrayendo producto: {e}")
                continue
        
        return products
    
    def _extract_product_data(self, product_element) -> Optional[Dict[str, Any]]:
        """Extraer datos de un producto específico de Amazon."""
        try:
            # Extraer título
            title_elem = product_element.select_one(self.selectors['product_title'])
            title = self._clean_text(title_elem.get_text()) if title_elem else ""
            
            if not title:
                return None
            
            # Extraer precio
            price_elem = product_element.select_one(self.selectors['product_price'])
            price = self._extract_price(price_elem.get_text()) if price_elem else None
            
            # Extraer precio original
            original_price_elem = product_element.select_one(self.selectors['product_original_price'])
            original_price = self._extract_price(original_price_elem.get_text()) if original_price_elem else None
            
            # Extraer rating
            rating_elem = product_element.select_one(self.selectors['product_rating'])
            rating = self._extract_rating(rating_elem.get('aria-label')) if rating_elem else None
            
            # Extraer número de reviews
            reviews_elem = product_element.select_one(self.selectors['product_reviews'])
            reviews_count = self._extract_reviews_count(reviews_elem.get('aria-label')) if reviews_elem else 0
            
            # Extraer URL del producto
            url_elem = product_element.select_one(self.selectors['product_url'])
            product_url = urljoin(self.base_url, url_elem.get('href')) if url_elem else ""
            
            # Extraer imagen
            image_elem = product_element.select_one(self.selectors['product_image'])
            image_url = image_elem.get('src') if image_elem else ""
            
            # Extraer disponibilidad
            availability_elem = product_element.select_one(self.selectors['product_availability'])
            availability = bool(availability_elem) if availability_elem else True
            
            # Extraer marca
            brand_elem = product_element.select_one(self.selectors['product_brand'])
            brand = self._clean_text(brand_elem.get_text()) if brand_elem else ""
            
            # Extraer ASIN (Amazon Standard Identification Number)
            asin = self._extract_asin(product_url)
            
            # Construir datos del producto
            product_data = {
                'id': asin or f"amazon_{hash(title)}",
                'name': title,
                'price': price,
                'original_price': original_price,
                'currency': 'USD',
                'rating': rating,
                'reviews_count': reviews_count,
                'brand': brand,
                'url': product_url,
                'image_url': image_url,
                'availability': availability,
                'competitor': self.competitor_name,
                'scraped_at': datetime.now().isoformat(),
                'raw_data': {
                    'title': title,
                    'price_text': price_elem.get_text() if price_elem else "",
                    'original_price_text': original_price_elem.get_text() if original_price_elem else "",
                    'rating_text': rating_elem.get('aria-label') if rating_elem else "",
                    'reviews_text': reviews_elem.get('aria-label') if reviews_elem else ""
                }
            }
            
            return product_data
            
        except Exception as e:
            self.logger.warning(f"Error extrayendo datos de producto: {e}")
            return None
    
    def _extract_rating(self, rating_text: str) -> Optional[float]:
        """Extraer rating numérico del texto de Amazon."""
        if not rating_text:
            return None
        
        try:
            # Buscar patrón "X.X out of 5 stars"
            match = re.search(r'(\d+\.?\d*)\s+out\s+of\s+5', rating_text)
            if match:
                return float(match.group(1))
            
            # Buscar solo el número
            match = re.search(r'(\d+\.?\d*)', rating_text)
            if match:
                rating = float(match.group(1))
                return rating if 0 <= rating <= 5 else None
            
            return None
            
        except (ValueError, AttributeError):
            return None
    
    def _extract_reviews_count(self, reviews_text: str) -> int:
        """Extraer número de reviews del texto de Amazon."""
        if not reviews_text:
            return 0
        
        try:
            # Buscar números en el texto
            numbers = re.findall(r'[\d,]+', reviews_text)
            if numbers:
                # Tomar el primer número encontrado
                count_str = numbers[0].replace(',', '')
                return int(count_str)
            
            return 0
            
        except (ValueError, AttributeError):
            return 0
    
    def _extract_asin(self, product_url: str) -> Optional[str]:
        """Extraer ASIN de la URL del producto."""
        if not product_url:
            return None
        
        try:
            # Buscar ASIN en la URL
            match = re.search(r'/dp/([A-Z0-9]{10})', product_url)
            if match:
                return match.group(1)
            
            # Buscar en parámetros de URL
            parsed_url = urlparse(product_url)
            query_params = parse_qs(parsed_url.query)
            
            if 'asin' in query_params:
                return query_params['asin'][0]
            
            return None
            
        except Exception:
            return None
    
    def _has_next_page(self, html_content: str) -> bool:
        """Verificar si hay siguiente página."""
        from bs4 import BeautifulSoup
        
        soup = BeautifulSoup(html_content, 'html.parser')
        next_button = soup.select_one(self.selectors['next_page'])
        
        return next_button is not None and 'disabled' not in next_button.get('class', [])
    
    def _clean_text(self, text: str) -> str:
        """Limpieza específica para texto de Amazon."""
        if not text:
            return ""
        
        # Limpieza básica
        text = super()._clean_text(text)
        
        # Remover caracteres específicos de Amazon
        text = re.sub(r'\s+', ' ', text)  # Normalizar espacios
        text = text.replace('\u200e', '')  # Remover caracteres de dirección
        text = text.replace('\u200f', '')
        
        return text.strip()
    
    def _extract_price(self, price_text: str) -> Optional[float]:
        """Extracción específica de precios de Amazon."""
        if not price_text:
            return None
        
        try:
            # Limpiar texto de precio
            price_text = price_text.replace('$', '').replace(',', '').strip()
            
            # Buscar patrón de precio
            match = re.search(r'(\d+\.?\d*)', price_text)
            if match:
                return float(match.group(1))
            
            return None
            
        except (ValueError, AttributeError):
            return None
    
    def get_status(self) -> Dict[str, Any]:
        """Obtener estado específico del scraper de Amazon."""
        status = super().get_status()
        status.update({
            'amazon_specific': {
                'selectors_configured': len(self.selectors),
                'category_mapping': {
                    'electronics': 'electronics',
                    'books': 'books',
                    'home': 'home-garden'
                }
            }
        })
        return status 